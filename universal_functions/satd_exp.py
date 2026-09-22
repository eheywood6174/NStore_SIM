"""Computes a function y(x) with the following properties:
y(x) > ymin for all x
y(x) < ymax for all x
y(x) is monotonic

It is necessary that ymax > ymin > 0
"""
import numpy as np
def satd_exp(x, ymin, ymax):
    if ymin<=0:
        print(f'ERROR in <satd_exp>: ymin={ymin}')
        input("Break out here")
    elif ymax<=ymin:
        print(f'ERROR in <satd_exp>: ymax (={ymax}) < ymin (={ymin})')
        input("Break out here")
    
    #Find the limits
    lymin = np.log(ymin)
    lymax = np.log(ymax)

    z = lymin + ((lymax-lymin)/np.pi)*(np.arctan(x) + np.pi/2)

    y = np.exp(z)

    return y