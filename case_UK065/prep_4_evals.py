"""This function does two things:
(1) It initialises an array of parameters for evaluation,
(2) It initialises a file updated each evaluation.
This function is specific to a particular case.
"""
import os
import numpy as np
import datetime
import time as tm
from inv_satd_exp import inv_satd_exp

def prep_4_evals(storz, edcost):
    #Initialise entries based on storz
    parm_vec_0 = np.array([inv_satd_exp(storz[0,0], 0.1, 50),
                           inv_satd_exp(storz[0,1], 0.1, 50),
                           inv_satd_exp(storz[0,2], 0.1, 4E3),
                           inv_satd_exp(storz[1,0], 0.1, 100),
                           inv_satd_exp(storz[1,1], 0.1, 100),
                           inv_satd_exp(storz[1,2], 0.1, 50E3),
                           inv_satd_exp(storz[2,1], 0.1, 100),
                           inv_satd_exp(storz[2,2], 0.1, 500E3)])
    

    if os.path.exists("outputs") == False: #Create outputs directory if it doesn't exist
        os.mkdir("outputs")
    
    time = datetime.datetime.now() #Record current time for output file name
    year = time.strftime("%y")
    month = time.strftime("%m")
    day = time.strftime("%d")
    hour = time.strftime("%H")
    minute = time.strftime("%M")
    second = time.strftime("%S")

    filepath = f"outputs/{year}_{month}_{day}__{hour}_{minute}_{second}"
    with open(f'{filepath}_data.txt', "x") as outputs_file:
        outputs_file.write(f'{year}_{month}_{day}__{hour}_{minute}_{second} {edcost}\n')
    

    return [parm_vec_0, filepath]