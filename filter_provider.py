#!/usr/bin/env python
# -*- coding: utf-8 -*-

class acceptance_tester:
    """Tests data points for acceptance into dataset_container."""

    def __init__(self, tester_type):
        """Initialize with the type of data to test.
        
        Parameters
        ----------
            tester_type : string
                The type of data that validity should be tested for.
        
        Returns
        -------
            None
        """
        self._tester_map = {'heartrate': self._test_heartrate,
                            'intensity': self._test_intensity,
                            'steps': self._test_steps}
        self._tester = self._tester_map.get(tester_type, self._test_accept_all)
    
    def __call__(self, datapoint):
        """Pass a datapoint to test, returns acceptance based on the type set.
        
        Parameters
        ----------
            datapoint : datapoint
                The datapoint to test for acceptance
        
        Returns
        -------
            bool
                Whether or not the value is valid.
        """
        return self._tester(datapoint)
        
    def _test_accept_all(self, datapoint):
        """Accept all datapoints.
        
        Parameters
        ----------
            datapoint : datapoint
                The datapoint being tested.
        
        Returns
        -------
            True
                This function always returns True to accept all data points.
        """
        return True
    
    def _test_heartrate(self, datapoint):
        """Test HR datapoints for acceptance. Do not accept values that match 
        the following:
            * HR == 255
            * HR <= 0
        
        Parameters
        ----------
            datapoint : datapoint
                The datapoint to test for acceptance
        
        Returns
        -------
            bool
                Whether or not the value is valid.
        """
        return not datapoint.value >= 255 and not datapoint.value <= 0
        
    def _test_intensity(self, datapoint):
        """Test intensity datapoints for acceptance. Do not accept values that 
        match the following:
            * intensity == 255
        
        Parameters
        ----------
            datapoint : datapoint
                The datapoint to test for acceptance
        
        Returns
        -------
            bool
                Whether or not the value is valid.
        """
        return not datapoint.value >= 255

    def _test_steps(self, datapoint):
        """Test step datapoints for acceptance. Do not accept values that match 
        the following:
            * steps < 0
        
        Parameters
        ----------
            datapoint : datapoint
                The datapoint to test for acceptance
        
        Returns
        -------
            bool
                Whether or not the value is valid.
        """
        return not datapoint.value < 0

class dataset_filter:
    """A class providing dataset filtering."""
    
    def __init__(self):
        """Initialize the filters.
        
        Parameters
        ----------
            None
        
        Returns
        -------
            None
        """
        self._filter_map = {'heartrate': self._filter_hr}
        self._filter_params = {}
        self._filters = []
        
    def add_filter(self, filtername, **kwargs):
        """Add a filter to be applied to the dataset. The first parameter 
        selects the filter type, any other parameters must be named and will be 
        stored and passed to the filter function as parameters.
        
        Parameters
        ----------
            filtername : string
                The name of the filter to add.
            kwargs : dict
                Any other named parameters will be stored and passed to the 
                filter when it is called.
        
        Returns
        -------
            None
        """
        if filtername in self._filter_map and not filtername in self._filters:
            self._filters.append(filtername)
            self._filter_params[filtername] = kwargs
    
    def __call__(self, timestamps, values):
        """Apply the filters that have been set up for this provider to the 
        dataset passed and return the resulting dataset.
        
        Parameters
        ----------
            timestamps : numpy.array
                The timestamps of the data to be filtered
            values : numpy.array
                The values of the data to be filtered
        """
        for filtername in self._filters:
            timestamps, values = self._filter_map[filtername](timestamps, values, 
                                                              **self._filter_params[filtername])
        return timestamps, values
    
    def count(self):
        """Returns the number of filter functions applied to data.
        
        Parameters
        ----------
            None
        
        Returns
            int
                The number of filters stored
        """
        return len(self._filters)
    
    def _filter_hr(self, timestamps, values, delta_doublefilter=3):
        """A heartrate-specific filter. It checks if a value is twice as high as
        the ones preceding and following it, within the delta_doublefilter 
        environment, and divides the values matching by two.
        
        Parameters
        ----------
            timestamps : numpy.array
                The timestamps of the data to be filtered
            values : numpy.array
                The values of the data to be filtered
            delta_doublefilter : int
                The delta around double the value of a heartrate value for which
                the filter will still be applied.
        
        Returns
        -------
            None
        """
        from numpy import arange
        for i in arange(1, len(values) - 1):
            diff_lower = abs((float(values[i])/2.) - values[i - 1])
            diff_upper = abs((float(values[i])/2.) - values[i + 1])
            if (diff_lower < delta_doublefilter)*\
              (diff_upper < delta_doublefilter):
                values[i] /= 2.
        return timestamps, values
        