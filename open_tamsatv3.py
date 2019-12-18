# this code opens the tamsatv3 data

import netCDF4
import math
import matplotlib.pyplot as plt
import numpy as np


def open_tamsatv3_func():
    """
    This function opens the tamsatv3 data
    """

    nc = netCDF4.Dataset('/glusterfs/scenario/users/vr031288/TAMSATv3/rfe_1984_2016_filled_1.00.v3.nc')

    rainfall = nc.variables['rfe'][:]
    lon      = nc.variables['longitude'][:]
    lat      = nc.variables['latitude'][:]

    mask = np.nanmean(rainfall[:,:,:],axis=0)
    for i in np.arange(mask.shape[0]):
        for j in np.arange(mask.shape[1]):
            if math.isnan(mask[i,j]):
                mask[i,j]=0.0
            else:
                mask[i,j]=100.0

    return rainfall, lat, lon, mask, 1984

if __name__=='__main__':
    rainfall, lat, lon, mask, start = open_tamsatv3_func()

    plt.contourf(lon, lat, np.mean(rainfall, axis=0))
    plt.show()

    plt.contourf(lon, lat, mask)
    plt.show()
