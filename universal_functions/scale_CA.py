"""Applies a scaling factor to all elements of an array.

Arguments:
orig_ca (list): list of down-sampled supply arrays
scal_fctr (float): scaling factor to apply to arrays

Outputs:
scaled_ca (list): list of scaled supply arrays
"""
import numpy as np
from numba.typed import List

def scale_CA(orig_ca, scal_fctr):

    scaled_ca = List() #Initialise output
    for array in orig_ca: #Loop through each array in the list
        scaled_array = array*scal_fctr #Copy the array and apply the scale factor
        scaled_ca.append(scaled_array) #Add scaled array to output
    
    return scaled_ca

