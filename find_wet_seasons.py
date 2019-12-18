# This code contains the function that is used to identify 
# the onset and cessation dates in specific years
# The same function is used for both the bimodal and the unimodal regions

import math
import numpy as np
#import matplotlib.pyplot as plt

def find_onset_and_cessation(timeseries, start, end_year, window1, window2,year_length):
    """
    This function finds the onset and cessation of the wet season
    The methodology is based on that of Liebmann et al. (2012) Journal of Climate
    The full methodology is described in Dunning et al. (2016)
    It uses the numpy library
    It does not work out the onset and end for first and last year
    For each year it starts searching 'window1' days prior to the start of the water year
    The index of the start of the water year is given by 'start'
    'timeseries' should be one dimensional and be a multiple of year_length long
    window1 and window2 determines how far each side of the wet season days are searched for (start and end resp.)
    Leap days should have already been removed
    start should be in the range 0-364
    The anomaly is calculated over all year first, then the relevant parts are selected and summed
    """


    # Calculate p-alpha
    p_minus_alpha = timeseries - np.mean(timeseries)


    # Create storage arrays
    # Don't calculate for the first or last year
    years = timeseries.shape[0]/year_length-1
    onset = np.zeros(years-1)
    end   = np.zeros(years-1)
    onset_success = []
    end_success   = []

    # Loop through second to penultimate year
    #plt.figure()
    for year in np.arange(1,years):

        # Select the anomaly from start - window to end + window
        begin = int(year*year_length+start-window1)
        endd = int(year*year_length+end_year+window2)
        this_year = p_minus_alpha[begin:endd]

        # Calculate the cumulative precipitation for that period
        delta = this_year.copy()
        for day in np.arange(len(this_year)):
            delta[day] = np.sum(this_year[0:day+1])
        

        # Find the index of the absolute min and max
        # Modify so that the min is not at the end and max is after min
        min_index = np.argmin(delta)
        # Check that the min is not right at the end of the record (within last 8 days)
        # Iterate until it is not at the end
        length_6 = len(delta)-8
        iterr = 0
        while min_index>length_6:
            iterr +=1
            delta_con = delta[:-7*iterr]
            min_index = np.argmin(delta_con)
            length_6 = length_6 - 7
            if length_6<10:
                min_index = float('nan')
                break
        if math.isnan(min_index):
           max_index = float('nan')
        else:
            max_index = np.argmax(delta[min_index:])+min_index

        # Plot to test
        #ax1 = plt.subplot(4,4,year)
        #ax1.plot(this_year, color='DodgerBlue')
        #ax2 = ax1.twinx()
        #ax2.plot(delta, 'g', linewidth=3)
        #ax2.plot([min_index+1, min_index+1], [min(delta)-10,max(delta)+10], 'm', linewidth=4) 
        #ax2.plot([max_index+1, max_index+1], [min(delta)-10,max(delta)+10], 'm', linewidth=4) 
        


        # Transform to 'day of the year'
        onset_day     = min_index+start-window1+1
        cessation_day = max_index+start-window1


        # Store in onset and cessation arrays
        if onset_day > cessation_day:  #Not successful
            print 'why did this happen? - onset>cesssation in find_onset_and_cessation function'
            onset[year-1] = float('nan')
            end[year-1]   = float('nan')
        else: 
            # If onset day and cessation day are nans then it will do this loop
            onset[year-1] = onset_day
            end[year-1]   = cessation_day


    #plt.show()
    return onset, end
