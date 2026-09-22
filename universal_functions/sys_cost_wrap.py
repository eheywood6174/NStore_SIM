"""This function acts as a wrapper for sys_cost_eval, and returns ONLY
the <sys_cost> variable; this is used with the scipy.optimise.fmin function
in the main program.

Arguments:
supply_ca (list): list containing arrays of original and down-sampled supply data
demand_ca (list): list containing arrays of original and down-sampled demand data
storz (ndarray): list containing arrays of store parameters
cost_elems (dict): dict. of all info. required to determine costs
param_vec (array): used to define power ratings and capacities of all stores (in this version, param_vec has nine entries)
NSSm_opts (array): simulation options
filepath (string): filepath to save outputs to

Returns:
sys_cost (float): overall system cost
"""

from sys_cost_eval import sys_cost_eval

def sys_cost_wrap(param_vec, supply_ca, demand_ca, storz, cost_elems, NSSm_opts, filepath):

    [sys_cost, supp_fctr, storz_t] = sys_cost_eval(param_vec, supply_ca, demand_ca, storz, cost_elems, NSSm_opts, filepath)

    return sys_cost