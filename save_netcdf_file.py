# This function saves the onset and cessation dates
# as a netcdf file


import numpy as np
import netCDF4 

def save_onset_cessation_netcdf(data_name, lat, lon, start, storage_onset, storage_cessation, storage_length, 
                                storage_onset_lo, storage_cessation_lo,storage_length_lo,
                                storage_onset_sh,storage_cessation_sh, storage_length_sh):

    """
    This function saves the onset and cessation dates as a netcdf file
    The onset for long and short rains are also included
    The time is determined by the length of the array and the start date
    This function uses the netcdf4 and numpy libraries
    """

    # Set up netcdf file
    ncw = netCDF4.Dataset(data_name+'_onset_end.nc', 'w')
    ncw.setncattr('Conventions', 'CF-1.5')
    ncw.setncattr('Created', 'Created using save_netcdf_file.py and onset_end_files.py')

    # Create dimensions
    dimensions = storage_onset.shape
    numLon  = dimensions[2]
    numLat  = dimensions[1]
    numTime = dimensions[0]
    lonDim  = ncw.createDimension('lon', numLon)
    latDim  = ncw.createDimension('lat', numLat)
    timDim  = ncw.createDimension('time', numTime)

    # Create dimension variables
    lonVar = ncw.createVariable('lon', 'f8', ('lon',))
    lonVar.setncattr('long_name', 'longitude')
    lonVar.setncattr('units', 'degrees_east')

    latVar = ncw.createVariable('lat', 'f8', ('lat',))
    latVar.setncattr('long_name', 'latitude')
    latVar.setncattr('units', 'degrees_north')

    timVar = ncw.createVariable('time', 'f8', ('time',))
    timVar.setncattr('long_name', 'Time')
    timVar.setncattr('units', 'years since %4i-1-1 00:00:0.0'%(start))

    # Create variables to hold onset etc
    # Unimodal
    onset_var = ncw.createVariable('onset', 'f8', ('time','lat', 'lon'))
    onset_var.setncattr('units', 'day')
    onset_var.setncattr('long_name', 'Onset Date for Annual Regions')

    end_var = ncw.createVariable('cessation', 'f8', ('time','lat', 'lon'))
    end_var.setncattr('units', 'day')
    end_var.setncattr('long_name', 'Cessation Date for Annual Regions')

    length_var = ncw.createVariable('length', 'f8', ('time','lat', 'lon'))
    length_var.setncattr('units', 'day')
    length_var.setncattr('long_name', 'Season Length for Annual Regions')

    # Long rains
    long_onset_var = ncw.createVariable('long_onset', 'f8', ('time','lat', 'lon'))
    long_onset_var.setncattr('units', 'day')
    long_onset_var.setncattr('long_name', 'Onset Date for Long Rains')

    long_end_var = ncw.createVariable('long_cessation', 'f8', ('time','lat', 'lon'))
    long_end_var.setncattr('units', 'day')
    long_end_var.setncattr('long_name', 'Cessation Date for Long Rains')

    long_length_var = ncw.createVariable('long_length', 'f8', ('time','lat', 'lon'))
    long_length_var.setncattr('units', 'day')
    long_length_var.setncattr('long_name', 'Season Length for Long Rains')

    # Short rains
    short_onset_var = ncw.createVariable('short_onset', 'f8', ('time','lat', 'lon'))
    short_onset_var.setncattr('units', 'day')
    short_onset_var.setncattr('long_name', 'Onset Date for Short Rains')

    short_end_var = ncw.createVariable('short_cessation', 'f8', ('time','lat', 'lon'))
    short_end_var.setncattr('units', 'day')
    short_end_var.setncattr('long_name', 'Cessation Date for Short Rains')

    short_length_var = ncw.createVariable('short_length', 'f8', ('time','lat', 'lon'))
    short_length_var.setncattr('units', 'day')
    short_length_var.setncattr('long_name', 'Season Length for Short Rains')


    # Write values to the variables
    lonVar[:] = lon
    latVar[:] = lat
    timVar[:] = np.arange(1,1+dimensions[0],1)

    onset_var[:]         = storage_onset
    end_var[:]           = storage_cessation
    length_var[:]        = storage_length

    long_onset_var[:]    = storage_onset_lo
    long_end_var[:]      = storage_cessation_lo
    long_length_var[:]   = storage_length_lo

    short_onset_var[:]   = storage_onset_sh
    short_end_var[:]     = storage_cessation_sh
    short_length_var[:]  = storage_length_sh


    # Close the file
    ncw.close()

