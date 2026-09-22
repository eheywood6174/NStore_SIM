import numpy as np

"""Checks and presents basic infomation about <Supply> and <Demand> arrays; scales <Supply> so that is has the same sum as <Demand>.

Arguments:
supply (ndarray): array containing the unscaled supply data
demand (ndarray): array containing the demand data

Returns:
(supply_scaled, nhrs, nyrs) (tuple): tuple (len=3) containing: 
    the scaled supply data (ndarray), 
    the number of hours this data covers (int),
    the number of years this data covers, rounded to the nearest year (int)
"""

def prob_intro(supply:np.ndarray, demand:np.ndarray):
    nhrs_S = len(supply)
    nhrs_D = len(demand)

    if abs(nhrs_S - nhrs_D) > 0:
        print("ERROR trapped in <prob_intro>")
        print(f"<Demand> contains {len(nhrs_D)} entries")
        print(f"<Supply> contains {len(nhrs_S)} entries")
        input("Press enter to break out:")

    nhrs = nhrs_S
    nyrs = round(nhrs/(365.25*24))
    nhrs_dscrp = nhrs - nyrs*365.25*24

    print(f"Time-series data for supply and demand has length {nhrs}")
    print(f"This equates to {nyrs} years (discrep. = {nhrs_dscrp} hrs)")

    if nhrs_dscrp > 24:
        print("Anomaly trapped in <prob_intro>")
        print("Record length not close to an integer*365.25*24")
        input("Press enter to break out:")

    sum_S = sum(supply)
    sum_D = sum(demand)

    print(f"The sum of entries in <Supply> = {sum_S:_.1f}")
    print(f"The sum of entries in <Demand> = {sum_D:_.1f}")

    supply_scaled = supply

    if abs(sum_S - sum_D) > 1E-6*(sum_S + sum_D):
        print("Scaling <Supply> so supply matches demand")
        supply_scaled = supply*sum_D/sum_S

    return (supply_scaled, nhrs, nyrs)