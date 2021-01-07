# This code calculates the harmonic ratio
# to determine if a region has one or two wet seasons per yea
# It works on daily data

# Import the necessary libraries
import numpy as np
import scipy.signal as ss
from math import log

from fourier_analysis1 import fourier_analysis

from open_rainfall_data import open_tamsatv3_func

import matplotlib.pyplot as plt
import cartopy



def find_closest_two_power(length):
    """
    This function finds the greatest power of 2 smaller than length
    It will return the power smaller to reduce zero padding 
    """
    power = log(length,2)
    new_length = 2**int(round(power))
    return new_length




def Fourier_Map():
    """
    This code produces the Fourier maps and masks
    This function uses the  fourier_analysis function saved in fourier_analysis1.py
    """


    # Open the data
    precip, lat, lon,  mask, start =  open_tamsatv3_func()
    data_name='TAMSATv3'
    year_length=365.0

    # Set senitivities - may need to be adjusted if you get NaNs!
    # If you get NaNs then increase the value
    sens1,sens2,sens3 = 0.03,0.03,0.03# 0.04,0.04,0.04

    # Create storage array
    power_storage = precip[0:4].copy()
    power_storage[:] = np.nan

    # Loop through all grid points
    dimensions = precip.shape
    for i in np.arange(dimensions[1]):
        print ('%i of %i rows completed'%(i,dimensions[1]))
        for j in np.arange(dimensions[2]):

            if mask[i,j]<50:
                continue

            # Find freq, magnitude and phase
            # First line maximises two season region
            #freq, mag, phase = fourier_analysis(precip[:,i,j], find_closest_two_power(dimensions[0]), detrend=1, dt=1.0/year_length)
            freq, mag, phase = fourier_analysis(precip[:,i,j], dimensions[0], detrend=1, dt=1.0/year_length)

            # Print power spectrum to check
            # Can uncomment if you want to check some sprectra
            #if (i%10 == 0 and j%10 == 0):
            #    plt.figure()
            #    plt.semilogx(freq, mag)
            #    plt.show() 

            # Find power at 1/2/3 cycles per year
            power_storage[0,i,j] = np.mean(mag[np.where(np.abs(freq-1)<=sens1)[0]]) 
            power_storage[1,i,j] = np.mean(mag[np.where(np.abs(freq-2)<=sens2)[0]])                   
            power_storage[2,i,j] = np.mean(mag[np.where(np.abs(freq-3)<=sens3)[0]])


    # Calculate the ratio of 2 to 1
    power_storage[3,:,:] = power_storage[1,:,:]/power_storage[0,:,:]

    # Save the file
    np.save('fourier_mask_for_'+data_name+'.npy', np.array(power_storage[3,:,:]))



def plot_fourier_map():
    """
    This code plots the fourier mask
    """

    # Open rainfall data (to get lats and lons)
    precip, lat, lon,  mask, start =  open_tamsatv3_func()

    # Open the fourier mask
    data_name = 'TAMSATv3'
    fourier_mask = np.load('fourier_mask_for_'+data_name+'.npy')

    # Plot
    ax = plt.subplot(1,1,1, projection=cartopy.crs.PlateCarree())
    cp = plt.contourf(lon, lat, fourier_mask, transform=cartopy.crs.PlateCarree(), 
                        cmap='magma', levels = np.arange(0.0,2.0,0.2), extend='max')
    cbar = plt.colorbar(cp)
    con = plt.contour(lon, lat, fourier_mask, transform=cartopy.crs.PlateCarree(),
                        levels=[1.0], colors='grey', linewidths=2, linestyles = 'dashed', dashes=(10,4))
    ax.add_feature(cartopy.feature.COASTLINE)
    ax.add_feature(cartopy.feature.BORDERS)
    plt.title('Fourier mask for '+data_name)
    plt.show()



if __name__=="__main__":
    Fourier_Map()
    plot_fourier_map()
