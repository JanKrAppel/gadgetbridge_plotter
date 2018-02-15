#!/usr/bin/env python
# -*- coding: utf-8 -*-

class line_plotter:
    """
    A class that creates a plot for line data.
    """
    
    def __init__(self, dataset_type, timestamps, values):
        """
        Initialize the plotter. Pass the dataset type, and an array of 
        timestamps and values of equal length. The dataset type is used as a
        Y axis label on the plot.
        """
        self.__type = dataset_type
        self.__timestamps = timestamps
        self.__values = values
    
    def plot(self):
        """
        Plot the data stored in the class.
        """
        from matplotlib import pyplot as plt
        from numpy import amin, amax
        plt.plot(self.__timestamps, self.__values)
        plt.ylabel(self.__type)
        plt.xlim(amin(self.__timestamps), amax(self.__timestamps))
        plt.grid()

class hist_plotter:
    """
    A class that creates a plot for histogram data.
    """
    
    def __init__(self, dataset_type, timestamps, bins, histogram):
        
        self.__type = dataset_type
        self.__timestamps = timestamps
        self.__bins = bins
        self.__histogram = histogram
    
    def plot(self):
        """
        Plot the data stored in the class.
        """
        from matplotlib import pyplot as plt
        from numpy import amin, amax
        plt.pcolormesh(self.__timestamps, self.__bins, self.__histogram.T)
        plt.xlim(amin(self.__timestamps), amax(self.__timestamps))
        plt.ylabel(self.__type + ' histogram')