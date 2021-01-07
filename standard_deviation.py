#This code works out the standard deviation at each point to determine regions that are too dry.

# Import the necessary libraries
import numpy as np
import math

from open_rainfall_data import open_tamsatv3_func

import matplotlib.pyplot as plt
import cartopy

def calculate_standard_dev():
    """
    This function calculates the standard deviation at each grid point
    It is assumed that the data is in 3D format: time, lat, lon
    the output is then saved as a .npy file
    """


    # Open the data
    precip, lat, lon,  mask, start =  open_tamsatv3_func()
    data_name='TAMSATv3'
    year_length=365.0

    # Calculate standard deviation
    standard_deviation = np.zeros([precip.shape[1], precip.shape[2]])
    for i in np.arange(precip.shape[1]):
        for j in np.arange(precip.shape[2]):
            if mask[i,j]<50.0:
                standard_deviation[i,j] = np.nan
            else:
                standard_deviation[i,j] = np.nanstd(precip[:,i,j])

    # Save as a .npy file
    np.save('standard_deviation_mask_for_'+data_name+'.npy', standard_deviation)


def plot_standard_dev():
    """
    This code plots the standard deviation
    """

    # Open rainfall data (to get lats and lons)
    precip, lat, lon,  mask, start =  open_tamsatv3_func()

    # Open the fourier mask
    data_name = 'TAMSATv3'
    stdev_mask = np.load('standard_deviation_mask_for_'+data_name+'.npy')

    # Plot
    ax = plt.subplot(1,1,1, projection=cartopy.crs.PlateCarree())
    cp = plt.contourf(lon, lat, stdev_mask, transform=cartopy.crs.PlateCarree(), 
                        cmap='viridis_r', levels = np.arange(0.0,11.0,1), extend='max')
    cbar = plt.colorbar(cp)
    con = plt.contour(lon, lat, stdev_mask, transform=cartopy.crs.PlateCarree(),
                        levels=[1.0], colors='grey', linewidths=2, linestyles = 'dashed', dashes=(10,4))
    ax.add_feature(cartopy.feature.COASTLINE)
    ax.add_feature(cartopy.feature.BORDERS)
    plt.title('Standard Deviation Mask for '+data_name)
    plt.show()

if __name__=='__main__':
    calculate_standard_dev()
    plot_standard_dev()

