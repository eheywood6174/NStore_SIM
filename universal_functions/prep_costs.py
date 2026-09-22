"""
Arguments:
stocosts0: array of primary info on storage cap_ex and op_ex and deficit costs
supply: array of hourly information about supply profile
demand: array of hourly information about demand profile
re_costs: array of (cost-per-MWh) for each hour
dr_pc_pa: array of "net" discount rate as a percentage p.a.

Outputs:
cost_elems: dictionary containing relevant costing information for system costing
"""
import numpy as np
from condns_stocsts import condns_stocsts

def prep_costs(stocosts0, supply, demand, re_costs, dr_pc_pa):

    nhrs = len(supply) #How many hours of data are present?
    nhpa = 8766 #No. hours in the average year
    nyrs = np.round(nhrs/nhpa) #Number of years in the period
    dr_pc_ph = (1 + dr_pc_pa*0.01)**(1/nhpa) #Discount factor ( ()/hr )
    idxp5 = np.array(range(nhrs)) + 0.5 #Index vector for devaluation
    jdxp5 = idxp5*0 + 1 #A vector of ones
    devalutn = np.power(dr_pc_ph, idxp5) #Devaluation vector
    txx = (supply*re_costs)*1E3 #Temporary variable
    re_unit = np.sum(txx/devalutn) #Gen. costs of over-generation = 1.0
    totdmnd = sum(demand) #Total demand
    totsupp = sum(supply) #Total supply
    re_p_mwh = re_unit*1E-3/totdmnd #Average NPV of RE cost per MWh
    re_dvlf = sum(supply/devalutn)/totsupp #Mean devaln. factor (supply)
    dm_dvlf = sum(demand/devalutn)/totdmnd #Mean devaln. factor (demand)
    ge_dvlf = sum(jdxp5/devalutn)/nhrs #Mean devaln. factor (general)

    #Condense the storage cost info
    #Each store has values for CapEx, OpEx and life for each of 3 quantities
    stocosts1 = condns_stocsts(stocosts0, nyrs, dr_pc_pa)

    #Create a dictionary for costs
    costelems = {'stocosts':stocosts1, #All storage cost elements
                 're_unit':re_unit, #Cost for "1 unit" of genn.
                 're_dvlf':re_dvlf, #Mean devaln. factr (supply)
                 'dm_dvlf':dm_dvlf, #Mean devaln. factor (demand)
                 'ge_dvlf':ge_dvlf, #Mean devaln. factor (general)
                 'totsupp':totsupp, #Sum of all supply
                 'totdmnd':totdmnd,} #Sum of all demand
    
    return costelems