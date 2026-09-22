"""Expands the energy stores information array with additional information

Tne initial array contains:
    1. Rated Input Power (GW)
    2. Rated Ouput Power (GW)
    3. Store capacity (GWh)
    4. Round-trip efficiency (  ) N.B. not percentage!
    5. Self-discharge rate (/hr)
    6. Fraction of fill below which we elevate "marginal value" above 1: ( )
    7. Fraction of fill above which we reduce "marginal value" below 1:  ( )

This items added by this function comprise:
    8. Fraction of fill at start of simulation
    9. Relative priorities in filling/emptying for forecasts
    10. The down-sampling ratio applicable to each store

Arguments:
storz_o (list): list of arrays containing energy stores information
init_fill (list): fractions of fill at start of simulation for each store

Returns:
storz_x (ndarray): 2d array containing parameters for all stores
"""

def xpand_storz(storz_o:list, init_fill:list):
    import numpy as np

    tx_values = [] #Initialise variables for carrying between loops
    sum_tx = 0
    DS_ratios = []
    ist_list = []
    
    for i in range(len(storz_o)): #For each dictionary:
        pow_avrg = (storz_o[i][0]*storz_o[i][3] + storz_o[i][1])/2
        ist = storz_o[i][2]/pow_avrg #Calculate the indicative storage time
        ist_list.append(ist) #Save indiciative storage time for this store
        DS_ratio = round(ist/10, 0) #Choose the downsampling ratio
        if DS_ratio == 0: #Push any zeros up to 1
            DS_ratio += 1

        tx = 1/ist #A convenient temporary variable
        DS_ratios.append(DS_ratio) #Update carry-over variables
        tx_values.append(tx)
        sum_tx += tx

    storz_x = np.zeros((len(storz_o), 10)) #Initialise output array

    iordr = range(len(storz_o)) #Indicative storage times ###EDITED###: no longer reorders
    storz_t = storz_o #Reorder the store data
    init_fill_t = init_fill #Reorder the intial fill fractions
    DS_ratios_t = DS_ratios #Redorder down-sampling ratios

    for i in range(len(storz_o)):
        #Populate array with pre-existing info.
        storz_x[i][0:7] = storz_t[i]
        fst_prio = tx_values[i]/sum_tx #Normalise for affine combination
        #Add new info. to each array
        storz_x[i][7] = init_fill_t[i]
        storz_x[i][8] = fst_prio
        storz_x[i][9] = DS_ratios_t[i]

    return storz_x