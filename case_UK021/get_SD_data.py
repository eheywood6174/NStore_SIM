"""Local overwrite of a global function.
Imports supply/demand data from a text file and scales
supply accordingly.
"""
import numpy as np
def get_SD_data():
    #Load data from text file
    with open("Data0File.dat", 'r') as fp:
        data = fp.readlines()
    
    n = len(data)

    #Initialise arrays
    demand = np.zeros(n)
    offshrwnd = np.zeros(n)
    onshrwnd = np.zeros(n)
    solar = np.zeros(n)

    #Separate each line into columns:
    #Demand, Offshore Wind, Onshort Wind, Solar
    for i in range(n):
        t = data[i].strip().split()
        demand[i] = np.float64(t[0])
        offshrwnd[i] = np.float64(t[1])
        onshrwnd[i] = np.float64(t[2])
        solar[i] = np.float64(t[3])
    
    #Plan for a steady 9.5GW of nuclear power
    demand -= 9.5

    #Create supply array from relevant columns
    supply = 0.8*(0.7*offshrwnd + 0.3*onshrwnd) + 0.2*solar

    #Scale supply to demand
    supply_u = supply*sum(demand)/sum(supply)

    return [supply_u, demand]