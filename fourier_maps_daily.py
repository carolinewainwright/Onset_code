# This code prints maps for the daily data showing the 
# Ratio of the power at one cycle per year
# to the power at two cycles per year
# It works mainly for daily data

# Import the necessary libraries
import netCDF4 
import numpy as np
import scipy.signal as ss
import matplotlib.pyplot as plt
from math import log

import sys
import os
import imp
from mpl_toolkits.basemap import Basemap
from basemap_africa_plot import basemap_africa_plot_func as plot_africa
sys.path.append('/home/vr031288/onset/amip_code')
from fourier_analysis1 import fourier_analysis

import colourbars as cb

from open_all_cmip_files_future import open_correct_model_run_cmip_future
from open_all_cmip_files_future import open_correct_model_run_cmip_historical

from open_tamsatv3 import open_tamsatv3_func

def find_closest_two_power(length):
    """
    This function finds the greatest power of 2 smaller than length
    It will return the power smaller to reduce zero padding 
    """
    power = log(length,2)
    new_length = 2**int(round(power))
    return new_length



def Fourier_Maps_CMIP(regridd = False):
    """
    This code produces the Fourier plots for the AMIP runs
    It loops through all the amip data
    Three plots are produced per model run
    HadGEM2-A has special options because it runs a 360 day year
    This function uses the  fourier_analysis function saved in fourier_analysis1.py
    regridd determines if the model data is regridded or not 
    """

    # Loop through all the model runs
    for model_run in [0]:#np.arange(30):#28 or 6 [22,23,24]: #
        if model_run==3:
            continue
        for rcp in ['rcp45']:#,'rcp85']:
            for years in ['2030-2049']:# ,'2080-2099']:

                # Open the data
                #precip, lat, lon, model_name, mask = open_correct_model_run_cmip_future(model_run, rcp, years,  regridd)

                #precip, lat, lon, model_name, mask = open_correct_model_run_cmip_historical(model_run,  regridd)
                precip, lat, lon,  mask, start =  open_tamsatv3_func()
                model_name='TAMSATv3'

                #rcp = 'historical'
                #years = '1980-1999'


                #print precip.shape
                #print precip.shape[0]/365
                #if model_name[0:3] !='Had':
                #    continue
                sens1,sens2,sens3 = 0.02,0.02,0.02# 0.04,0.04,0.04 #0.025,0.025,0.025
                print model_name+' data opened'
                #print precip.shape
                #print precip.shape[0]/365.0
                #print precip.shape[0]/360.0
                #if model_name[0:3] =='Had':
                #    sens1,sens2,sens3 = 0.022,0.022,0.02

                # Create storage array
                power_storage = precip[0:4].copy()

                # Loop through all grid points
                dimensions = precip.shape
                for i in np.arange(dimensions[1]):
                    print '%i of %i rows completed'%(i,dimensions[1])

                    for j in np.arange(dimensions[2]):

                        # Print precipitation timeseries to check
                        #if (i%10 == 0 and j%10 == 0):
                        #    plt.figure()
                        #    plt.plot(precip[:,i,j])
                        #    plt.show()

                        # Find freq, magnitude and phase
                        if model_name=='HadGEM2-CC' or model_name=='HadGEM2-ES' or model_name=='HadCM3' or model_name=='HadGEM2-CC_ReGrid2' or model_name=='HadGEM2-ES_ReGrid2' or model_name=='HadCM3_ReGrid2' or model_name=='HadGEM2-CC_ReGrid1' or model_name=='HadGEM2-ES_ReGrid1' or model_name=='HadCM3_ReGrid1': # 360 day years
                            #freq, mag, phase = fourier_analysis(precip[:,i,j], find_closest_two_power(dimensions[0]), detrend=1, dt=1.0/360.0)
                            freq, mag, phase = fourier_analysis(precip[:,i,j], dimensions[0], detrend=1, dt=1.0/360.0)

                        else:
                            freq, mag, phase = fourier_analysis(precip[:,i,j], find_closest_two_power(dimensions[0]), detrend=1, dt=1.0/365.0)
                            #freq, mag, phase = fourier_analysis(precip[:,i,j], dimensions[0], detrend=1, dt=1.0/365.0)

                        # Print power spectrum to check
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


                # Plot the results
                file_path = '/net/glusterfs_essc/scenario/users/vr031288/Onset/CMIP_Future/Fourier_plots/'

                # 1
                plt.figure()
                x = plot_africa(power_storage[0,:,:], lat, lon, '', 'Amplitude', np.arange(30)/100.0, 'both') #Power at 1 cycle/year
                #plt.savefig(file_path+model_name+'_'+rcp+'_'+years+'_powerat1.png')    
                plt.show()
                #plt.close()

                # 2
                plt.figure()
                x = plot_africa(power_storage[1,:,:], lat, lon, '', 'Amplitude', np.arange(20)/100.0, 'both')#Power at 2 cycle/year
                #plt.savefig(file_path+model_name+'_'+rcp+'_'+years+'_powerat2.png') 
                plt.show()
                #plt.close()

                # 3
                plt.figure()
                x = plot_africa(power_storage[2,:,:], lat, lon, '', 'Amplitude', np.arange(15)/100.0, 'both')
                #plt.savefig(file_path+model_name+'_'+rcp+'_'+years+'_powerat3.png') 
                plt.show()
                #plt.close()

                # 2:1
                # Ratio of Second to First Harmonic
                plt.figure()
                x = plot_africa(power_storage[3,:,:], lat, lon, '', '', np.arange(20)/10.0, 'max') 
                #plt.savefig(file_path+model_name+'_'+rcp+'_'+years+'_powerat2to1.png') 
                plt.show()
                #plt.close()

                #np.save('/net/glusterfs_essc/scenario/users/vr031288/Onset/CMIP_Future/Fourier_files/fourier_mask_incsea_for_'+model_name+'_'+rcp+'_'+years+'.npy', power_storage[3,:,:])
                np.save('/net/glusterfs_essc/scenario/users/vr031288/Onset/CMIP_Future/Fourier_files/fourier_mask_incsea_for_'+model_name+'.npy', np.array(power_storage[3,:,:]))

                # 2:1 masked
                # Ratio of Second to First Harmonic
                ratio_new = power_storage[3,:,:]
                ratio_new[np.where(mask<10)] = float('nan')
                plt.figure()
                x = plot_africa(ratio_new, lat, lon, '', '', np.arange(20)/10.0, 'max') 
                #plt.savefig(file_path+model_name+'powerat2to1_masked.png')  
                #plt.savefig(file_path+model_name+'_'+rcp+'_'+years+'_powerat2to1_masked.png') 
                plt.show()
                #plt.close()

                # Save the files 
                #np.save('/net/glusterfs_essc/scenario/users/vr031288/Onset/CMIP_Future/Fourier_files/fourier_mask_for_'+model_name+'_'+rcp+'_'+years+'.npy', power_storage[3,:,:])
                #np.save('/net/glusterfs_essc/scenario/users/vr031288/Onset/CMIP_Future/Fourier_files/fourier_alllevels_for_'+model_name+'_'+rcp+'_'+years+'.npy', np.array(power_storage[:,:,:]))
                np.save('/net/glusterfs_essc/scenario/users/vr031288/Onset/CMIP_Future/Fourier_files/fourier_mask_for_'+model_name+'.npy', np.array(power_storage[3,:,:]))
                np.save('/net/glusterfs_essc/scenario/users/vr031288/Onset/CMIP_Future/Fourier_files/fourier_alllevels_for_'+model_name+'.npy', np.array(power_storage[:,:,:]))



if __name__=="__main__":
    #Fourier_Maps_CMIP(2.0)
    #Fourier_Maps_CMIP(False)
    Fourier_Maps_CMIP(1.0) 
