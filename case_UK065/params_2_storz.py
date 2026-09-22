"""Uses a set of parameters held in param_vec to overwrite entries in the storz
array to produce a new array, storz_t. This function is highly specific to the
case being solved.

Arguments:
storz (array): array of store parameters
param_vec (array): array of parameters used for overwriting
"""
import numpy as np
from satd_exp import satd_exp

def params_2_storz(storz, param_vec):

    storz_t = storz #Copy storz array

    #Overwrite variable entries in storz_t
    storz_t[0][0] = satd_exp(param_vec[0], 0.1, 50) #Input power 2
    storz_t[0][1] = satd_exp(param_vec[1], 0.1, 50) #Output power 2
    storz_t[0][2] = satd_exp(param_vec[2], 0.1, 4E3) #Storage capacity 2
    storz_t[1][0] = satd_exp(param_vec[3], 0.1, 100) #Input power 3
    storz_t[1][1] = satd_exp(param_vec[4], 0.1, 100) #Output power 3
    storz_t[1][2] = satd_exp(param_vec[5], 0.1, 50E3) #Storage capacity 3
    storz_t[2][0] = 0.0 #Input power 4
    storz_t[2][1] = satd_exp(param_vec[6], 0.1, 100) #Output power 4
    storz_t[2][2] = satd_exp(param_vec[7], 0.1, 500E3) #Storage capacity 4

    return storz_t