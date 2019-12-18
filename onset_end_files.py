# This code creates onset and cessation files for the CMIP runs
# It opens the fourier and standard deviation masks that are already saved elsewhere
# The result is saved as a netcdf file with onset and end of unimodal and bimodal seasons
# The method used is the same of that in Dunning et al. (submitted)
# The method uses the fourier mask to determine where is unimodal and where is bimodal
# Fourier masks have been computed using the fourier_maps_daily code ad are imported as .npy files
# The find_water_year and find_wet_season codes are also imported from elsewhere


# Import the necessary libraries and functions
import numpy as np
import math

from open_all_cmip_files_future import open_correct_model_run_cmip_future                  # To open cmip data
from open_all_cmip_files_future import open_correct_model_run_cmip_historical                  # To open cmip data
from save_netcdf_file import save_onset_cessation_netcdf_cmip                         # To save results
import sys


#sys.path.append('/home/vr031288/onset/amip_code')
from find_water_year_or_season import find_water_year_start                      #
from find_water_year_or_season import find_water_year_start_twoseasons           # To run onset code
from find_wet_seasons import find_onset_and_cessation                            #


                                                                       #
#sys.path.append('/home/vr031288/onset/code')                                     # To import the GPCP data
#from create_land_sea_gpcp import create_land_sea_mask_gpcp                       # to test the code
#from open_data_functions import open_gpcp_1dd_all                                #

from open_tamsatv3 import open_tamsatv3_func 

# Find the onset etc.

