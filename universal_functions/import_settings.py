"""Stores desired settings from ASCII file into an array

Arguments:
filepath (str): filepath to settings file

Returns:
settings (ndarray): array containing settings
"""

def import_settings(filepath:str):

    import numpy as np

    with open(filepath) as file:
        lines = [float(line.split("=")[1].strip()) for line in file]

    settings = np.array(lines)

    return settings
