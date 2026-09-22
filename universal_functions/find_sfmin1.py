"""This function is a slave to <find_sfmin> which seeks to find the minimum
value of supply factor that will lead to an acceptable system. Supply factors
are invariably in the order of 1 - most typically in [1.1, 1.4].

This generates x-y data where x values represent supply factors for which the
minimum slack at any one hour interval is very close to the border between
acceptable and unacceptable. The y values represent the measure of acceptability
(negative bad, positive good).

Short x and y data are stored in <x_arr4> and <y_arr4> repsectively. Short data
usually comprises four (x,y) points (for cubic fitting), but will sometimes be
just a pair of points (for linear interpolation) - the latter is used when the
maximum number of interval halvings has been exceeded.

Full x and y data are stored in <x_arrN> and <y_arrN> respectively; these comprise
all (x,y) points found.

For each x values there are also NSto values reflecting store depletion levels (one
for each store) between period start and end. These data are held in <d_arr4> (one
row for each (x,y) pair). The same interpolation law used to find the root is also
used to approximate the fill levels.

<xbest> is an estimate of the crossing point based on linear interpolation.
<xspan> is the breadth of uncertainty (between extremes).

Throughout the function it is assumed that function y(x) is monotonic.
For values of x below the root, y is negative.
For values of x above the root, y is positive.
Function y(x) saturates at the negative extreme.

Note: each (x,y) pair calculated costs significant time. This function is designed
to be able to achieve a high level of quality with a minimum number of function
evaluations. For it to be effective, set values within NSSm_opts.txt very carefully.

Arguments:
supply_ca: array of supply data (different downsampling ratios)
demand_ca: array of demand data (different downsampling ratios)
storz: array of store parameters
NSSm_opts: dict of program options

Outputs:
[xbest, xspan, x_arr4, y_arr4, d_arr4, x_arrN, y_arrN]
"""

import numpy as np
from scale_CA import scale_CA
from NStore_sim import NStore_sim
from checkset6 import checkset6
from numba.typed import List

