# This code works out the standard deviation at each point to determine regions that are too dry.

# Import the necessary libraries
import netCDF4 
import numpy as np
import scipy.signal as ss
import math
import numpy.ma as ma
import sys
# Plotting libraries
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
sys.path.append('/home/vr031288/onset/amip_code')
from basemap_africa_plot import basemap_africa_plot_func as plot_africa
import colourbars as cb

from open_all_cmip_files_future import open_correct_model_run_cmip_future
from open_all_cmip_files_future import open_correct_model_run_cmip_historical
from open_tamsatv3 import open_tamsatv3_func

def calculate_standard_dev_CMIP(rg):
    """
    This function calculates the standard deviation at each grid point
    It is assumed that the data is in 3D format: time, lat, lon
    data determines the dataset used 
    plot determines whether the plots are produced or not
    it uses the open_correct_model_run function to open all of the cmip data
    the output is then saved so the standard deviation masks do not have to be re-saved each time. 
    """
    plot = True #False
    # Open correct data
    # Loop through all the model runs
    for model_run in np.arange(30):#1,7):#28):
        if model_run==3:
            continue
        for rcp in ['rcp45']:#,'rcp85']:
            for years in ['2030-2049' ]:#,'2080-2099']:
                #precip, lat, lon, model_name, mask = open_correct_model_run_cmip_future(model_run,rcp,years,rg)# False)#2.0)#False)#

                precip, lat, lon, model_name, mask = open_correct_model_run_cmip_historical(model_run,  rg)
                #precip, lat, lon, mask, start = open_tamsatv3_func()
                #model_name = 'TAMSATv3'

                #rcp = 'historical'
                #years = '1980-1999'
                print model_name
                print precip.shape[0]/365
                # Create storage array
                dimm = precip.shape
                st_dev_storage = np.zeros([dimm[1],dimm[2]])#precip[0].copy()

                # Loop through all grid points
                dimensions = st_dev_storage.shape
                for i in np.arange(dimensions[0]):
                    #if i%10 == 0:
                    #    print '%i rows completed'%i  
                    for j in np.arange(dimensions[1]):
                        st_dev_storage[i,j]  = np.std(precip[:,i,j])


                if plot == True:
                    # Plot the results
                    plt.figure()
                    x = plot_africa(st_dev_storage, lat, lon, 'Standard deviation of daily rainfall for '+model_name, 'mm', np.arange(20)/2.0, 'both')
                    plt.show()

                    st_dev_storage[np.where(st_dev_storage<1.0)] = float('nan')
                    plt.figure()
                    x = plot_africa(st_dev_storage, lat, lon, 'Standard deviation of daily rainfall for '+model_name, 'mm', np.arange(20)/2.0, 'both')
                    plt.show()

                # Save the files
                np.save('/net/glusterfs_essc/scenario/users/vr031288/Onset/CMIP_Future/StdDev_files/stddev_mask_for_'+model_name+'_'+rcp+'_'+years+'.npy', st_dev_storage[:,:])
                #np.save('/net/glusterfs_essc/scenario/users/vr031288/Onset/CMIP_Future/StdDev_files/stddev_mask_for_'+model_name+'.npy', st_dev_storage[:,:])

if __name__=="__main__":
    calculate_standard_dev_CMIP(False)
    calculate_standard_dev_CMIP(1.0)
