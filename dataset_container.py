#!/usr/bin/env python
# -*- coding: utf-8 -*-

class dataset_container:
    """
    Contains one single dataset. Holds a list of datapoint instances describing
    the actual data. Depending on the name the dataset was initialized with, 
    processing is performed to reject invalid data when appending new points.
    """
    
    def __init__(self, dataset_type, **kwargs):
        """
        Initialize the dataset with the _type. Type selects processing for 
        valid data when appending points.
        """
        from datetime import timedelta
        from filter_provider import dataset_filter, acceptance_tester
        self._type = dataset_type
        self._datapoints = []
        self._index = 0
        if 'time_resolution' in kwargs:
            self._time_resolution = kwargs['time_resolution']
        else:
            self._time_resolution = timedelta(minutes=1)
        self._accept = acceptance_tester(self._type)
        self._filters = dataset_filter()
        self._filtered_data = None
        
    def add_filter(self, filter_type, **kwargs):
        """
        Add a new filter to the filter provider. filter_type selects the filter
        that will be applied, any other parameter must be named and will be 
        passed to the actual filter function.
        """
        self._filters.add_filter(filter_type, **kwargs)
        self._filtered_data = None
        #This is done to update self._filtered_data:
        timestamps = self['timestamps']
        values = self['values']

    def append(self, timestamp, value):
        """
        Append a datapoint(timestamp, value) to the dataset. Depending on the
        _type, checks for validity are performed, and if invalid, the data point
        may be rejected.
        """
        dp = datapoint(timestamp, value)
        if self._accept(dp):
            self._datapoints.append(dp)

    def __getitem__(self, item):
        """
        Return list of timestamps when called with 'timestamps' or 0, and 
        list of values when called with 'values' or 1.
        """
        from numpy import array
        if self._filtered_data is None:
            timestamps, values = [], []
            for point in self._datapoints:
                timestamps.append(point.timestamp)
                values.append(point.value)
            timestamps, values = self._filters(array(timestamps), 
                                                array(values))
            self._filtered_data = {'timestamps': timestamps, 'values': values}
        else:
            timestamps = self._filtered_data['timestamps']
            values = self._filtered_data['values']
        if item == 'timestamps' or item == 0:
            return timestamps
        elif item == 'values' or item == 1:
            return values
        else:
            raise IndexError('Invalid index')
    
    def __iter__(self):
        """
        Return self as iterator
        """
        return self
    
    def next(self):
        """
        Iterate to the next datapoint in the list.
        """
        if self._index < len(self._datapoints):
            self._index += 1
            return self._datapoints[self._index - 1]
        else:
            self._index = 0
            raise StopIteration
    
    def time_resolution(self, value = None):
        """
        Manage the datasets time resolution. If called without a value, return
        the current time resolution. If a value is passed, it is set as the new
        time resolution. The value must be >= 1 min, or an error will be 
        raised.
        """
        from datetime import timedelta
        if not value is None:
            if value < timedelta(minutes=1):
                raise ValueError('Time resolution cannot be lower than 1 min.')
            else:
                self._time_resolution = value
        else:
            return self._time_resolution
    
    def timestamp_start(self):
        """
        Return first timestamp for the dataset.
        """
        return min(self['timestamps'])
    
    def timestamp_end(self):
        """
        Return last timestamp for the dataset.
        """
        return max(self['timestamps'])
    
    def timerange(self):
        """
        Return the timerange [start, end] of the dataset as a list.
        """
        return [self.timestamp_start(), self.timestamp_end()]
    
    def _downsample_data(self, func):
        """
        Arbitrary downsample function. Pass a callable that performs the actual
        downsampling. func should accept an array of values and return a single
        number. 
        """
        from numpy import array
        from plotting import plotter
        cur_time = self.timestamp_start()
        res_timestamps = []
        res_values = []
        while(cur_time <= self.timestamp_end()):
            sliced_data = self._timeslice_data(cur_time, cur_time + 
                                                self.time_resolution())
            val = func(sliced_data['values'])
            res_timestamps.append(cur_time)
            res_values.append(val)
            cur_time += self.time_resolution()
        return plotter(self._type, timestamps=array(res_timestamps), 
                       values=array(res_values))
    
    def downsample_mean(self):
        """
        Downsample data using the Numpy mean function.
        """
        from numpy import mean
        return self._downsample_data(mean)
    
    def downsample_median(self):
        """
        Downsample data using the Numpy median function.
        """
        from numpy import median
        return self._downsample_data(median)
    
    def downsample_histogram(self, hist_min=None, hist_max=None, 
                             resolution=5):
        from numpy import array, arange, amin, amax, histogram
        from plotting import plotter
        if hist_min is None:
            #Take the minimum, round to nearest 10
            hist_min = int(amin(self['values'])/10)*10
        if hist_max is None:
            #Take the maximum, round to nearest 10
            hist_max = int(amax(self['values'])/10)*10
        bins = arange(hist_min, hist_max, resolution)
        cur_time = self.timestamp_start()
        res_timestamps = []
        res_histogram = []
        while(cur_time <= self.timestamp_end()):
            sliced_data = self._timeslice_data(cur_time, cur_time + 
                                                self.time_resolution())
        
            hist = histogram(sliced_data['values'], bins, density=True)[0]
            res_timestamps.append(cur_time)
            res_histogram.append(hist)
            cur_time += self.time_resolution()
        res_timestamps.append(self.timestamp_end())
        return plotter(self._type, timestamps=array(res_timestamps), bins=bins, 
                       histogram=array(res_histogram))

    def downsample_sum(self):
        """
        Downsample data using the Numpy sum function.
        """
        from numpy import sum
        return self._downsample_data(sum)
    
    def downsample_none(self):
        """
        Don't downsample, just return full-resolution data as saved in the 
        dataset.
        """
        from numpy import array
        from plotting import plotter
        res_timestamps = self['timestamps'] 
        res_values = self['values']
        return plotter(self._type, timestamps=array(res_timestamps), 
                       values=array(res_values))
    
    def _timeslice_data(self, timestamp_start, timestamp_end):
        """
        Helper function to perform the actual time slicing common to
        downsampling.
        """
        from numpy import array, column_stack
        timestamps = array(self['timestamps']) 
        values = array(self['values'])
        mask = (timestamps >= timestamp_start)*(timestamps < timestamp_end)
        res = dataset_container(self._type)
        res.time_resolution(value=self.time_resolution())
        for timestamp, value in column_stack((timestamps[mask], values[mask])):
            res.append(timestamp, value)
        return res
        
class datapoint:
    """
    Container for a single data point. Holds datapoint.timestamp and 
    datapoint.value. Is iterable to allow for timestamp, value = datapoint 
    assignments.
    """
    
    def __init__(self, timestamp, value):
        """
        Initialize the datapoint. Pass a timestamp and a value to hold.
        """
        self.timestamp = timestamp
        self.value = value
        self._index = 0
        
    def __iter__(self):
        """
        Return self as iterator.
        """
        return self
    
    def next(self):
        """
        Iterate over the values. First iteration yields timestamp, second
        iteration yields value.
        """
        if self._index == 0:
            self._index += 1
            return self.timestamp
        elif self._index == 1:
            self._index += 1
            return self.value
        else:
            self._index = 0
            raise StopIteration
        