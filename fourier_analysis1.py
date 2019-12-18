# This code calculates the power spectrum of a given time series
# A function is created that computes and plots it.
# This function includes options for detrending

# Import the necessary libraries
import matplotlib.pyplot as plt
import numpy as np 
import scipy.fftpack as fftp
import scipy.signal as ss


# Define the function which will do fourier analysis
def fourier_analysis(time_series, length, detrend=False, dt=1.0/12.0):
    """ This function performs fourier analysis of a time series
    The time_series is a 1D array containing points at every time step
    Length determines the length of the array to be output i.e. are we using zero-padding
    If detrend is set to True then the data will be detrended before fourier analysis is applied
    The value detrend is set to determines the order of the polynomial removed
    dt is the time step between each point.
    Power spectra is a plot of mag against freqs """

    # Detrend the data as necessary
    if detrend != False:
        t = np.arange(len(time_series))
        p = np.polyfit(t,time_series, detrend)
        pv = np.polyval(p,t)
        time_series = time_series - pv
    
    # Divide by the standard deviation
    time_series = time_series/np.std(time_series)

    # FFT procedure
    F = np.fft.fft(time_series, n=length)
    N = length
    w = np.fft.fftfreq(N, dt)
 
    # Focus on positive frequencies
    ind_pos = np.where(w>=0)
    freqs = w[ind_pos]
    mag = np.abs(F[ind_pos])/N
    phase = np.angle(F[ind_pos])  

    # Return freqs, mag, phase
    return freqs, mag, phase




    
