"""This function distributes discharging duty among the various stores.
<calc_powrs_d1> is a development from <calc_powrs_d> which had a rather
discontinuous approach to allocating discharge power across stores with 
strict priority so that the most preferred store delivered as much as 
possible and then the next most preferred store would deliver as much as 
possible etc..  Here, by contrast, all stores always see some output
(unless they are empty or have zero rated output power).

This function works in stages. Often it completes after the first stage.
Subsequent stages are needed if one or more of the stores was limited
by having no energy left or by the rated output power. If this
happens, residual output power is spread across the remaining stores - 
if it can be. Sometimes, the output vector, <powers> will not sum to 
<Pnet> (if all of the stores have some limitations acting). Usually it 
will. 

Arguments:
pnet (float): power available now
xvec (ndarray): array containing the initial fill levels of the stores
storz (array): array of store parameters
propns_dchrgng (array): array of desired discharging proportions

Outputs:
powers (ndarray):
"""
import numpy as np
from numba import njit

@njit
def calc_powrs_d1(pnet, xvec, storz, propns_dchrgng):

    #Unpack vectors from storz
    sto_pwrs = storz[:,1] #Output powers

    #Prepare for the major 'while' loop
    powers = xvec*0 #Initialise output 
    xvect = xvec #Initialise vector of fill levels
    propns = propns_dchrgng #Initialise discharging proportions vector
    igo = 1 #Set loop condition to 'go'
    p_rem = 0 - pnet #Initialise outgoing power

    while igo==1:
        sumpropns = sum(propns) #Prepare for normalisation
        if sumpropns==0: #No more power can be distributed
            igo = 0
        else:
            igo = 0 #The first pass will usually finish this
            propns /= sumpropns #Normalise
            del_x_0 = p_rem*propns #Distribute the power
            del_x_lims = np.minimum(sto_pwrs-powers, xvect) #Lims on output power
            del_x_lims = np.maximum(del_x_lims, propns*0) #No negatives!
            del_x_1 = np.minimum(del_x_0, del_x_lims) #Actual achievable power
            del_x_xcss = del_x_0 - del_x_1 #Calculate excesses
            powers += del_x_1 #Accumulate power values
            xvect -= powers #Trim down fill levels
            if max(del_x_xcss) > 0: #There is power left to spread
                p_rem -= sum(del_x_1) #Adjust p_rem
                blox = np.nonzero(del_x_xcss>0) #Find elements that were limited
                propns[blox] *= 0 #Prohibit these stores from more
                igo = 1 #Continue loop
            else:
                p_rem = 0 #Redundant, helps reading
        
    powers = -1*powers #Final action before returning
    
    return powers