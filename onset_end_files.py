# This code creates onset and cessation files for TAMSAT data
# It opens the fourier and standard deviation masks that are already saved elsewhere
# The result is saved as a netcdf file with onset and end of annual and biannual seasons
# The method used is the same of that in Dunning et al. (2016)
# The method uses the fourier mask to determine where is annual and where is biannual
# Fourier masks have been computed using the fourier_maps_daily code ad are imported as .npy files
# The find_water_year and find_wet_season codes are also imported from elsewhere
# leap days should have been removed!!!


# Import the necessary libraries and functions
import numpy as np
import math

from save_netcdf_file import save_onset_cessation_netcdf                         # To save results


#sys.path.append('/home/vr031288/onset/amip_code')
from find_water_year_or_season import find_water_year_start                      #
from find_water_year_or_season import find_water_year_start_twoseasons           # To run onset code
from find_wet_seasons import find_onset_and_cessation                            #

from open_rainfall_data import open_tamsatv3_func


def calculate_onset_and_cessation():
    """
    This function finds the onset and cessation
    Data is assumed to be of the format time, lat, lon
    """

    # Open data, land sea mask, fourier mask and std dev mask
    print 'Started calculating onset etc.'
    print 'Loading data...'
    initial_data, lat, lon, land_sea_mask, start_date_tamsat= open_tamsatv3_func()
    data_name = 'TAMSATv3'
    std_dev_mask = np.load('standard_deviation_mask_for_'+data_name+'.npy')
    fourier_mask = np.load('fourier_mask_for_'+data_name+'.npy')
    year_length = 365 # Some models have 360 day years

    print 'Data loaded'
    print initial_data.shape[0]/float(year_length)

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
            if land_sea_mask[i,j]<50.0 or std_dev_mask[i,j]<1.0:
                storage_onset[:,i,j]        = np.nan
                storage_cessation[:,i,j]    = np.nan
                storage_length[:,i,j]       = np.nan
                storage_onset_lo[:,i,j]     = np.nan
                storage_cessation_lo[:,i,j] = np.nan
                storage_length_lo[:,i,j]    = np.nan
                storage_onset_sh[:,i,j]     = np.nan
                storage_cessation_sh[:,i,j] = np.nan
                storage_length_sh[:,i,j]    = np.nan
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
                storage_onset[:,i,j]        = onsets
                storage_cessation[:,i,j]    = cessations
                storage_length[:,i,j]       = cessations - onsets

                # Set two to nan
                storage_onset_lo[:,i,j]     = np.nan
                storage_onset_sh[:,i,j]     = np.nan
                storage_cessation_lo[:,i,j] = np.nan
                storage_cessation_sh[:,i,j] = np.nan
                storage_length_lo[:,i,j]    = np.nan
                storage_length_sh[:,i,j]    = np.nan


            # BIMODAL
            else: 
                # Find the start of the water year
                (start1,end1,start2,end2) = find_water_year_start_twoseasons(timeseries,year_length)

                # If this method has failed to find any starts or ends use other method
                if math.isnan(start1):
                    (start,end) = find_water_year_start(timeseries)
                    # Find the onset and cessation
                    onsets,cessations = find_onset_and_cessation(timeseries, start, end,50,50,year_length)
                    storage_onset[:,i,j]        = onsets
                    storage_cessation[:,i,j]    = cessations
                    storage_length[:,i,j]       = cessations - onsets

                    # Set two to nan
                    storage_onset_lo[:,i,j]     = np.nan
                    storage_onset_sh[:,i,j]     = np.nan
                    storage_cessation_lo[:,i,j] = np.nan
                    storage_cessation_sh[:,i,j] = np.nan
                    storage_length_lo[:,i,j]    = np.nan
                    storage_length_sh[:,i,j]    = np.nan

                # It it has only managed to find one season
                elif math.isnan(start2):
                    onsets,cessations= find_onset_and_cessation(timeseries, start1, end1,50,50,year_length)
                    storage_onset[:,i,j]        = onsets
                    storage_cessation[:,i,j]    = cessations
                    storage_length[:,i,j]       = cessations - onsets

                    # Set two to nan
                    storage_onset_lo[:,i,j]     = np.nan
                    storage_onset_sh[:,i,j]     = np.nan
                    storage_cessation_lo[:,i,j] = np.nan
                    storage_cessation_sh[:,i,j] = np.nan
                    storage_length_lo[:,i,j]    = np.nan
                    storage_length_sh[:,i,j]    = np.nan

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
                    storage_onset[:,i,j]        = np.nan
                    storage_cessation[:,i,j]    = np.nan
                    storage_length[:,i,j]       = np.nan


    # Save the arrays
    save_onset_cessation_netcdf(data_name, lat, lon, start_date_tamsat, 
                                storage_onset, storage_cessation, storage_length, 
                                storage_onset_lo, storage_cessation_lo,storage_length_lo,
                                storage_onset_sh,storage_cessation_sh, storage_length_sh)

if __name__=='__main__':
    calculate_onset_and_cessation()
