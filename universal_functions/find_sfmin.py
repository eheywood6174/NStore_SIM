"""Finds a 'representative' value of over-supply that either:
(a) meets demand except for NSSm_opts['accp_umd'] (GWh), or
(b) meets demand with min. slack NSSm_opts['accp_slk'] at each hour,
depending on NSSm_opts['accp_crt'] = 0 or 1 respectively.
In both cases the function whose root is sought is C0 continuous and
monotonic. It is not C1 continuous at all points. For this reason, the
approach taken is to find a small set of (x,y) points close to the
solution and then to fit a cirve through those points to solve for the
root of that curve. In some cases the set comprises 4 points, in some it
comprises 2 points. In all cases, when a root is sought it lies within
the range of x coordinates used.

Arguments:
supply_ca: array of supply data
demand_ca: array of demand data
storz: array of energy store parameters
NSSm_opts: dict of program settings

Outputs:
supp_factor: minimum over-generation factor
del_fill: array of energy reduction for each store
x_arrN: array of over-generation factors trialled
y_arrN: array of corresponding y values
x_arrX: a larger (100-) array of values showing the polynomial
y_arrX: a larger (100-) array of values showing the polynomial
"""

import numpy as np
from find_sfmin0 import find_sfmin0
from find_sfmin1 import find_sfmin1

