"""Apportions a fraction of energy <delta_e> to store #isto. The existing fill level
of this store is found in <xvec>. The parameters of the stores are held in <storz>.
Recall that input energy is multipled by efficiency to cause the
difference in the energy content of any one store. 
The store has two constraints. For charging, those are determined by the
unfilled capacity (divided by efficiency) and the input power rating. 
For discharging, those are determined by the amount of energy in store
and by the output power rating. If the constraints are hit, then the
energy that was to have been put in (or taken out) would be distributed
proportionately over the other stores but that does not matter here.
The purpose of this forecasting is simply to set priorities on which 
stores should fill or empty first. We are focused on store #iSto.

Arguments:
xvec (nd_array): array containing the initial fill levels of the stores
storz (array): array of parameters for each store
isto (int): the index of the current store
ds_rat (float): the down-sampling ratio for the current store
delta_e (float): the fraction of energy being apportioned to the current store

Outputs:
x_i (float): updated fill value for the current store
"""
import numpy as np
from numba import njit

@njit
def get_x_futr(xvec, storz, isto, ds_rat, delta_e):

    x_i = xvec[isto] #Initialise output
    tt = storz[isto][8]/sum(storz[isto:,8]) #What fraction to allocate

    if delta_e > 0: #Distribute positive energy differential
        #Calculate the limits on how much energy could be put into #isto
        tx = ds_rat*storz[isto][0] #The limit on energy from input power
        ty = (storz[isto][2] - x_i)/storz[isto][3] #Energy limit on input energy
        tz = min(delta_e*tt) #How much we might seek to put in
        tw = min([tx, ty, tz]) #This is the controlling amount
        x_i += tw*storz[isto][3] #Update x_i
    else: #Distribute the negative energy differential
        #Calculate the limits on how much energy could be taken from #isto
        tx = ds_rat*storz[isto][1] #The limit on output energy from power
        ty = x_i #Limit on output energy based on energy
        tz = min(0 - delta_e*tt) #How much we might seek to take out
        tw = min([tx, ty, tz]) #This is the controlling amount
        x_i -= tw #Update x_i

    return x_i