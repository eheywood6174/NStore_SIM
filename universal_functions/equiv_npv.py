"""Calculates the NPV of unit spend paid at the end of each of nperio periods.

Arguments:
nperio: The number of periods
dscnt_rate_pc: The discount rate as a percentage, per period.

Outputs:
eq_NPV:
"""
import numpy as np

def equiv_npv(nperio, dscnt_rate_pc):

    xfac = 100/(100+dscnt_rate_pc) #Value reduces by this factor each period
    #Initialise quantities
    summn = 0.0
    valu = 1.0*xfac
    for i in range(int(nperio)): #Step through all periods
        summn += valu #Increment the NPV
        valu *= xfac #Reduce the value
    
    eq_NPV = summn

    return eq_NPV