def find_sfmin(supply_ca, demand_ca, storz, NSSm_opts):
    #Decide which way to go: unmet demand (0) or minimum slack (1)
    if NSSm_opts['accp_crt']==0: #Use find_sfmin0
        [xbest, xspan, x_arr, y_arr, d_arr, x_arrN, y_arrN] = find_sfmin0(
            supply_ca, demand_ca, storz, NSSm_opts)
        print("<find_sfmin> has completed search type #0")
    else: #Use find_sfmin1
        [xbest, xspan, x_arr, y_arr, d_arr, x_arrN, y_arrN] = find_sfmin1(
            supply_ca, demand_ca, storz, NSSm_opts)
        print("<find_sfmin> has completed search type #1")
    
    #Use the value of xbest to determine if x is capped high or low
    if xbest>=NSSm_opts['sf_max']: #Over-generation factor is capped
        print(f'<find_sfmin>: over-genn. factor is capped at {xbest}')
        supp_factor = xbest #Set this value
        x_arrX = x_arr #Assign dummy value to x_arrX
        y_arrX = y_arr #Assign dumy value to y_arrX
        del_fill = storz[:,2]*storz[:,7] #Assign dummy value to del_fill
        return [supp_factor, del_fill, x_arrN, y_arrN, x_arrX, y_arrX]
    elif xbest<=NSSm_opts['sf_min']: #Over-generation factor is floored
        print(f'<find_sfmin>: over-genn. factor is capped at {xbest}')
        supp_factor = xbest #Set this value
        x_arrX = x_arr #Assign dummy value to x_arrX
        y_arrX = y_arr #Assign dummy value to y_arrX
        del_fill = storz[:,2]*storz[:,7] #Assign dummy value to del_fill
        return [supp_factor, del_fill, x_arrN, y_arrN, x_arrX, y_arrX]

    #Now fit a cubic polynomial (or line) to the supplied data points
    xmax = max(x_arr) #Find upper limit of x_arr
    xmin = min(x_arr) #Find lower limit of x_arr
    z_arr = 2*(x_arr-xmin)/(xmax-xmin) - 1 #Shift x-array to zero centre
    zbest = 2*(xbest-xmin)/(xmax-xmin) - 1 #Shift xbest accordingly
    if len(x_arr)==4: #Now go about fitting a cubic
        amat = np.array([z_arr**3, z_arr**2, z_arr, z_arr*0+1]) #Set up 'A' matrix
        coeffs = np.linalg.lstsq(amat, y_arr)[0] #Find coefficients for cubic
        ruuts = np.roots(coeffs) #Discover all roots
        irlrts = np.argwhere(ruuts.imag==0) #Which are the real roots?
        rl_ruuts = ruuts[irlrts] #These are the real roots
        iadmit = 1+2E-3 #Allow some roots slightly outside
        validrut = (rl_ruuts>-iadmit)*(rl_ruuts<iadmit) #Identify valid roots
        irlruuts1 = np.argwhere(validrut)
        rl_ruuts1 = rl_ruuts[irlruuts1][0] #Pick out valid real roots
        nrl_ruuts1 = len(rl_ruuts1) #How many good roots are there?
        if nrl_ruuts1<1:
            print("ERROR in <find_sfmin>: no good roots found")
            input("Break out here")
        else:
            dstiruut = np.abs(rl_ruuts1-zbest) #Find distances from zbest
            isrt = np.argsort(dstiruut) #Sort for minimum distance
            if len(isrt)==0:
                print("ERROR in <find_sfmin>: no good roots within fitted curve")
                input("Please break out here")
                zt = zbest #USe estimated best z value
                dstipts = np.abs(z_arr-zbest) #Find distances from zbest
                isrt = np.argsort(dstipts) #Sort for min. distance
                del_fill = 0.5*(d_arr[isrt[0]] + d_arr[isrt[1]]) #Simple average
            else: #This is a success for the cubic
                zt = rl_ruuts1[0][0].real #Pick out the good root
                #print(f'rl_ruuts1={rl_ruuts1}')

                #Compute del_fill - the reductions in fill level
                del_fill = np.matmul(np.array([zt**3, zt**2, zt, 1]), np.linalg.lstsq(amat, d_arr)[0]) #Interpolate all stores
                #Compute the corresponding supply factor (i.e. the root)
                supp_factor = xmin + (zt+1)*0.5*(xmax-xmin)
                #print(f'zt={zt}')
                #print(f'xmin={xmin}, xmax={xmax}')


                #The following outputs are for plotting; a very small overhead
                z_arrX = np.linspace(-1, 1, num=201)
                amatx = np.transpose(np.array([z_arrX**3, z_arrX**2, z_arrX, z_arrX*0+1]))
                y_arrX = np.matmul(amatx, coeffs)
                x_arrX = xmin + (z_arrX+1)*0.5*(xmax-xmin)
    
    else: #Dealing with a line, not a cubic
        amat = np.array([z_arr**1, z_arr**0]) #Set up 'A' matrix
        coeffs = np.linalg.lstsq(amat, y_arr)[0] #Find coefficients for line
        ruut = np.roots(coeffs) #Discover the single root
        iadmit = 1+2E-3 #Allow some roots slightly outside
        validrut = (ruut>-iadmit)*(ruut<iadmit) #Check validity
        if validrut==1: #This is success for the line
            zt = ruut[0]

            #Compute del_fill - the reductions in fill level
            del_fill = np.matmul(np.array([zt, 1]),np.linalg.lstsq(amat, d_arr)[0])
            #Compute the corresponding supply factor (i.e. the root)
            supp_factor = xmin + (zt+1)*0.5*(xmax-xmin)
            #print(f'zt={zt}')
            #print(f'xmin={xmin}, xmax={xmax}')

            #These outputs are for plotting; a very small overhead
            z_arrX = np.linspace(-1, 1, 201)
            amatx = np.array([(z_arrX), 
                              (z_arrX*0+1)])
            y_arrX = np.matmul(amatx.reshape((-1,2)), coeffs)
            x_arrX = xmin + (z_arrX+1)*0.5*(xmax-xmin)
        else:
            print("ERROR in <find_sfmin>: no good root for line within fitted data")
            input("Break out here")
    
    print(f'Found <supp_factor> = {supp_factor}')
    if supp_factor<NSSm_opts['sf_min'] or supp_factor>NSSm_opts['sf_max']:
        t = input(f'ERROR: supp_factor={supp_factor}, break out here.')
    return [supp_factor, del_fill, x_arrN, y_arrN, x_arrX, y_arrX]