def find_onset_and_cessation_cmip(model_number,rcp,years):
    """
    This function finds the onset and cessation for the amip data
    Data is assumed to be of the format time, lat, lon
    the argument: model_number, rcp and years determines which model is used 
    """

    
    # Open data, land sea mask, fourier mask and std dev mask
    print 'Started calculating onset etc.'
    print 'Loading data...'
    #if rcp=='historical':
    #    initial_data, lat, lon, model_name, land_sea_mask = open_correct_model_run_cmip_historical(model_number,  1.0)#False)
    #else:
    #    initial_data, lat, lon, model_name, land_sea_mask = open_correct_model_run_cmip_future(model_number, rcp,years, 1.0)#False)#1.0)#
    #std_dev_mask = np.load('/net/glusterfs_essc/scenario/users/vr031288/Onset/CMIP_Future/StdDev_files/stddev_mask_for_'+model_name+'_'+rcp+'_'+years+'.npy')
    #fourier_mask = np.load('/net/glusterfs_essc/scenario/users/vr031288/Onset/CMIP_Future/Fourier_files/fourier_mask_for_'+model_name+'_'+rcp+'_'+years+'.npy')
    #year_length = 365


    initial_data, lat, lon,land_sea_mask, start_date_tamsat= open_tamsatv3_func()
    model_name = 'TAMSATv3'
    std_dev_mask = np.load('/glusterfs/scenario/users/vr031288/Onset/CMIP_Future/StdDev_files/stddev_mask_for_'+model_name+'.npy')
    fourier_mask = np.load('/glusterfs/scenario/users/vr031288/Onset/CMIP_Future/Fourier_files/fourier_mask_for_'+model_name+'.npy')
    year_length = 365

    print model_name

    if model_name=='HadGEM2-CC' or model_name=='HadGEM2-ES' or model_name=='HadCM3' or model_name=='HadGEM2-CC_ReGrid2' or model_name=='HadGEM2-ES_ReGrid2' or model_name=='HadCM3_ReGrid2' or model_name=='HadGEM2-CC_ReGrid1' or model_name=='HadGEM2-ES_ReGrid1' or model_name=='HadCM3_ReGrid1' :
        year_length = 360

    print 'Data loaded for '+model_name
    print initial_data.shape[0]/float(year_length)

    # This scetion imports the GPCP data to test the code 
    #initial_data, startyear,lon, lat =   open_gpcp_1dd_all()
    #land_sea_mask = create_land_sea_mask_gpcp()
    #land_sea_mask[np.where(land_sea_mask==0)] = 100.0
    #fourier_mask = np.load('/net/glusterfs_essc/scenario/users/vr031288/Onset/fourier_mask_for_GPCP_1DD.npy')
    #std_dev_mask = np.load('/net/glusterfs_essc/scenario/users/vr031288/Onset/AMIP/StdDev_files/stddev_mask_for_GPCP_1DD.npy')
    #model_name = 'GPCP_1DD'
    #year_length = 365
    #print 'Data loaded for '+model_name


    # Find the dimensions and set up storage arrays
    data       = initial_data.copy()
    dimensions = data.shape
    # Storage arrays are two shorter as onset and cessation is not calaculated in the first or last year
    storage_onset     = np.zeros([dimensions[0]/year_length-2, dimensions[1],dimensions[2]])     #onset 
    storage_cessation = np.zeros([dimensions[0]/year_length-2, dimensions[1],dimensions[2]])     #cessation 
    storage_length    = np.zeros([dimensions[0]/year_length-2, dimensions[1],dimensions[2]])     #length 

    storage_onset_lo     = np.zeros([dimensions[0]/year_length-2, dimensions[1],dimensions[2]])   #LONG RAINS onset 
    storage_cessation_lo = np.zeros([dimensions[0]/year_length-2, dimensions[1],dimensions[2]])   #cessation 
    storage_length_lo    = np.zeros([dimensions[0]/year_length-2, dimensions[1],dimensions[2]])   #length 

    storage_onset_sh     = np.zeros([dimensions[0]/year_length-2, dimensions[1],dimensions[2]])   #SHORT RAINS onset 
    storage_cessation_sh = np.zeros([dimensions[0]/year_length-2, dimensions[1],dimensions[2]])   #cessation 
    storage_length_sh    = np.zeros([dimensions[0]/year_length-2, dimensions[1],dimensions[2]])   #length


    # Loop through each grid point
    for i in np.arange(dimensions[1]):
        if i%1 == 0:
            print '%i out of %i rows completed'%(i,dimensions[1])
        for j in np.arange(dimensions[2]):

            # Mask out the sea and where std dev < 1.0 mm/day
            if land_sea_mask[i,j]<10 or std_dev_mask[i,j]<1.0:
                storage_onset[:,i,j] = float('nan')
                storage_cessation[:,i,j] = float('nan')
                storage_length[:,i,j] = float('nan')
                storage_onset_lo[:,i,j] = float('nan')
                storage_cessation_lo[:,i,j] = float('nan')
                storage_length_lo[:,i,j] = float('nan')
                storage_onset_sh[:,i,j] = float('nan')
                storage_cessation_sh[:,i,j] = float('nan')
                storage_length_sh[:,i,j] = float('nan')
                continue

            # Extract timeseries
            timeseries = data[:,i,j]

            # Check to see if one of two cycles
            # UNIMODAL 
            if fourier_mask[i,j] < 1.0:
                # Find the start of the water year
                (start,end) = find_water_year_start(timeseries,year_length)

                # Find the onset and cessation
                onsets,cessations = find_onset_and_cessation(timeseries, start, end,50,50,year_length)
                storage_onset[:,i,j] = onsets
                storage_cessation[:,i,j] = cessations
                storage_length[:,i,j] = cessations - onsets

                # Set two to nan
                storage_onset_lo[:,i,j] = float('nan')
                storage_onset_sh[:,i,j] = float('nan')
                storage_cessation_lo[:,i,j] = float('nan')
                storage_cessation_sh[:,i,j] = float('nan')
                storage_length_lo[:,i,j] = float('nan')
                storage_length_sh[:,i,j] = float('nan')


            # BIMODAL
            else: 
                # Find the start of the water year
                (start1,end1,start2,end2) = find_water_year_start_twoseasons(timeseries,year_length)

                # If this method has failed to find any starts or ends use other method
                if math.isnan(start1):
                    (start,end) = find_water_year_start(timeseries)
                    # Find the onset and cessation
                    onsets,cessations = find_onset_and_cessation(timeseries, start, end,50,50,year_length)
                    storage_onset[:,i,j] = onsets
                    storage_cessation[:,i,j] = cessations
                    storage_length[:,i,j] = cessations - onsets

                    # Set two to nan
                    storage_onset_lo[:,i,j] = float('nan')
                    storage_onset_sh[:,i,j] = float('nan')
                    storage_cessation_lo[:,i,j] = float('nan')
                    storage_cessation_sh[:,i,j] = float('nan')
                    storage_length_lo[:,i,j] = float('nan')
                    storage_length_sh[:,i,j] = float('nan')

                # It it has only managed to find one season
                elif math.isnan(start2):
                    onsets,cessations= find_onset_and_cessation(timeseries, start1, end1,50,50,year_length)
                    storage_onset[:,i,j] = onsets
                    storage_cessation[:,i,j] = cessations
                    storage_length[:,i,j] = cessations - onsets

                    # Set two to nan
                    storage_onset_lo[:,i,j] = float('nan')
                    storage_onset_sh[:,i,j] = float('nan')
                    storage_cessation_lo[:,i,j] = float('nan')
                    storage_cessation_sh[:,i,j] = float('nan')
                    storage_length_lo[:,i,j] = float('nan')
                    storage_length_sh[:,i,j] = float('nan')

                # If both start1 and start2 are not nans then it has found 2 seasons!
                else:
                    # Find the onset and cessation of major season
                    onset1,cess1= find_onset_and_cessation(timeseries, start1, end1,20,20,year_length)
                    # Find the onset and cessation of minor season
                    onset2, cess2 = find_onset_and_cessation(timeseries, start2, end2,20,20,year_length)

                    if start1<331 and start1>150 and start2<331 and start2>150: # both in region 31st May-1st Dec
                        if start1>start2:                 # start1 is later so start1 is short rains
                            storage_onset_lo[:,i,j] = onset2
                            storage_onset_sh[:,i,j] = onset1
                            storage_cessation_lo[:,i,j] = cess2
                            storage_cessation_sh[:,i,j] = cess1
                            storage_length_lo[:,i,j] = cess2-onset2
                            storage_length_sh[:,i,j] = cess1-onset1

                        else:
                            storage_onset_lo[:,i,j] = onset1
                            storage_onset_sh[:,i,j] = onset2
                            storage_cessation_lo[:,i,j] = cess1
                            storage_cessation_sh[:,i,j] = cess2
                            storage_length_lo[:,i,j] = cess1-onset1
                            storage_length_sh[:,i,j] = cess2-onset2

                    elif start1 <331 and start1>150:      # start1 is short rains 
                        storage_onset_lo[:,i,j] = onset2
                        storage_onset_sh[:,i,j] = onset1
                        storage_cessation_lo[:,i,j] = cess2
                        storage_cessation_sh[:,i,j] = cess1
                        storage_length_lo[:,i,j] = cess2-onset2
                        storage_length_sh[:,i,j] = cess1-onset1


                    else:
                        storage_onset_lo[:,i,j] = onset1
                        storage_onset_sh[:,i,j] = onset2
                        storage_cessation_lo[:,i,j] = cess1
                        storage_cessation_sh[:,i,j] = cess2
                        storage_length_lo[:,i,j] = cess1-onset1
                        storage_length_sh[:,i,j] = cess2-onset2

 
                    # Set one to nan
                    storage_onset[:,i,j] = float('nan')
                    storage_cessation[:,i,j] = float('nan')
                    storage_length[:,i,j] = float('nan')







    # Save the arrays
    #save_onset_cessation_netcdf_cmip(model_name+'_'+rcp+'_'+years, lat, lon, int(years[0:4]), storage_onset, storage_cessation, storage_length, storage_onset_lo, storage_cessation_lo,storage_length_lo,storage_onset_sh,storage_cessation_sh, storage_length_sh)
    save_onset_cessation_netcdf_cmip(model_name, lat, lon, start_date_tamsat, storage_onset, storage_cessation, storage_length, storage_onset_lo, storage_cessation_lo,storage_length_lo,storage_onset_sh,storage_cessation_sh, storage_length_sh)

if __name__=='__main__':
    """
    for i in np.arange(30): #1,7):#28
        if i ==3:
            continue
        for rcp in ['rcp45','rcp85']:
            for years in ['2030-2049' ,'2080-2099']:
                find_onset_and_cessation_cmip(i,rcp,years)

        rcp, years = 'historical', '1980-1999'
        find_onset_and_cessation_cmip(i,rcp,years)
    """

    find_onset_and_cessation_cmip(None,None,None)
