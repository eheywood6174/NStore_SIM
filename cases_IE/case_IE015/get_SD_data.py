"""Local overwrite of a global function.
Imports supply/demand data from a text file and scales
supply accordingly.
"""
import numpy as np
def get_SD_data():
    #Load data from text file
    with open("data.dat", 'r') as fp:
        data = fp.readlines()
    
    n = len(data)

    #Initialise arrays
    demand = np.zeros(n)
    supply = np.zeros(n)

    #Separate each line into columns:
    #Demand, Supply
    for i in range(n):
        t = data[i].strip().split()
        demand[i] = np.float64(t[1])
        supply[i] = np.float64(t[0])

    #Scale supply to demand
    supply_u = supply*sum(demand)/sum(supply)

    return [supply_u, demand]