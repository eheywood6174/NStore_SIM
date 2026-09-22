"""Examines a specific case to determine how much energy has been put into each store
and how much has been taken out.

Arguments:
supply_CA (ndarray): supply data
demand_CA (ndarray): demand data
storz (ndarray): store parameters
NSSm_opts (ndarray): program parameters

Outputs:
InE: total energy values input to each of N stores
OutE: total electrical energy values output from each of N stores
del_fill: reductions in fill levels (GWh) for each of N stores
xmat: fill states of stores
pmat: powers of each store
lmat: input losses for each store
dmat: self-discharge losses for each store
uvec: unmet demand values
cvec: curtailment values
svec: slack values
"""
import numpy as np
from NStore_sim import NStore_sim
from numba.typed import List

def energy_thru(supply_CA, demand_ca1, storz, NSSm_opts):
    #Convert NStore_sim inputs to enable Numba
    nssm_opts_arr = np.array([x for x in NSSm_opts.values()])
    demand_ca = List()
    [demand_ca.append(x) for x in demand_ca1]
    [xmat, pmat, lmat, dmat, uvec, cvec, svec] = NStore_sim(supply_CA, demand_ca, storz, nssm_opts_arr, idisp=1)

    #Determine input and output energies for each store
    nsto = len(storz) #How many stores?
    InE = np.zeros(nsto) #Initialise input energies array
    OutE = np.zeros(nsto) #Initialise output energies array
    for i in range(nsto): #Step through the stores
        pvec = pmat[:,i] #Extract power vector for store i
        ppos = pvec>0 #Flag when power is positive (input)
        pneg = pvec<0 #Flag when power is negative (output)
        InE[i] = sum(ppos*pvec) #Sum input energy packets
        OutE[i] = 0 - sum(pneg*pvec) #Sum output energy packets
    del_fill = storz[:,2]*storz[:,7] - xmat[-1,:]

    return [InE, OutE, del_fill, xmat, pmat, lmat, dmat, uvec, cvec, svec]