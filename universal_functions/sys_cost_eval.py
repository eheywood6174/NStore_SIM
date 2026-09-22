"""Determines the system cost depending on the independent entries in param_vec
and on other fixed quantities. Different versions of this function will apply
to different cases. This version is suitabale for an investigation of a three store
system operating with data used by CLS for the Royal Society report.

Arguments:
supply_ca (list): list containing arrays of original and down-sampled supply data
demand_ca (list): list containing arrays of original and down-sampled demand data
storz (ndarray): list containing arrays of store parameters
cost_elems (dict): dict. of all info. required to determine costs
param_vec (array): used to define power ratings and capacities of all stores (in this version, param_vec has nine entries)
NSSm_opts (array): simulation options
filepath (string): filepath to save outputs to
"""
import numpy as np
from params_2_storz import params_2_storz
from find_sfmin import find_sfmin
from calc_cost import calc_cost
import os
import time as tm
import random

def sys_cost_eval(param_vec, supply_ca, demand_ca, storz, cost_elems, NSSm_opts, filepath):

    #Extract currect <edcost> from outputs file
    with open(f'{filepath}_data.txt', "r") as fp:
        data = fp.readlines()
    
    t = data[-1].strip().split()
    edcost = np.float64(t[-1])

    #Copy storz array and replace entries using param_vec
    storz_t = params_2_storz(storz, param_vec)

    #Determine the minimum over-generation factor, supp_fctr
    #Note that this also finds del_fill and some diagnostic vectors
    tic = tm.perf_counter() #Start timer
    [supp_fctr, del_fill, x_arr, y_arr, x_arrx, y_arrx] = find_sfmin(supply_ca, demand_ca, storz_t, NSSm_opts)
    toc = tm.perf_counter() #Stop timer
    eval_time = toc - tic #Time taken to find scale factor

    #Determine overall system cost
    [sys_cost, cost_p_mwh, sto_cost_mat] = calc_cost(storz_t, cost_elems, supp_fctr, del_fill, edcost)
    
    #Prevent a case of capped supp_fctr from returning a good cost
    if supp_fctr >= NSSm_opts['sf_max']:
        sys_cost = max(NSSm_opts['bad_npv'], sys_cost)
    
    #Update the estimate of energy deficit cost (if downward)
    if cost_p_mwh < edcost:
        edcost_old = edcost #Record existing edcost
        tx = NSSm_opts['edcst_x'] #The update rate for edcost
        edcost = np.exp((1-tx)*np.log(edcost_old) + tx*np.log(cost_p_mwh))

    with open(f'{filepath}_data.txt', "a") as fp:
        fp.write(f'{sys_cost.real} {supp_fctr.real} {"_".join([str(x) for x in param_vec])} {"_".join([str(x) for x in del_fill])} {eval_time} {edcost}\n')
    
    print(f'Calculated <sys_cost> = {sys_cost/1E9:,.3f} (£bn)')

    return [sys_cost, supp_fctr, storz_t]