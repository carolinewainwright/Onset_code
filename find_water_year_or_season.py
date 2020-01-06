# This script contains the code to find the start and end of the 
# climatological water year for regions with one wet season per year
# or the start and end of the two climatological water seasons 
# if the point in question has two wet seasons per year
# It also contains the functions used to find the minima and maxima that is needed
# in order for the two season method to work


import numpy as np
import math
import matplotlib.pyplot as plt

# UNIMODAL
def find_water_year_start(timeseries_input,year_length):
    """
    This function finds the start and end of the climatological water year
    Based on the method of Liebmann et al. (2012) Journal of Climate
    The new method is fully described in Dunning et al (2016)
    It uses the numpy library
    'timeseries' should be one dimensional and be a multiple of 'year_length' long
    Leap days should have already been removed
    Start is returned and is in the range 0-year_length-1
    This function only works if there are no nans in the data
    If there are nans in the data then it will raise a ValueError
    """

    # Cap timeseries
    timeseries = timeseries_input.copy()
    #timeseries[np.where(timeseries>30.0)] = 30.0
    #print np.nanmax(timeseries)

    # Check it is a multiple of year_length long
    length = len(timeseries)
    if length%year_length != 0:
        raise ValueError('The timeseries must be a multiple of year_length long. Please try again')

    # Find alpha
    # This is the daily mean over all the data
    alpha = np.mean(timeseries)

    # Use this to test and see if there are any nans in the data
    if math.isnan(alpha):
        raise ValueError('The timeseries contains NaNs. Please remove and try again')
 
    # Find beta
    # This is the climatological daily mean rainfall on each day of the calendar year
    beta = np.zeros(year_length)
    for day in np.arange(year_length):
        beta[day] = np.mean(timeseries[day::year_length])


    # Find beta - alpha
    # This is the climatological daily mean rainfall anomaly
    bma = beta - alpha
    gamma = bma.copy()

    # Sum
    # Gamma is then the cumulative climatological daily mean rainfall anomaly
    for day in np.arange(year_length):  
        gamma[day] = np.sum(bma[0:day+1])

 
    # Find index of the minimum and max     
    min_index = np.argmin(gamma)
    max_index = np.argmax(gamma)

    # Start is the day after the minimum
    start = min_index + 1
    # End is the day of the maximum 
    # If end less than start, end+year_length; this means the season goes over the end of the calendar year
    end = max_index + 0
    if end < start:
        end += year_length

    # Return start 
    return start,end



# BIMODAL

# Define functions to help with identifying peaks and troughs 
def MovingAverage(interval, window_size):
    window= np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'valid')

def is_it_min(listt, index):
    test_value = listt[index]
    test_list = listt[index-4:index+5]
    if np.argmin(test_list) == 4:
        return True
    else:
        return False

def is_it_max(listt, index):
    test_value = listt[index]
    test_list = listt[index-4:index+5]
    if np.argmax(test_list) == 4:
        return True
    else:
        return False



