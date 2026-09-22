"""This is a "main program" for [NStore_sim]. 
This program calls up an optimisation action to find a (near-)optimal
combination of storage parameters to meet the requirements of a future 
Ireland energy system at minimal cost. 
The system considered here uses three types of storage/flexibility ... 
WIS + H2 + gas.
"""
#Insert the parent file into the module search tree
#This allows users to easily overwrite general functions for this case
#e.g., to overwrite NStore_sim for this case, save the new version as NStore_sim.py
#in the case folder
import sys
from pathlib import Path
par = Path.cwd().parent
sys.path.insert(1, f'{par}/universal_functions')

#Import relevant Python libraries
import numpy as np
import os
import scipy

#Import relevant NStore_SIM functions
from get_SD_data import get_SD_data
from import_settings import import_settings
from import_dict import import_dict
from xpand_storz import xpand_storz
from make_DS_arrays import make_DS_arrays
from prob_intro import prob_intro
from prep_costs import prep_costs
from prep_4_evals import prep_4_evals
from sys_cost_wrap import sys_cost_wrap

os.environ['NUMBA_FULL_TRACEBACKS'] = '0'

#Store supply/demand data in arrays
[supply_u, demand] = get_SD_data()
#Scale supply to match demand, if needed
[supply, nhrs, nyrs] = prob_intro(supply_u, demand)

#Load relevant store parameters from text files and store in array(s)
settings_h2 = import_settings("settings_h2.txt")
settings_gas = import_settings("settings_gas.txt")
settings_wis = import_settings("settings_wis.txt")
#The initial fill fractions for the stores
init_fill = [0.7, 0.7, 0.5]

#Group the store array(s) into a single 2D array with additional parameters
storz = xpand_storz([settings_wis, settings_h2, settings_gas], init_fill)

#Load simulation settings from text file and store in a dict
NSSm_opts = import_dict("NSSm_opts.txt")

#Create downsampled supply/demand arrays
supply_CA = make_DS_arrays(supply, storz[:,9])
demand_CA = make_DS_arrays(demand, storz[:,9])

#Create a dict of information for system costing
#N.B. the values below are case-specific
stocosts0 = np.array([[16.7, 16.7, 10.0, 3.0, 3.0, 2.0, 35, 35, 35, -1],
                      [333.0, 315.0, 0.727, 1.5, 1.5, 1.5, 30, 30, 30, -1],
                      [1.0, 1200.0, 0.0, 1.5, 1.5, 1.5, 25, 25, 100, 150]])
re_cost0 = 90.0
re_cost1 = 90.0
idxp5 = np.array(range(nhrs)) + 0.5
re_costs = re_cost0 + (re_cost1-re_cost0)*(idxp5/nhrs)
dr_pc_pa = 8.0
costelems = prep_costs(stocosts0, supply, demand, re_costs, dr_pc_pa)

#Create the initial parameter vector for optimisation
[param_vec, filepath] = prep_4_evals(storz, NSSm_opts['init_edcost'])

#Store the base problem information in the outputs folder
if os.path.exists("outputs") == False: #Create outputs directory if it doesn't exist
    os.mkdir("outputs")

stocosts = np.array(costelems['stocosts'])
ce_t = np.array(list(costelems.values())[1:])
keys = [key for key in NSSm_opts.keys()]
values = [value for value in NSSm_opts.values()]


with open(f'{filepath}_base.txt', 'x') as fp:
    for i in range(len(storz)):
        fp.write(f'{" ".join([str(x) for x in storz[i,:]])}\n')
    for i in range(len(NSSm_opts)):
        fp.write(f'{str(keys[i])}={str(values[i])} ')
    fp.write(f'\n{"_".join([str(x) for x in stocosts])}')
    fp.write(f'_{" ".join([str(x) for x in ce_t])}')

#Optimise system cost using a simplex algorithm
opt_param_vec = scipy.optimize.fmin(sys_cost_wrap, param_vec, args=(supply_CA, demand_CA, storz, costelems, NSSm_opts, filepath), 
                                    maxfun=int(NSSm_opts['num_Rstt']))
opt_param_vec = scipy.optimize.fmin(sys_cost_wrap, opt_param_vec, args=(supply_CA, demand_CA, storz, costelems, NSSm_opts, filepath), 
                                    maxfun=int(NSSm_opts['num_Rstt']))
opt_param_vec = scipy.optimize.fmin(sys_cost_wrap, opt_param_vec, args=(supply_CA, demand_CA, storz, costelems, NSSm_opts, filepath), 
                                    maxfun=int(NSSm_opts['num_Rstt']))
print(f'Found <opt_param_vec> = {opt_param_vec}')
print("Optimisation complete")