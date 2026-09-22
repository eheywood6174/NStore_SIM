"""Computes the NPV system cost as the sum of contributions for individual storage
costs and generation costs. Note that array storz has power/energy units of GW/GWh
respectively.

Arguments:
storz (ndarray): array containing store parameters
cost_elems (dict): dictionary containing relevant costing information
supp_fac (float): multiplier applied to normalised supply
del_fill (float): the reduction in fill levels for each store
edcost (float): current estimate of cost for net energy deficit in store
idisp (int): flag indicating whether printed output is required
"""
import numpy as np

def calc_cost(storz, cost_elems, supp_fac, del_fill, edcost, idisp=0):

    #Provide shortened names
    sto_costs = cost_elems['stocosts'] #Cost elements for stores
    re_unit = cost_elems['re_unit'] #NPV of one unit of normalised supply
    re_dvlf = cost_elems['re_dvlf'] #Devaluation factor for RE
    dm_dvlf = cost_elems['dm_dvlf'] #Devaluation factor for demand
    ge_dvlf = cost_elems['ge_dvlf'] #General devaluation factor
    totdmnd = cost_elems['totdmnd'] #Total energy consumed
    totsupp = cost_elems['totsupp'] #Total supply
    #Transfer relevant storz data to array
    stores = np.zeros((len(storz), 4)) #Initialise stores array
    for i in range(len(storz)):
        stores[i] = storz[i][0:4]
    #Calculate total costs
    sto_cost_mat = np.zeros((len(storz), 4)) #Initialise storage costs array
    sto_cost_mat[:, 0:3] = (stores[:,0:3]*sto_costs[:,0:3])*1E6 #Asset costs
    tx = sto_costs[:,3] #Deficit costs
    ty = tx<0 #Non-positive?
    tz = tx*(1-ty)*ge_dvlf + ty*edcost #£-per-MWh deficit
    sto_cost_mat[:,3] = (del_fill*tz)*1E3 #Deficit costs
    sys_cost = sum(sum(sto_cost_mat)) + re_unit*supp_fac #System cost
    cost_p_mwh = sys_cost/(1E3*totdmnd*dm_dvlf)

    if idisp==1:
        print("Storage cost components (NPV) listed here:")
        print(" |---------+-------------+----------------+------------|")
        print(" | Store # |  Element    |   Value        | Cost (£bn) |")
        print(" |---------+-------------+----------------+------------|")
        nsto = len(storz)
        for isto in range(nsto):
            #Output input power and asscociated costs
            print(f' |  {isto+1:5d}  | IP Power    | {storz[isto,0]:8.2f} (GW)  | {sto_cost_mat[isto,0]/1E9:8.2f}   |')
            #Output output power and asscociated costs
            print(f' |  {isto+1:5d}  | OP Power    | {storz[isto,1]:8.2f} (GW)  | {sto_cost_mat[isto,1]/1E9:8.2f}   |')
            #Output storage capacity and associated costs
            if storz[isto,2]>10E3: #Large enough to warrant TWh?
                print(f' |  {isto+1:5d}  | Energy Cap. | {storz[isto,2]/1E3:8.2f} (TWh) | {sto_cost_mat[isto,2]/1E9:8.2f}   |')
            else: #Use GWh
                print(f' |  {isto+1:5d}  | Energy Cap. | {storz[isto,2]:8.2f} (GWh) | {sto_cost_mat[isto,2]/1E9:8.2f}   |')
            #Output reduction in stored energy and associated costs
            if abs(del_fill[isto])>1E3: #Large enough to use TWh?
                print(f' |  {isto+1:5d}  | Enrgy Dfct. | {del_fill[isto]/1E3:8.2f} (TWh) | {sto_cost_mat[isto,3]/1E9:8.2f}   |')
            else: #Use GWh
                print(f' |  {isto+1:5d}  | Enrgy Dfct. | {del_fill[isto]:8.2f} (GWh) | {sto_cost_mat[isto,3]/1E9:8.2f}   |')
            print(" |---------+-------------+----------------+------------|")
        print("Generation costs now given:")
        print(" |-----------------------+----------------+------------|")
        print(" |    Element            |   Value        | Cost (£bn) |")
        print(" |-----------------------+----------------+------------|")
        print(f' | Genn. to meet demand  | {totdmnd/1E3:8.2f} (TWh) | {re_unit/1E9:8.2f}   |')
        tx = supp_fac-1
        print(f' | Losses & Curtailment  | {totdmnd*tx/1E3:8.2f} (TWh) | {re_unit*tx/1E9:8.2f}   |')
        print(" |-----------------------+----------------+------------|")
        print(f'\nTotal system NPV cost            = {sys_cost/1E9:8.3f} (£bn)')
        print(f'Equivalent constant cost per MWh = {cost_p_mwh:8.3f} (£/MWh)')

    return [sys_cost.real, cost_p_mwh.real, sto_cost_mat.real]
