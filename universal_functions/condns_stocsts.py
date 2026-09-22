"""Condenses storage costs into four numbers per store. Each store is characterised by
three quantities (CapEx, OpEx as a % of CapEx, and asset lifetime (yrs)) for each of:
input power, output power, and storage capacity; the 10th value is the cost of each
MWh deficit in fill level between start and end of the period of n_year years.

The four output numbers per store in each row of the output array are the
equivalent NPVs of costs for the period of n_year years followed the costs (in year0
money) per MWh of deficit in fill.
"""
import numpy as np
from equiv_npv import equiv_npv

def condns_stocsts(stocosts0, n_year, drate_pc):

    nsto = len(stocosts0) #How many stores?
    npv_factor = equiv_npv(n_year, drate_pc) #Conversion of annual payment

    stocosts1 = np.zeros((nsto, 4))
    for isto in range(nsto):
        capex_ip_powr = stocosts0[isto][0] #CapEx ( /kW) for input power
        capex_op_powr = stocosts0[isto][1] #CapEx ( /kW) for output power
        capex_op_capc = stocosts0[isto][2] #CapEx ( /kWh) for output capacity
        opex_ip_powr = stocosts0[isto][3] #OpEx (%) for input power
        opex_op_powr = stocosts0[isto][4] #OpEx (%) for output power
        opex_op_capc = stocosts0[isto][5] #OpEx (%) for capacity
        life_ip_powr = stocosts0[isto][6] #Lifetime (yrs): input power
        life_op_powr = stocosts0[isto][7] #Lifetime (yrs): output power
        life_op_capc = stocosts0[isto][8] #Lifetime (yrs): capacity
        cost_e_deficit = stocosts0[isto][9] #Cost ( /MWh) for store deficit

        #Roll up CapEx and OpEx for input power into simple NPV ( /kW)
        tx = equiv_npv(life_ip_powr, drate_pc) #Intermediate variable
        ty = capex_ip_powr*(1+tx*opex_ip_powr/100) #Intermediate variable
        npv_ip_powr = ty * npv_factor/tx #Assign NPV value

        #Roll up CapEx and OpEx for output power into simple NPV ( /kW)
        tx = equiv_npv(life_op_powr, drate_pc) #Intermediate variable
        ty = capex_op_powr*(1+tx*opex_op_powr/100) #Intermediate variable
        npv_op_powr = ty * npv_factor/tx #Assign NPV value

        #Roll up CapEx and OpEx for storage capacity into simple NPV ( /kW)
        tx = equiv_npv(life_op_capc, drate_pc) #Intermediate variable
        ty = capex_op_capc*(1+tx*opex_op_capc/100) #Intermediate variable
        npv_op_capc = ty * npv_factor/tx #Assign NPV value

        #Install condensed costs into stocosts1
        stocosts1[isto] = [npv_ip_powr, npv_op_powr, npv_op_capc, cost_e_deficit]
    return stocosts1