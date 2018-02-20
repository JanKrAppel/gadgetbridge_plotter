#!/usr/bin/env python
# -*- coding: utf-8 -*-

class filter_provider:
    """
    A class providing dataset filtering. 
    """
    
    def __init__(self):
        """
        initialize the filters.
        """
        self._filter_params = {}
        self._filters = []
        self._filter_map = {'heartrate': self._filter_hr}
        
    def add_filter(self, filter, **kwargs):
        """
        Add a filter to be applied to the dataset. The first parameter selects
        the filter type, any other parameters must be named and will be stored
        and passed to the filter function as parameters.
        """
        if filter in self._filter_map and not filter in self._filters:
            self._filters.append(filter)
            self._filter_params[filter] = kwargs
    
    def __call__(self, timestamps, values):
        """
        Apply the filters that have been set up for this provider to the dataset
        passed and return the resulting dataset.
        """
        for filter in self._filters:
            timestamps, values = self._filter_map[filter](timestamps, values, 
                                                          **self._filter_params[filter])
        return timestamps, values
    
    def filters_count(self):
        """
        Returns the number of filter functions applied to data
        """
        return len(self._filters)
    
    def _filter_hr(self, timestamps, values, delta_doublefilter=5, **kwargs):
        """
        A heartrate-specific filter. It checks if a value is twice as high as
        the ones preceding and following it, within the delta_doublefilter 
        environment, and divides the values matching by two. 
        """
        from numpy import arange
        for i in arange(1, len(values) - 1):
            diff_lower = abs((values[i]/2.) - values[i - 1])
            diff_upper = abs((values[i]/2.) - values[i + 1])
            if (diff_lower < delta_doublefilter)*\
                (diff_upper < delta_doublefilter):
                values[i] /= 2.
        return timestamps, values
        