#!/usr/bin/env python
# -*- coding: utf-8 -*-

class acceptance_tester:
    """
    Tests data points for acceptance into dataset_container
    """

    def __init__(self, tester_type):
        """
        Initialize with the type of data to test.
        """
        self._tester_map = {'heartrate': self._test_heartrate,
                            'intensity': self._test_intensity,
                            'steps': self._test_steps}
        self._tester = self._tester_map.get(tester_type, self._test_accept_all)
    
    def __call__(self, datapoint):
        """
        Pass a datapoint to test, returns acceptance based on the type set.
        """
        return self._tester(datapoint)
        
    def _test_accept_all(self, datapoint):
        """
        Accept all datapoints.
        """
        return True
    
    def _test_heartrate(self, datapoint):
        """
        Test HR datapoints for acceptance. Do not accept values that match the 
        following:
            - HR == 255
            - HR <= 0
        """
        return not datapoint.value == 255 and not datapoint.value <= 0
        
    def _test_intensity(self, datapoint):
        """
        Test intensity datapoints for acceptance. Do not accept values that 
        match the following:
            - intensity == 255
        """
        return not datapoint.value == 255

    def _test_steps(self, datapoint):
        """
        Test step datapoints for acceptance. Do not accept values that match 
        the following:
            - steps < 0
        """
        return not datapoint.value < 0

class dataset_filter:
    """
    A class providing dataset filtering. 
    """
    
    def __init__(self):
        """
        initialize the filters.
        """
        self._filter_map = {'heartrate': self._filter_hr}
        self._filter_params = {}
        self._filters = []
        
    def add_filter(self, filtername, **kwargs):
        """
        Add a filter to be applied to the dataset. The first parameter selects
        the filter type, any other parameters must be named and will be stored
        and passed to the filter function as parameters.
        """
        if filtername in self._filter_map and not filtername in self._filters:
            self._filters.append(filtername)
            self._filter_params[filtername] = kwargs
    
    def __call__(self, timestamps, values):
        """
        Apply the filters that have been set up for this provider to the dataset
        passed and return the resulting dataset.
        """
        for filtername in self._filters:
            timestamps, values = self._filter_map[filtername](timestamps, values, 
                                                              **self._filter_params[filtername])
        return timestamps, values
    
    def count(self):
        """
        Returns the number of filter functions applied to data
        """
        return len(self._filters)
    
    def _filter_hr(self, timestamps, values, delta_doublefilter=3, **kwargs):
        """
        A heartrate-specific filter. It checks if a value is twice as high as
        the ones preceding and following it, within the delta_doublefilter 
        environment, and divides the values matching by two. 
        """
        from numpy import arange
        for i in arange(1, len(values) - 1):
            diff_lower = abs((float(values[i])/2.) - values[i - 1])
            diff_upper = abs((float(values[i])/2.) - values[i + 1])
            if (diff_lower < delta_doublefilter)*\
              (diff_upper < delta_doublefilter):
                values[i] /= 2.
        return timestamps, values
        