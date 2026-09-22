"""This function distributes charging duty among the various stores.
<calc_powers_c1> is a development from <calc_powers_c>, which had a rather
discontinuous approach to allocating powers across stores with strict priority
so that the most preferred store took as much as possible, then the next most
preferred store would take as much as possible, etc...
Here, by contrast, all stores always see some input.
Normally, sum(powers) is identical to Pnet but it may be less if
every one of the stores has hit a limit on how much power it can accept.

This function worlks in stages. Often it completes after the first stage.
Subsequent stages are needed if one or more of the stores was limited by
either its max capacity or by the rated input power. If this happens,
residual pwoer is spread across the remaining stores if possible.

Arguments:
pnet (float): power available now
xvec (ndarray): array containing the initial fill levels of the stores
storz (array): array of store parameters
propns_chrgng (array): array of desired charging proportions

Outputs:
powers (ndarray):
"""
import numpy as np
from numba import njit

@njit
def calc_powrs_c1(pnet, xvec, storz, propns_chrgng):

    #Unpack some vectors from storz
    sto_pwrs = storz[:,0] #Input powers
    sto_caps = storz[:,2] #Storage capacities
    sto_effs = storz[:,3] #Round-trip efficiencies

    #Prepare for the major 'while' loop
    powers = xvec*0 #Initialise output
    xvect = xvec #Initialise vector of fill levels
    propns = propns_chrgng #Initialise charging proportions vector
    igo = 1 #Set loop condition to 'go'
    p_rem = pnet #Initialise remaining power

    while igo==1:
        sumpropns = sum(propns) #Prepare for normalisation
        if sumpropns==0: #No more can be distributed
            igo = 0
        else:
            igo = 0 #The first pass will usually finish this
            propns /= sumpropns #Normalise
            del_x_0 = p_rem*propns #Distribute power
            del_x_lims = np.minimum((sto_pwrs-powers), ((sto_caps-xvect)/sto_effs)) #Lims
            del_x_lims = np.maximum(del_x_lims, propns*0) #No negatives!
            del_x_1 = np.minimum(del_x_0, del_x_lims) #Actual achievable power
            del_x_xcss = del_x_0 - del_x_1 #Calculate excesses
            powers += del_x_1 #Accumulate power values
            xvect += powers*sto_effs #Adjust up the fill levels
            if max(del_x_xcss) > 0: #There is power remaining
                p_rem -= sum(del_x_1) #Adjust p_rem
                blox = np.nonzero(del_x_xcss>0) #Find elements that were limited
                propns[blox] *= 0 #Prohibit these stores from receiving more
                igo = 1 #Continue loop
            else:
                p_rem = 0 #Redundant, helps reading

    return powers