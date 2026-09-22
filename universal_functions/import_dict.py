"""Imports parameters fom a text file and stores them in a dict.
The input file must use one row per parameter, and be formatted as:
<key1> = <value1>
<key2> = <value2>
(etc.)

Arguments:
filepath (str): filepath to input file

Outputs:
settings (dict):
"""
import numpy as np

def import_dict(filepath):

    #Open input file and extract data
    with open(filepath, 'r') as fp:
        data = fp.readlines()

    #Remove comments from file
    data = [line.split('#')[0] for line in data]

    #Split data strings about '='
    data = [line.split('=') for line in data]
    
    #Separate data into keys and values, removing trailing characters
    keys = [line[0].strip() for line in data]
    values = [line[1].strip() for line in data]
    
    #Initialise output
    settings = {}

    #Populate output
    for i in range(len(values)):
        #try:
            #settings.update({keys[i]:int(values[i])}) #Store value as int if possible
        #except:
        settings.update({keys[i]:np.float64(values[i])}) #Else store value as float
    
    return settings