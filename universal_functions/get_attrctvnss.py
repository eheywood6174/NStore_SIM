"""This function ascribes a central marginal value to the energy in
a store based on the fill-ratio, xt (which may be a vector).
Parameter vectors rtv and stv control how wide the central region is.

The function has zero slope and unity value for all of xt \in [rtv,stv]
For xt<rtv, value is given by (1+epsilo)/(epsilo+f(xt)) where f(xt) is a 
quadratic reaching 1 asymptotically at xt=rtv.
For xt>stv, there is a quadratic reaching 0 at xt=1 (starting tangentlly
to the line y=1).

Arguments:
xt (ndarray): array of fill ratios for stores
rtv (ndarray): parameter vector controlling central region
stv (ndarray): parameter vector controlling central region

Outputs:
values (ndarray):
"""
import numpy as np
from numba import njit

@njit
def get_attrctvnss(xti, rtv, stv, epsilo=1E-6):

    nsto = int(len(xti)) #How many stores?

    z_xt = xti*0 #A conveneient vector of zeros
    o_xt = xti*0 + 1 #A conveneient vector of ones
    xtj = np.maximum(xti, z_xt) #Force all xt values >=0
    xt = np.minimum(xtj, o_xt) #Force all xt values <=1

    f_xt = 1 - ((rtv-xt)/rtv)**2 #This is 0 at xt=0 and 1 at xt=rtv
    vec1 = ((1+epsilo)*o_xt)/(o_xt*epsilo + f_xt) #High at xt=0, 1 at xt=rtv
    g_xt = 1 - ((xt-stv)/(o_xt-stv))**2 #This is 1 at xt=stv and 0 at xt=1
    vec3 = g_xt*(1-epsilo) + epsilo #This is 1 at xt=stv and epsilo at xt=1
    flags1 = (xt<rtv) #Flag which are in first segment
    flags3 = (xt>stv) #Flag which are in last segment
    flags2 = o_xt - (flags1+flags3) #Flag which are in the centre
    #Assemble output
    vf1 = vec1*flags1
    vf2 = o_xt*flags2
    vf3 = vec3*flags3
    values = vf1 + vf2 + vf3

    return values