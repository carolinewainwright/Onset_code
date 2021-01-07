# This code opens the TAMSATv3 rainfall data
# the path name should be changed to the relevant file


import netCDF4
import math
import matplotlib.pyplot as plt
import numpy as np


def open_tamsatv3_func():
    """
    This function opens the tamsatv3 data
    returns rainfall (3D), lat (1D), lon (1D), land_sea_mask (2D), and start year
    it uses the netCDF4 library
    """

    # Open netcdf file
    nc = netCDF4.Dataset('Example_data_TAMSATv3_daily_1997_2006_EastAfrica.nc')

    # Extrcat the variables
    rainfall = nc.variables['rfe'][:]
    lon      = nc.variables['longitude'][:]
    lat      = nc.variables['latitude'][:]

    # Create a land sea mask
    mask = np.nanmean(rainfall[:,:,:],axis=0)
    for i in np.arange(mask.shape[0]):
        for j in np.arange(mask.shape[1]):
            if math.isnan(mask[i,j]):
                mask[i,j]=0.0
            else:
                mask[i,j]=100.0

    # Return
    return rainfall, lat, lon, mask, 1997

# Test to check it works
if __name__=='__main__':
    rainfall, lat, lon, mask, start = open_tamsatv3_func()
    print (rainfall.shape)
    plt.contourf(lon, lat, np.mean(rainfall, axis=0))
    plt.show()

    plt.contourf(lon, lat, mask)
    plt.show()
