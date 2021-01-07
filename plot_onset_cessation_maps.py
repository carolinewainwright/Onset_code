# This code plots the mean onset/cessation for the different simulations
# it is mainly used to look at different fourier regions

import numpy as np
import math
import matplotlib.pyplot as plt
import netCDF4
import cartopy
import matplotlib
font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 16}
matplotlib.rc('font', **font)
import matplotlib.colors as colors
from open_rainfall_data import open_tamsatv3_func

#~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~#

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

#~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~#
def plot_mean_onset_cessation():
    """
    This function plots the mean onset/cessation
    """

    # Set Year Length
    year_len=365

    # Open the file
    nc_file_string = 'TAMSATv3_onset_end.nc'

    # Open the onset/cessation file
    onset_nc_file = netCDF4.Dataset(nc_file_string)

    # Extract the variables
    lon             = onset_nc_file.variables['lon'][:]
    lat             = onset_nc_file.variables['lat'][:]
    onset           = np.nanmean(onset_nc_file.variables['onset'][:],axis=0)
    cessation       = np.nanmean(onset_nc_file.variables['cessation'][:],axis=0)
    short_onset     = np.nanmean(onset_nc_file.variables['short_onset'][:],axis=0)
    short_cessation = np.nanmean(onset_nc_file.variables['short_cessation'][:],axis=0)
    long_onset      = np.nanmean(onset_nc_file.variables['long_onset'][:],axis=0)
    long_cessation  = np.nanmean(onset_nc_file.variables['long_cessation'][:],axis=0)


    # Open the foutier mask
    fourier_mask = np.load('fourier_mask_for_TAMSATv3.npy')
    #precip, lat, lon,  mask, start =  open_tamsatv3_func()


    # Create a plot
    plt.figure(figsize=(14,16))
    title_strings = ['a) Onset','b) Cessation','c) Onset (Long rains)','d) Cessation (Long rains)','e) Onset (Short rains)','f) Cessation (Short rains)']

    for plot_ind,matrix in enumerate([onset,cessation,long_onset,long_cessation,short_onset,short_cessation]):

        ax = plt.subplot(3,2,plot_ind+1,projection=cartopy.crs.PlateCarree())

        # Remove >365/360
        matrix[np.where(matrix>year_len)] = matrix[np.where(matrix>year_len)]-year_len
        matrix[np.where(matrix<0)] = matrix[np.where(matrix<0)]+year_len

        #Add dots
        maskked =  np.ma.masked_where(np.isnan(matrix),matrix)
        con  = plt.pcolor(lon, lat, maskked,  transform=cartopy.crs.PlateCarree(), 
                        cmap = plt.cm.rainbow, edgecolors='none', vmin=0, vmax=year_len)

        cbar = plt.colorbar(con)
        cbar.set_label('Date of year')
        start_days = np.array([0,31,59,90,120,151,181,212,243,273,304,334,365])
        start_mons = np.array(['Jan 1','Feb 1','Mar 1', 'Apr 1','May 1','June 1', 'July 1','Aug 1', 'Sep 1','Oct 1','Nov 1','Dec 1','Jan 1'])
        cbar.set_ticks(start_days[np.where(start_days>=0)])
        cbar.set_ticklabels(start_mons[np.where(start_days>=0)])
        plt.title(title_strings[plot_ind])

        ax.add_feature(cartopy.feature.COASTLINE)
        ax.add_feature(cartopy.feature.BORDERS)

        # Add grey mask
        if plot_ind<2:
            plt.contourf(lon, lat, fourier_mask, levels=[1.0,1000.0], cmap=truncate_colormap(plt.get_cmap('Greys'), 0.0, 0.5),extend='neither')
        else:
            plt.contourf(lon, lat, fourier_mask, levels=[0.0,1.0], cmap=truncate_colormap(plt.get_cmap('Greys'), 0.0, 0.5),extend='neither')
        plt.contour(lon, lat, fourier_mask, levels=[1.0], color='navy', linewidths=2)

    plt.subplots_adjust(left=0.03, bottom=0.04, right=None, top=None, wspace=None, hspace=None)
    plt.savefig('TAMSATv3_onset_cessation_plot.png')
    plt.show()

#~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~()~#
if __name__=='__main__':
    plot_mean_onset_cessation()
