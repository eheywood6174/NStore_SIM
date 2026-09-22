"""This function steps through time-series data for supply and demand
and operates energy stores in a "near-optimal way" so as to best
balance supply with demand. For the explanations below, one time-period
is referred to as one "hour".

Arguments:
supply_ca: list containing supply arrays (orig. + downsampled)
demand_ca: list containing demand arrays (orig. + downsampled)
storz: array of store parameters
NSSm_opts: array of function parameters

Outputs:
xmat: Array of fill levels of each of N stores. (1 row per hr).
pmat: Array of power into each of N stores.     (1 row per hr).
lmat: Array of input losses for each of N sto.s (1 row per hr).
dmat: Array of self-dischrg losses for N stores (1 row per hr).
uvec: Array of unmet demand.                    (1 entry per hr).
cvec: Array of constrained supply.              (1 entry per hr).
svec: Array of available "slack".               (1 entry per hr).
          ("Slack" indicates how much power headroom is left at each hr)
"""
import numpy as np
from numba import njit
from calc_powers import calc_powers
import sys

@njit
def NStore_sim(supply_ca, demand_ca, storz, NSSm_opts, idisp=0):

    nhrs = len(supply_ca[0]) #How many hours in time series
    nsto = len(storz) #How many store represented
    xvec = storz[:, 2]*storz[:, 7] #Initial fill levels
    efficiencies = storz[:,3]
    xmat = np.zeros((nhrs, nsto)) #Initialise array for fill levels
    pmat = np.zeros((nhrs, nsto)) #Initialise array for store powers
    lmat = np.zeros((nhrs, nsto)) #Initialise array for input losses
    dmat = np.zeros((nhrs, nsto)) #Initialise array self-discharge losses
    uvec = np.zeros(nhrs) #Initialise array for unmet demand
    cvec = np.zeros(nhrs) #Initialise array for curtailed P
    svec = np.zeros(nhrs) #Initialise array for "slack"
    op_powrz = storz[:, 1] #Array of max storage output powers
    sd_rates = storz[:, 4] #Array of self-discharge rates
    nchar = 0 #Initialise number of chars

    #Now run the large loop. This is the guts of NStore_SIM
    xvec_prev = xvec #Initialise xvec_prev

    for ihrs in range(nhrs): #Step through the hours
        pnet = supply_ca[0][ihrs] - demand_ca[0][ihrs] #Measure over-supply
        [powers, powers_xc] = calc_powers(supply_ca, demand_ca, ihrs, xvec, storz, NSSm_opts) #Calculate powers into stores
        pvec = powers + powers_xc #Total power vector (except self-discharge)
        sumpvc = sum(pvec) #Sum of powers going into storage

        #Calculate how much power could possibly come out from each store now
        slaks_sto = np.minimum(op_powrz, xvec) #Array of "slack" per store
        #Assess and record curtailed power or unmet demand
        if pnet > 0: #Curtailment is a possibility
            if sumpvc < pnet: #Curtailment happened!
                cvec[ihrs] = pnet - sumpvc
        else: #Unmet demand is a possibility
            if sumpvc > pnet: #Unmet demand happened!
                uvec[ihrs] = sumpvc - pnet
        tx = pnet + sum(slaks_sto) #Total slack available
        svec[ihrs] = max([tx, 0]) #Record slack (always non-negative)

        #Now assess input losses
        flags_pos = pvec > 0 #These stores are charging
        flags_neg = 1 - flags_pos #These stores are discharging
        lvec = pvec*flags_pos*(1-efficiencies) #The input losses
        delta_xvec = pvec*flags_pos*efficiencies + pvec*flags_neg
        xvec = xvec*(1-sd_rates) + delta_xvec #Update fill levels
        xmat[ihrs] = xvec #Store new fill levels
        pmat[ihrs] = pvec #Store the store power values
        lmat[ihrs] = lvec #Store input loss values
        dmat[ihrs] = xvec*sd_rates #Store self-discharge values
        #iok = check_xlims(ihrs, xvec, xvec_prev, storz, powers, powers_xc)
        xvec_prev = xvec #Update the "previous xvec"

        if idisp==1:
            if (ihrs+1)%NSSm_opts[2]==0:
                print(f'Executing NStore_SIM ({ihrs+1}/{nhrs})')

    if idisp==1:
        print(f'NStore_SIM complete! ({nhrs}/{nhrs})')

    return (xmat, pmat, lmat, dmat, uvec, cvec, svec)