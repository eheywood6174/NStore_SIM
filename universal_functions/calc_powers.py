"""This function computes a column vector <powers> comprising <NSto> 
individual powers where <NSto> is the number of separate stores.
Positive values of power are charging the stores. 
Negative values of power are discharging the stores.
 
The "attractiveness" for any store is unity for all values of the
non-dimnensionalised fill level between <at> & <bt>.
Positive <Pnet> is when there is an excess of power (store charging).
Negative <Pnet> is when there is power shortfall (store discharging).

This function is an upgraded version of <calc_powers>. That took a very
quantised approach to allocating charging/discharging power while this
adopts a much smoother approach. It is expected to make optimisation 
much smoother.

Arguments:
supply_ca (list): list containing supply arrays (orig. + downsampled)
demand_ca (list): list containing demand arrays (orig. + downsampled)
ihrs (int): the hour currently being calculated
storz (array): array of store parameters
NSSm_opts (array): array containing settings
"""
import numpy as np
from numba import njit
from get_x_futr import get_x_futr
from get_attrctvnss import get_attrctvnss
from calc_powrs_c import calc_powrs_c1
from calc_powrs_d import calc_powrs_d1
from calc_powrs_xc import calc_powrs_xc

@njit
def calc_powers(supply_ca, demand_ca, ihr, xvec, storz, NSSm_opts):

    #How many hours?
    nhrs = len(supply_ca[0])

    #Initialise the outputs and fill-level adjustments
    powers = np.zeros(len(xvec))
    powers_xc = np.zeros(len(xvec))
    xvec_c = np.zeros(len(xvec))
    xvec_d = np.zeros(len(xvec))

    #Calculate the net power available now
    pnet = supply_ca[0][ihr] - demand_ca[0][ihr]

    #Unpack the relevant parts of storz
    nsto = len(storz) #How many stores are there?
    scvec = storz[:, 2] #The storage capacities
    effvec = storz[:, 3] #Array of round trip efficiencies for the stores
    rtevec = np.sqrt(effvec) #Array of sqaure roots of efficiencies
    dschrt = storz[:, 4] #Array of self-discharge rates for stores
    atvec = storz[:, 5] #Non-dim. fill levels below which mrg. value rises
    btvec = storz[:, 6] #Non-dim. fill levels above which mrg. value falls

    #Now adjust the present fill levels based on discharge level
    xvec_tmp = xvec*(1-dschrt) #Use this vector to determine <power>
    xvec_f = xvec_tmp #This is the default "future" vector

    #Now prepare the forward views of fill levels (only for priority levels for charging/discharging)
    fst_ds = NSSm_opts[1] #How many forward steps of downsampled data
    if fst_ds > 0: #Act only if some foresight is called for
        for i in range(nsto - 1): #Apply foresight to each store except the slowest
            ds_rat = storz[i][9] #The downsampling ratio for this store
            intvl = np.ceil(ihr/ds_rat - 1E-9) #Which downsampled interval are we in
            jntvl = ds_rat*intvl + 1 - (ihr+1) #How many hours left in this interval !!!POTENTIAL INDEX ERROR!!!
            kntvl = ds_rat - jntvl #How many hours at start of last
            vmult = np.ones(int(ds_rat+1))
            vmult[0] = jntvl/ds_rat
            vmult[-1] = kntvl/ds_rat
            #irng = range(intvl, intvl+ds_rat+1) #Range of relevant downsampled data
            supply_subr = supply_ca[i+1][intvl:intvl+ds_rat+1] #Down-sampled supply sub-range
            demand_subr = demand_ca[i+1][intvl:intvl+ds_rat+1] #Down-sampled demand sub-range
            power_subr = supply_subr - demand_subr #Down-sampled net power sub-range
            delta_e = ds_rat*(vmult*power_subr) #The energy delta
            xvec_f[i] = get_x_futr(xvec_tmp, storz, i, ds_rat, delta_e)
    
    ndfills = xvec_f/scvec #Non-dimensionalised fill levels
    attrctvnss = get_attrctvnss(ndfills, atvec, btvec) #Evaluate attractiveness

    if pnet > 0: #Stores are charging
        marg_vals_chg = attrctvnss*rtevec #Marginal values (charging)
        propns_chgng = marg_vals_chg**4 #Proportions for charging
        flags_replete = xvec_f>(storz[:,1]*(nhrs-ihr)) #Effectively full?
        propns_chgng = propns_chgng*(1-flags_replete) + 1E-3*flags_replete
        powers = calc_powrs_c1(pnet, xvec_tmp, storz, propns_chgng)
        xvec_c = powers*effvec #This is the xvec adjustment for charging
    elif pnet < 0: #Stores are discharging
        marg_vals_dchg = attrctvnss/rtevec #Marginal values (discharging)
        propns_dchgng = marg_vals_dchg**(-4) #Proportions for discharging
        powers = calc_powrs_d1(pnet, xvec_tmp, storz, propns_dchgng)
        xvec_d = powers #This is the xvec adjustment for discharging
    
    #Now consider whether any cross-charging should occur
    #if NSSm_opts[0] == 1: #Cross-charging is enabled
        #xvec_updtd = xvec_tmp + xvec_c + xvec_d #Update the fill levels
        #powers_xc = calc_powrs_xc(powers, xvec_updtd, storz, marg_vals_chg, marg_vals_dchg, prio_c, prio_d)
    
    return [powers, powers_xc]