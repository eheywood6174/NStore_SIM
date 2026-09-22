"""This script allows for real-time monitoring of the cost optimisation function.
The script reads data from the most recently modified file in the 'outputs' folder
and plots system cost against evaluation number.
"""
import sys
from pathlib import Path
par = Path.cwd().parent
sys.path.insert(1, f'{par}/universal_functions')

import os
import numpy as np
import matplotlib.pyplot as plt
from import_settings import import_settings
from get_SD_data import get_SD_data
from make_DS_arrays import make_DS_arrays
from scale_CA import scale_CA
from params_2_storz import params_2_storz
from energy_thru import energy_thru
from calc_cost import calc_cost
from traj_plots import traj_plots

fnames = [] #Initialise filenames list

for (path, dirnames, filenames) in os.walk("outputs"):
    for name in filenames:
        fnames.append(os.path.join(path, name)) #Add all files in 'outputs' folder to the list

latest_file = max(fnames, key=os.path.getmtime) #Select the file that was most recently modified

with open(latest_file, "r") as f:
    data = f.readlines() #Extract data from file

#Identify corresponding base information file and extract data
time_string = data[0].strip().split()[0]
with open(f'outputs/{time_string}_base.txt', "r") as f:
    base_info = [line.strip() for line in f]

nsto = len(base_info) - 2 #How many stores in this case?
storz = np.zeros((nsto, 10)) #Initialise stores array
for i in range(nsto):
    storz[i] = np.array(np.float64(base_info[i].split())) #Populate stores array
NSSm_opts = {} #Initialise NSSm_opts dict
dict_pairs = base_info[nsto].split() #List of key:value pairs for NSSm_opts dict
for i in range(len(dict_pairs)):
    t = dict_pairs[i].split('=') #Split pair into key and value
    NSSm_opts.update({t[0]:np.float64(t[1])})
#NSSm_opts = np.array(np.float64(base_info[nsto].split())) #Populate NSSm_opts array
stocosts = np.zeros((nsto, 4)) #Initialise stocosts array
tstring = base_info[nsto+1].split('_') #Separate the last line into convenient parts
for i in range(nsto):
    #Select relevant stocost slice and remove unwanted characters
    t = tstring[i].replace('[', '')
    t = t.replace(']', '').split()
    #Populate relevant part of stocosts array
    stocosts[i,:] = np.float64(t)
[re_unit, re_dvlf, dm_dvlf, ge_dvlf, totsupp, totdmnd] = np.float64(tstring[nsto].split()) #Store remaning values from final line

#Create arrays for system cost, over-genn. factors, paramater vectors, eval. times and edcosts
data_t = np.array([line.strip().split() for line in data[1:]])
#costs = np.float64(data_t[:,0])
supp_factors = np.float64(data_t[:,1])
param_vecs = np.float64(np.array([line.split("_") for line in data_t[:,2]]))
del_fills = np.float64(np.array([line.split("_") for line in data_t[:,3]]))
eval_times = np.float64(data_t[:,4])
edcosts = np.float64(data_t[:,5])

cost_elems = {}
cost_elems['stocosts'] = stocosts #Cost elements for stores
cost_elems['re_unit'] = re_unit #NPV of one unit of normalised supply
cost_elems['re_dvlf'] = re_dvlf #Devaluation factor for RE
cost_elems['dm_dvlf'] = dm_dvlf #Devaluation factor for demand
cost_elems['ge_dvlf'] = ge_dvlf #General devaluation factor
cost_elems['totdmnd'] = totdmnd #Total energy consumed
cost_elems['totsupp'] = totsupp #Total supply

best_edcost = edcosts[-1]
#best_edcost = 80.5002969

costs = np.zeros(len(supp_factors))
for i in range(len(supp_factors)):
    storz_t = params_2_storz(storz, param_vecs[i])
    [cost, t1, t2] = calc_cost(storz_t, cost_elems, supp_factors[i], del_fills[i], best_edcost)
    costs[i] = cost

evno = len(costs) #How many evaluations so far?
ibstc = np.argmin(costs) #Which evaluation gave the best total cost?
best_cost = costs[ibstc] #How much did it cost?
print(f'Up to now there have been {evno} evaluations')
cost_per_mwh = best_cost*1E-3/(totdmnd*re_dvlf) #Calculate cost per MWh
print(f'Eval. #{ibstc+1} yielded NPV cost={best_cost/1E9:_.3f} (£bn) (={cost_per_mwh:_.3f} (£/MWh))')
supp_facx = supp_factors[ibstc] #Which over-genn. factor gave the best cost?
print(f'The over-generation factor found was {supp_facx:_.5f}')

#Plot system data and eval. time against evaluation number
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
ax1.plot(np.array(range(len(costs)))+1, np.float64(costs))
ax1.set_xlabel("Evaluation no.")
ax1.set_ylabel("System cost")
ax1.set_ylim(0, min(np.float64(costs))*3)
ax1.grid(True, ls='-')
ax2.plot(np.array(range(len(costs)))+1, np.float64(eval_times))
ax2.set_xlabel("Evaluation no.")
ax2.set_ylabel("Computation time")
ax2.grid(True, ls='-')
plt.show()

igo = 1
while igo==1:
    print("")
    t = input("Which evaluation would you like to inspect? ")
    try:
        ides = int(t) - 1
        assert ides>=0
        supp_facx = supp_factors[ides]
        igo = 0
    except:
        print(f"Invalid choice; up to now there have been {evno} evaluations")

#Extract desired parameter vector, supply factor and edcost
edcost = best_edcost
param_vec_x = param_vecs[ides]
nparm = len(param_vec_x)

#Examine energy throughputs for the desired case

#Obtain supply data and demand data
sd_data = get_SD_data()
supply_CA = make_DS_arrays(sd_data[0], storz[:, 9])
demand_CA = make_DS_arrays(sd_data[1], storz[:, 9])

supply_CA1 = scale_CA(supply_CA, supp_facx) #Scaled supply
storz_t = params_2_storz(storz, param_vec_x) #Set storage parameters
print("Executing NStore_SIM...")
[InE, OutE, del_fill_t, xmat, pmat, lmat, dmat, uvec, cvec, svec] = energy_thru(supply_CA1, demand_CA, storz_t, NSSm_opts)
for i in range(nsto):
    print(f'Store #{i+1}: Total energy (in/out)=({InE[i]/1E3:_.6f}, {OutE[i]/1E3:_.6f}) (TWh)')
    ratx = OutE[i]/InE[i]
    effx = storz_t[i,3]
    print(f'          Op/Ip ratio = {ratx:_.6f}, eta = {effx:_.6f}')
    dfcit = del_fills[ides][i]/1E3
    print(f'          Store deficit = {dfcit:_.6f} (TWh)')

#Now present the summary breakdown of costs

#Create cost_elems dict.
#cost_elems = {'stocosts':stocosts, #All storage cost elements
#                 're_unit':re_unit, #Cost for "1 unit" of genn.
#                 're_dvlf':re_dvlf, #Mean devaln. factr (supply)
#                 'dm_dvlf':dm_dvlf,
#                 'ge_dvlf':ge_dvlf,
#                 'totsupp':totsupp,
#                 'totdmnd':totdmnd} #Sum of all supply

[sys_cost, cost_p_mwh, sto_cost_mat] = calc_cost(storz_t, cost_elems, supp_facx, del_fills[ides], edcost, idisp=1)

print("Plot trajectories for this case? (0/1)")
iplot = input()

if iplot == "1":
    iok = traj_plots(xmat, pmat, lmat, dmat, uvec, cvec, svec)
