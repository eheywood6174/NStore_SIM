"""Counts the number of out-of-bounds values of xvec
"""

def check_xlims(ihrs, xvec, xvec_prev, storz, powers, powers_xc):
    import numpy as np

    tol = 1E-12 #Use this to avoid catching rounding errors
    store_capacities = np.array([store[2] for store in storz]) #Extract relevant part of storz
    iok = sum(xvec<(0-store_capacities*tol)) + sum(xvec>(store_capacities*(1+tol)))

    if iok > 0:
        print(f"ERROR: Trapped an out-of-bounds xfill level at hr {ihrs}")
        exit(0)
    
    return