"""This function calculates how much cross-charging should occur. This
function is always called after we have already calculated how to
operate the stores in order to address all system excess/shortfall. 
The power already committed for system excess/shortfall is in <powers>.
The set of fill levels (already updated to account for the changes that
occur due to accommodating the system excesses or shortfalls) is <xvec>

The marginal values for charging and discharging are held in arrays
<mrg_vals_c> and <mrg_vals_d> respectively and the priorities for 
charging and discharging are <prio_c> and <prio_d>.
The logic operates by setting pointers to the stores most eligible to
be charged and discharged. It steps along one pointer each time until
there is no longer any scope for cross-charging. Which pointer moves
depends on which store limited the power transfer ... charging side or
discharging side. 

At each step, we record the changes in powers committed for two different 
stores (one releasing and one receiving energy) and we also record the 
changes the energy levels that will be left in those two stores.

N.B. Cross-charging makes sense only when the power-ratings of the 
stores are a potential limit (which they must be in an optimal system).
Cross-charging loses energy - but it "keeps storage power in play".
Cross-charging only happens when at least one store is close to a border.

Arguments:
powers (ndarray):
xvec (ndarray):
storz (array):
mrg_vals_c (ndarray):
mrg_vals_d (ndarray):
prio_c (ndarray):
prio_d (ndarray):

Outputs:
powers_xc (ndarray):
"""
import numpy as np
from numba import njit

@njit
def calc_powrs_xc(powers, xvec, storz, mrg_vals_c, mrg_vals_d, prio_c, prio_d):

    idx_c = 0 #Initialise the pointer for the charging store
    idx_d = 0 #Initialise the pointer for the discharging preference
    jdx_c = prio_c[idx_c] #Identify the store most eligible for charging
    jdx_d = prio_d[idx_d] #Identify the store most eligible or discharging
    powers_xc = powers*0 #Initialise the output
    powerz = powers #Initialise the "powers already committed"
    xvcz = xvec #Initialise the "energy levels in stores"
    mrg_vals_ct = mrg_vals_c #Copy mrg_vals_c
    mrg_vals_dt = mrg_vals_d #Copy mrg_vals_d
    xbig = max(mrg_vals_ct)*2 #This marginal value would be BIG
    nsto = len(storz) #Determine number of stores

    #Now run the major while loop
    while mrg_vals_ct[jdx_c] > mrg_vals_dt[jdx_d]: #If this is true, cross-charge
        #Determine what limits the charging side
        hr_ec = (storz[jdx_c][2]-xvcz[jdx_c])/storz[jdx_c][3] #Energy "headroom"
        hr_pc = storz[jdx_c][0] - powerz[jdx_c] #Some P possibly already used
        pt_c = min([hr_ec, hr_pc]) #The limit for charging
        pt_c = max([pt_c, 0]) #Prevent negative limit

        #Determine what limits the discharging side
        hr_ed = xvcz[jdx_d] #Energy "headroom"
        hr_pd = storz[jdx_d][1] + powerz[jdx_d] #Some P possibly already used
        pt_d = min(hr_ed, hr_pd) #The limit for discharging
        pt_d = max(pt_d, 0) #Prevent negative limit

        #Decide whether charging or discharging presents the limit
        if pt_c < pt_d: #Charging side is the limit
            pt = pt_c #Set XC power to pt_c
            mrg_vals_ct[jdx_c] = 0 #This is no longer favourable for charging
            idx_c = min([idx_c + 1, nsto]) #Index along charging side
        else: #Discharging side is the limit
            pt = pt_d #Set XC power to pt_d
            mrg_vals_dt[jdx_d] = xbig #This is no longer favourable for discharging
            idx_d = min([idx_d + 1, nsto]) #Index along discharging side

        #Finally, make the adjustments
        xvcz[jdx_c] += pt*storz[jdx_c][3] #Increment charging energy
        xvcz[jdx_d] -= pt #Decrement discharging energy
        powerz[jdx_c] += pt #Increment charging power
        powerz[jdx_d] -= pt #Decrement discharging power
        powers_xc[jdx_c] += pt #Increment charging power
        powers_xc[jdx_d] -= pt #Decrement discharging power

        jdx_c = prio_c[idx_c] #Identify next most eligible (charging)
        jdx_d = prio_d[idx_d] #Identify next most eligible (discharging)
    
    return powers_xc