def find_water_year_start_twoseasons(times_input,year_length):
    """
    This function finds the start and end of the water year
    The method used is decribed in Dunning et al. (submitted)
    It uses the numpy library
    'timeseries' should be one dimensional and be a multiple of year_length long
    Leap days should have already been removed
    Start is returned and is in the range 0-year_length-1 
    End is also returned and is in the range 0-730
    This algorithm searches for two wet seasons in each year
    This algorithm has been modified so that it finds the peaks and troughs
    It then identifies the longest season based on this.
    It does not work if there are NaNs in the data
    If the method fails to identify two seasons than NaNs will be returned for the second start/end
    """

    # Cap timeseries
    times = times_input.copy()
    #times[np.where(times>30.0)] = 30.0

    # Check it is a multiple of year_length long
    length = len(times)
    if length%year_length != 0:
        raise ValueError('The timeseries must be a multiple of year_length long. Please try again')

    # Make a copy of the timeseries to ensure no overwriting is occuring
    timeseries=times.copy()

    # Find alpha
    # This is the daily mean over all the data
    alpha = np.mean(timeseries)

    # Use this to test and see if there are any nans in the data
    if math.isnan(alpha):
        raise ValueError('The timeseries contains NaNs. Please remove and try again')

    # Find beta
    # This is the climatological daily mean rainfall on each day of the calendar year
    beta = np.zeros(year_length)
    for day in np.arange(year_length):
        beta[day] = np.mean(timeseries[day::year_length])

    # Find beta - alpha
    # This is the climatological daily mean rainfall anomaly
    bma = beta - alpha
    gamma = bma.copy()

    # Sum
    # Gamma is then the cumulative climatological daily mean rainfall anomaly
    for day in np.arange(year_length):  
        gamma[day] = np.sum(bma[0:day+1])


    # Use alternative method for bimodal seasons
    # First use multiple months on each end to ensure seasons over the calendar year end are captured
    # Then take the moving average 
    gamma_curve    = np.concatenate((gamma[-50:],gamma, gamma[0:85]))
    smoothed_gamma = MovingAverage(gamma_curve, 31)
    # Use the functions above to identify min and max in the data
    maxs = [] 
    mins = [] 
    for point in np.arange(4,len(smoothed_gamma)-4):
        if is_it_max(smoothed_gamma, point) == True:
            maxs.append(point)
        if is_it_min(smoothed_gamma, point) == True:
            mins.append(point)

    # For each min find the max following it
    # The first max following each min is assumed to end that season
    # These are then stored in pairs
    pairs = []
    lengths = []
    for m in mins:
        loc = np.where(maxs>m)
        try:
            pairs.append([m, maxs[loc[0][0]]] )
            lengths.append(maxs[loc[0][0]]-m)
        except: # This means there is no max after that min
            continue

    # Plot to test
    #plt.figure()
    #plt.plot(np.arange(year_length), gamma, 'g', lw=2)
    #plt.plot(np.arange(year_length), smoothed_gamma[35:-70], 'indigo', lw=2)
    #dates = np.concatenate((np.arange(year_length-50+15,year_length), np.arange(0,1000)))
    #for m in mins:
    #    plt.plot([dates[m]],[smoothed_gamma[m]], 'dodgerblue', marker='o', ms=20)
    #for m in maxs:
    #    plt.plot([dates[m]],[smoothed_gamma[m]], 'r',marker='o', ms=20 )
    #plt.xlabel('Day of the year')
    #plt.ylabel('Cumulative daily mean rainfall anomaly (mm)')
    #plt.xlim([0,year_length])
    #plt.show()

    # Find the day of the year corresponding to the mins and max
    # The longest season is considered first
    # Then the second longest season
    # If two seasons are not found due to insifficent max/mins then the except part is used
    try:
        dates = np.concatenate((np.arange(year_length-50+15,year_length), np.arange(0,year_length+85-15)))
        longest = np.argsort(lengths)[-1]
        slongest = np.argsort(lengths)[-2]
        start11 = dates[pairs[longest][0]]
        end11 = dates[pairs[longest][1]]
        start22 = dates[pairs[slongest][0]]
        end22 = dates[pairs[slongest][1]]
        # If two seasons have used the same end then try again
        # The longer version is kept and the next is tried
        # If they all have the same end then NaNs are returned
        iterr = 0
        while (int(end22)==int(end11) or int(end22)==int(end11)+year_length or int(end22)+year_length==int(end11)) and iterr<len(lengths)-2:
            tlongest = np.argsort(lengths)[-3-iterr]
            start22 = dates[pairs[tlongest][0]]
            end22 = dates[pairs[tlongest][1]]
            iterr+=1
        if (int(end22)==int(end11) or int(end22)==int(end11)+year_length or int(end22)+year_length==int(end11)) and iterr == len(lengths)-2:
            start22 = float('nan')
            end22 = float('nan')

    # This means that two seasons were not returned initially and added to pairs
    # All the maxs have year_length added to ensure that all possible pairs have been considered
    # The seasons are then looked for in the same way
    except:
        dates = np.concatenate((np.arange(year_length-50+15,year_length), np.arange(0,1000)))
        if len(lengths)==0:
            nmax = []
            for m in maxs:
                nmax.append(m)
                nmax.append(m+year_length)
            maxs = np.sort(nmax)
        for m in mins:
            loc = np.where(maxs>m)
            try:
                pairs.append([m, maxs[loc[0][0]]] )
                lengths.append(maxs[loc[0][0]]-m)
            except:
                continue

        if len(lengths)>1: # More than one season found
            longest = np.argsort(lengths)[-1]
            slongest = np.argsort(lengths)[-2]
            start11 = dates[pairs[longest][0]]
            end11 = dates[pairs[longest][1]]
            start22 = dates[pairs[slongest][0]]
            end22 = dates[pairs[slongest][1]]
            # If two seasons have used the same end then try again
            # The longer version is kept and the next is tried
            # If they all have the same end then NaNs are returned
            iterr = 0
            while (int(end22)==int(end11) or int(end22)==int(end11)+year_length or int(end22)+year_length==int(end11)) and iterr<len(lengths)-2:
                tlongest = np.argsort(lengths)[-3-iterr]
                start22 = dates[pairs[tlongest][0]]
                end22 = dates[pairs[tlongest][1]]
                iterr+=1
            if (int(end22)==int(end11) or int(end22)==int(end11)+year_length or int(end22)+year_length==int(end11)) and iterr == len(lengths)-2:
                start22 = float('nan')
                end22 = float('nan')

        elif len(lengths)==1: # One season found
            longest = np.argsort(lengths)[-1]
            start11 = dates[pairs[longest][0]]
            end11 = dates[pairs[longest][1]]
            start22 = float('nan')
            end22 = float('nan')
        else:
            start22 = float('nan')
            end22 = float('nan')
            start11 = float('nan')
            end11 = float('nan')
   
    # Add year_length if start is after the end (should not be due to method)
    if start11>end11:
        end11 = end11+year_length
    if start22>end22:
        end22 = end22+year_length

    # Check one season is not the same as previous  (+_ year_length)
    # It should not be due to the method used, but just to check. 
    if np.abs(start22-start11)<year_length+3 and np.abs(start22-start11)>year_length-3:

        #season 2 is season 1+- year_length
        print 'year_length different: ',start22,start11
        if start11<year_length:
            start22=np.nan
            end22=np.nan
        else: 
            start11=start22
            end11 = end22
            start22=np.nan
            end22=np.nan

    # Return
    return start11,end11,start22,end22


