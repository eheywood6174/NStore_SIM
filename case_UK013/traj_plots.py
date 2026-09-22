"""Allows the user to make certain plots of the trajectories that have emerged.
"""

import numpy as np
import matplotlib.pyplot as plt

def traj_plots(xmat, pmat, lmat, dmat, uvec, cvec, svec):
    iwhich = 99
    nhrs = np.shape(xmat)[0]
    indx = np.array(range(nhrs))+1
    nsto = np.shape(xmat)[1]

    while iwhich > 0:
        print("Which plot to show? (Enter 0 to end)")
        for i in range(nsto):
            print(f'Enter {i+1} to see power and fill level plots for store {i+1}')
        print("Enter 1001 to plot total losses at storage inputs")
        print("Enter 1002 to plot total self-discharge losses")
        print("Enter 1003 to plot unmet demand")
        print("Enter 1004 to plot curtailed energy")
        print("Enter 1005 to plot slack at each hour")
        print("Please enter option here:")
        iwhich = int(input())
        if iwhich <= nsto:
            xvec = xmat[:,iwhich-1]
            pvec = pmat[:,iwhich-1]
            plt.ion()
            fig, (ax1, ax2) = plt.subplots(2,1, sharex=True)
            ax1.plot(indx, xvec)
            ax2.plot(indx, pvec)
            ax1.set_xlabel("Time (hrs)")
            ax2.set_xlabel("Time (hrs)")
            ax1.set_ylabel(f"Store {iwhich} level (GWh)")
            ax2.set_ylabel(f"Store {iwhich} power (GW)")
            ax1.grid(True, ls='-')
            ax2.grid(True, ls='-')
            plt.show()
        elif iwhich == 1001:
            lvec = np.sum(lmat,1)
            plt.ion()
            fig, (ax1, ax2) = plt.subplots(2,1,sharex=True)
            ax1.plot(indx, np.cumsum(lvec))
            ax2.plot(indx, lvec)
            ax1.set_xlabel("Time (hrs)")
            ax2.set_xlabel("Time (hrs)")
            ax1.set_ylabel(f"Cumulative input losses (GWh)")
            ax2.set_ylabel(f"Hourly loss rate (GW)")
            ax1.grid(True, ls='-')
            ax2.grid(True, ls='-')
            plt.show()
        elif iwhich == 1002:
            dvec = np.sum(dmat,1)
            plt.ion()
            fig, (ax1, ax2) = plt.subplots(2,1,sharex=True)
            ax1.plot(indx, np.cumsum(dvec))
            ax2.plot(indx, dvec)
            ax1.set_xlabel("Time (hrs)")
            ax2.set_xlabel("Time (hrs)")
            ax1.set_ylabel(f"Cumulative self-discharge losses (GWh)")
            ax2.set_ylabel(f"Hourly self-discharge loss rate (GW)")
            ax1.grid(True, ls='-')
            ax2.grid(True, ls='-')
            plt.show()
        elif iwhich == 1003:
            plt.ion()
            fig, (ax1, ax2) = plt.subplots(2,1,sharex=True)
            ax1.plot(indx, np.cumsum(uvec))
            ax2.plot(indx, uvec)
            ax1.set_xlabel("Time (hrs)")
            ax2.set_xlabel("Time (hrs)")
            ax1.set_ylabel(f"Cumulative unmet demand (GWh)")
            ax2.set_ylabel(f"Hourly unmet demand (GW)")
            ax1.grid(True, ls='-')
            ax2.grid(True, ls='-')
            plt.show()
        elif iwhich == 1004:
            plt.ion()
            fig, (ax1, ax2) = plt.subplots(2,1,sharex=True)
            ax1.plot(indx, np.cumsum(cvec))
            ax2.plot(indx, cvec)
            ax1.set_xlabel("Time (hrs)")
            ax2.set_xlabel("Time (hrs)")
            ax1.set_ylabel(f"Curtailed energy (GWh)")
            ax2.set_ylabel(f"Curtailed power (GW)")
            ax1.grid(True, ls='-')
            ax2.grid(True, ls='-')
            plt.show()
        elif iwhich == 1005:
            plt.ion()
            fig, ax = plt.subplots()
            ax.plot(indx, svec)
            ax.set_xlabel("Time (hrs)")
            ax.set_ylabel(f"Slack (GW)")
            ax.grid(True, ls='-')
            plt.show()
    iok = 1

    return iok