def find_sfmin1(supply_ca, demand_ca1, storz, NSSm_opts):

    #Initialise arrys for x-y data
    nsto = int(len(storz)) #How many stores?
    x_arr = np.ones(50)*-1 #Array of over-genn. factors (oversized)
    y_arr = np.zeros(50) #Array of (un)acceptability values (oversized)
    d_arr = np.zeros([50,nsto]) #Array for store fill deficits (oversized)

    #Initialise some variables, give shortened names to others
    idx = 0 #Indicate no data is 'in' yet
    sf_est = NSSm_opts['sf_est'] #Estimated root
    sf_scl = NSSm_opts['sf_scl'] #Scaling factor
    min_IHIt = NSSm_opts['N_IHIt'] #Min. bisection halvings
    max_IHIt = NSSm_opts['M_IHIt'] #Max. bisection halvings
    cubi_tol = NSSm_opts['cubi_tol'] #Tolerance of cubic fit

    #Convert NStore_sim args to enable use of Numba
    nssm_opts_arr = np.array([x for x in NSSm_opts.values()])
    demand_ca = List()
    [demand_ca.append(x) for x in demand_ca1]

    #Evaluate (x,y) at supplied scaling and grab 'first point'
    supply_fctr = sf_est #Search starts here
    supply_ca1 = scale_CA(supply_ca, supply_fctr) #Scale up supply
    [xmat, pmat, lmat, dmat, uvec, cvec, svec] = NStore_sim(
        supply_ca1, demand_ca, storz, nssm_opts_arr)
    ttt = min(svec) - NSSm_opts['accp_slk'] #This is acceptability
    ddd = storz[:,2]*storz[:,7] - xmat[-1,:] #Depletion levels
    x_arr[idx] = supply_fctr #Store one supply factor
    y_arr[idx] = ttt #Store corresponding (un)acceptability
    d_arr[idx,:] = ddd #Store corresponding fill deficits
    print(f'<find_sfmin1>: Pt #{idx}: ({x_arr[idx]}, {y_arr[idx]})') #Report first point
    idx += 1 #Increment the count

    #Decide whether first point was acceptable, unacceptable, or spot on!
    if ttt>0: #First point was acceptable
        isign = -1 #We are looking for a negative (unacceptable)
        scalx = 1/sf_scl #Set scaling for decreasing
    elif ttt<0: #First point was unacceptable
        isign = 1 #We are looking for a positive (acceptable)
        scalx = sf_scl #Set scaling for increasing
    else: #First point is spot on (unlikely, but possible)
        xbest = supply_fctr #Set xbest to initial guess
        xspan = 0.0 #Set span to zero
        x_arr4 = np.array([-0.1, 0.1]) + x_arr[0] #Array of x coords. has 2 entries
        y_arr4 = np.array([1, 1])*y_arr[0] #Array of y coords. has 2 entries
        d_arr4 = np.array([1, 1])*d_arr[0,:] #<d_arr4> has 2 identical rows
        x_arrN = x_arr[0] #Full x array has only 1 entry
        y_arrN = y_arr[0] #Full y array has only 1 entry
        return [xbest, xspan, x_arr4, y_arr4, d_arr4, x_arrN, y_arrN]
    
    #Now find the next point on the opposite side of (un)acceptable
    igo = 1 #Set while-loop flag to 'go'
    while igo==1:
        supply_fctr *= scalx #Increment supply factor
        supply_ca1 = scale_CA(supply_ca, supply_fctr) #Scale up supply
        [xmat, pmat, lmat, dmat, uvec, cvec, svec] = NStore_sim(
            supply_ca1, demand_ca, storz, nssm_opts_arr)
        ttt = min(svec) - NSSm_opts['accp_slk'] #This is acceptability
        ddd = storz[:,2]*storz[:,7] - xmat[-1,:] #Depletion levels
        x_arr[idx] = supply_fctr #Record point (x)
        y_arr[idx] = ttt #Record point (y)
        d_arr[idx,:] = ddd #Store corresponding fill deficits
        print(f'<find_sfmin1>: Pt #{idx}: ({x_arr[idx]}, {y_arr[idx]})') #Report discovered point
        idx += 1 #Increment the count
        if ttt*isign>=0: #We have bracketed a root
            igo=0 #Signal end of while loop
            print("Root now bracketed") #Report that root is bracketed
        else: #We are not yet satisfied
            if isign>0:
                print("Still seeking up")
            else:
                print("Still seeking down")
        #Check whether the search has gone outside the acceptable range
        if supply_fctr>=NSSm_opts['sf_max']:
            print("<find_sfmin1>: Supply factor too high")
            xbest = NSSm_opts['sf_max'] #Set xbest equal to max value
            xspan = 0.0 #Set span to 0
            x_arr4 = np.array([-0.1, 0.1]) + xbest #Provide dummy version of array
            y_arr4 = np.array([1, 1])*ttt #Provide dummy version of array
            d_arr4 = np.ones([2, nsto])*ddd #Provide dummy version of array
            x_arrN = x_arr[0:idx] #Provide dummy version of array
            y_arrN = y_arr[0:idx] #Provide dummy version of array
            return [xbest, xspan, x_arr4, y_arr4, d_arr4, x_arrN, y_arrN]
        elif supply_fctr<=NSSm_opts['sf_min']:
            print("<find_sfmin1>: Supply factor too low")
            xbest = NSSm_opts['sf_min'] #Set xbest equal to max value
            xspan = 0.0 #Set span to 0
            x_arr4 = np.array([-0.1, 0.1]) + xbest #Provide dummy version of array
            y_arr4 = np.array([1, 1])*ttt #Provide dummy version of array
            d_arr4 = np.ones([2, nsto])*ddd #Provide dummy version of array
            x_arrN = x_arr[0:idx] #Provide dummy version of array
            y_arrN = y_arr[0:idx] #Provide dummy version of array
            return [xbest, xspan, x_arr4, y_arr4, d_arr4, x_arrN, y_arrN]
    
    #Interval bisection will now take place
    #Set points (xa, ya) and (xc, yc)such that ya<0 and yc>0
    if isign>0: #We were seeking up
        xa = x_arr[idx-2]
        ya = y_arr[idx-2]
        dfilla = d_arr[idx-2,:]
        xc = x_arr[idx-1]
        yc = y_arr[idx-1]
        dfillc = d_arr[idx-1,:]
    else: #We were seeking down
        xa = x_arr[idx-1]
        ya = y_arr[idx-1]
        dfilla = d_arr[idx-1,:]
        xc = x_arr[idx-2]
        yc = y_arr[idx-2]
        dfillc = d_arr[idx-2,:]
    
    #Now run a number of iterations of interval bisection:
    #A positive reason to stop must satisfy three conditions -
    #1: The minimum number of iterations have been completed
    #2: There are >0 non-saturated points below the root
    #3: The 6 closest points to the root fit a cubic within tolerance
    #A negative reason to stop is that we have exceeded the max. iteration count
    igo = 1 #Set while-loop flag to "go"
    iter = 0 #Initialise iteration count
    while igo==1:
        iter += 1 #Increment iteration count
        xb = (xa+xc)/2 #Bisect the interval
        supply_ca1 = scale_CA(supply_ca, xb) #Scale up supply
        [xmat, pmat, lmat, dmat, uvec, cvec, svec] = NStore_sim(
            supply_ca1, demand_ca, storz, nssm_opts_arr)
        ttt = min(svec) - NSSm_opts['accp_slk'] #This is acceptability
        ddd = storz[:,2]*storz[:,7] - xmat[-1,:] #Fill deficits
        x_arr[idx] = xb #Record point (x)
        y_arr[idx] = ttt #Record point (y)
        d_arr[idx,:] = ddd #Store corresponding fill deficits
        print(f'<find_sfmin1>: Pt #{idx} ({x_arr[idx]}, {y_arr[idx]})')
        idx += 1 #Increment the count
        yb = ttt #Now decide which end to 'pull in'
        if yb<0: #Pull in LHS
            xa = xb
            ya = yb
            dfilla = ddd
        else: #Pull in RHS
            xc = xb
            yc = yb
            dfillc = ddd
        
        #Apply linear interpolation to make best estimate of root
        xbest = xa + (xc-xa)*((0-ya)/(yc-ya)) #Best current guess of root

        #Examine whether to stop interval bisection (positive)
        if iter>=min_IHIt: #We may be eligible to stop
            #Check for 2+ good points below the root
            flgs1 = y_arr>(0-NSSm_opts['accp_slk']) #Non-saturated actual data
            flgs2 = y_arr<0 #Points with x coords. below xbest
            flgs3 = x_arr>0 #Points with x coords. > 0
            flags = flgs1*flgs2*flgs3 #Good points below the root
            num_below = sum(flags) #Count good points below the root
            if num_below>0: #We have >0 good points below the root
                dists = np.abs(x_arr-xbest) #True distances from the root
                dists += 100*(1-flgs1) #Paint sat'd points as 'far away'
                dists += 1000*(1-flgs3) #Paint unused x_arr entries as 'far away'
                isort = np.argsort(dists) #Sort by distance
                iset6 = isort[0:6] #Select 6 good points closest to root
                xset6 = x_arr[iset6] #Assemble x coords.
                yset6 = y_arr[iset6] #Assemble y coords.
                [isgood, rat] = checkset6(xset6, yset6, cubi_tol)
                if isgood==1:
                    igo = 0 #Signal end of while-loop
        #Now examine whether to stop interval bisection (negative)
        if iter>=max_IHIt: #Too many iterations, we must stop
            print(f'Number of iterations reached maximum ({iter})')
            xspan = 0.0 #Set span to zero
            #Find closest point below the root
            indxA = np.argwhere(y_arr<0) #Points with negative y coords.
            ii = np.argmax(x_arr[indxA]) #Largest (true) x-coord. < root
            x_arrt = x_arr[indxA]
            xA = x_arrt[ii]
            y_arrt = y_arr[indxA]
            yA = y_arrt[ii] #Corresponding y coord.
            #Find closest point above the root
            indxB = np.argwhere(y_arr>0) #Points with positive y coords.
            ii = np.argmin(x_arr[indxB]) #Smallest (true) x-coord. > root
            x_arrt = x_arr[indxB]
            xB = x_arrt[ii]
            y_arrt = y_arr[indxB]
            yB = y_arrt[ii] #Corresponding y coord
            #Assemble output quantities
            x_arr4 = np.array([xA[0], xB[0]]) #Two coords. only
            y_arr4 = np.array([yA[0], yB[0]]) #Two coords. only
            d_arr4 = np.array([dfilla, dfillc]) #Two rows only
            x_arrN = x_arr[0:idx] #Extract array of good x coords.
            y_arrN = y_arr[0:idx] #Extract array of good y coords.
            return [xbest, xspan, x_arr4, y_arr4, d_arr4, x_arrN, y_arrN]
    x_arrN = x_arr[0:idx] #Set the long array of export points (x)
    y_arrN = y_arr[0:idx] #Set the long array of export points (y)

    #Calculate span of uncertainty
    xspan = xc-xa

    #Select a subset of 4 points to return
    dists = np.abs(x_arr-xbest) #True distances from root
    dists += 100*(1-flgs1) #Paint saturated points as 'far away'
    dists += 1000*(1-flgs3) #Paint unused entries as 'far away'
    jsort = np.argsort(dists) #Sort by distance
    iset4 = jsort[0:4] #Select 4 good points closest to root
    xset4 = x_arr[iset4] #Assemble x coords.
    yset4 = y_arr[iset4] #Assemble y coords.
    dset4 = d_arr[iset4,:] #Pick out store depletion levels

    #Finally, order the arrays by x coordinate
    ksort = np.argsort(xset4)
    x_arr4 = xset4[ksort]
    if sum(x_arr4<0)>0:
        input("ERROR: Break out here")
    y_arr4 = yset4[ksort]
    d_arr4 = dset4[ksort]

    return [xbest, xspan, x_arr4, y_arr4, d_arr4, x_arrN, y_arrN]