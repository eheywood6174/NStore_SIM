"""Inverts the function y(x) = satd_exp(x, ymin, ymax)
z = log(ymin) + ((log(ymax)-log(ymin)/pi) * (atan(x) + (pi/2))
y = exp(z)

Inverting this progresses as follows (with q:=arctan(x))
z = log(y)
q = (log(y)-log(ymin))/(log(ymax)-log(ymin))
x = tan(q-(pi/2))
"""
import numpy as np
def inv_satd_exp(y, ymin, ymax):
    z = np.log(y)
    q = np.pi*(np.log(y)-np.log(ymin))/(np.log(ymax)-np.log(ymin))
    x = np.tan(q - np.pi/2)

    return x