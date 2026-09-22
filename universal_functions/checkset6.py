"""Determines whether a set of six (x,y) points correspond to a
polynomial of order three within an acceptable tolerance.
The assessment is based on whether the sum of squares of errors is
less than tol x the sum of squares of variations from the mean.

Arguments:
xset: x coords.
yset: y coords.
tol: acceptable tolerance

Outputs:
isgood: either 0 or 1 for rat>tol or rat<tol respectively
rat:
"""
import numpy as np

def checkset6(xset, yset, tol):
    #Verify number of points
    szx = len(xset)
    szy = len(yset)
    if (abs(szx-6) + abs(szy-6))>0:
        print("ERROR in <checkset6>: wrong size arrays supplied")
        print(f'len(xset)={szx}, len(yset)={szy}')
        input("Break out here:")
    
    #Define variations in x and y data and set ssref
    ymean = np.mean(yset)
    yvars = yset - ymean
    yvars = yvars.reshape(6,1)
    ssref = sum(yvars**2)
    if ssref==0: #Protect against case where all y values are equal
        rat = 1
        isgood = 1
        return [isgood, rat]
    xmean = np.mean(xset)
    xvars = (xset-xmean)/(max(xset)-min(xset)) #Non-dim'd x vals

    #Fit y values to the six points
    amat = np.transpose(np.array([xvars**0, xvars**1, xvars**2, xvars**3]))
    coeffs = np.linalg.lstsq(amat, yvars)[0]
    yrecon = np.matmul(amat, coeffs)
    yerrs = yvars - yrecon
    sserrs = sum(yerrs**2)

    #Now compare sserrs with ssref
    if sserrs>tol*ssref:
        isgood = 0
    else:
        isgood = 1
    
    rat = sserrs/ssref

    return [isgood, rat]