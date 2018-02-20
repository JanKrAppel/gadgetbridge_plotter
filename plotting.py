#!/usr/bin/env python
# -*- coding: utf-8 -*-

class plotter:
    """
    A class that creates plots from data.
    """
    
    def __init__(self, dataset_name, **kwargs):
        """
        Initialize the class. Pass the dataset name as first argument. If 
        'timestamps' and 'values' are passed as named arguments, the data is 
        plotted as a line plot. If 'timestamps', 'bins' and 'histogram' are 
        passed, the data is plotted as a histogram plot. An exception is raised
        when other data is passed.
        """
        self._type = dataset_name
        if 'timestamps' in kwargs and 'values' in kwargs:
            self._plotfunc = self._line_plot
            self._timestamps = kwargs['timestamps']
            self._values = kwargs['values']
        elif 'timestamps' in kwargs and 'bins' in kwargs and \
            'histogram' in kwargs:
            self._plotfunc = self._hist_plot
            self._timestamps = kwargs['timestamps']
            self._bins = kwargs['bins']
            self._histogram = kwargs['histogram']
        else:
            raise InvalidArgumentsError('Invalid naming and/or number of ' + \
                                        'arguments')
    
    def plot(self):
        """
        Plot the data stored in the class as the appropriate plot type.
        """
        self._plotfunc()
    
    def _line_plot(self):
        """
        Plot the data stored in the class as a line plot.
        """
        from matplotlib import pyplot as plt
        from numpy import amin, amax
        plt.plot(self._timestamps, self._values)
        plt.ylabel(self._type)
        plt.xlim(amin(self._timestamps), amax(self._timestamps))
        plt.grid()
    
    def _hist_plot(self):
        """
        Plot the data stored in the class as a histogram.
        """
        from matplotlib import pyplot as plt
        from numpy import amin, amax
        plt.pcolormesh(self._timestamps, self._bins, self._histogram.T)
        plt.xlim(amin(self._timestamps), amax(self._timestamps))
        plt.ylabel(self._type + ' histogram')
                
class InvalidArgumentsError(BaseException):
    pass