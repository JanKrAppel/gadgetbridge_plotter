#!/usr/bin/env python
# -*- coding: utf-8 -*-
from numpy import array, arange, amin, amax, histogram
from numpy import column_stack, median, mean, sum
from plotting import Plotter
from datetime import timedelta
from filter_provider import DatasetFilter, AcceptanceTester

class DatasetContainer:
    """Contains one single dataset. Holds a list of Datapoint instances 
    describing the actual data. Depending on the name the dataset was 
    initialized with, processing is performed to reject invalid data when 
    appending new points."""
    
    def __init__(self, dataset_type, time_resolution=timedelta(minutes=1),
                 filter_provider=DatasetFilter, plotter=Plotter):
        """Initialize the dataset with the dataset_type. Type selects 
        processing for valid data when appending points.
        
        Parameters
        ----------
            dataset_type : string
                The dataset type.
            time_resolution : datetime.timedelta
                The time resolution of the dataset.
                (Default: timedelta(minutes=1))
            filter_provider : class
                A class providing data filters to the container. Must be 
                callable to apply the filters, and expose an add_filter and 
                count method.
            plotter : class
                A class providing plotting functionality. Must expose a plot 
                method.
        
        Returns
        -------
            None
        """
        self._type = dataset_type
        self._raw_datapoints = []
        self._index = 0
        self._time_resolution = time_resolution
        self._accept = AcceptanceTester(self._type)
        if hasattr(filter_provider, 'add_filter') \
            and hasattr(filter_provider, 'count') \
            and callable(filter_provider.add_filter) \
            and callable(filter_provider.count) \
            and callable(filter_provider):
            self._filters = filter_provider()
        else:
            raise ValueError('Got an invalid filter provider')
        if hasattr(plotter, 'plot') and callable(plotter.plot):
            self._plotter = plotter
        else:
            raise ValueError('Got an invalid plotter')
        self._data_up_to_date = True
        self._update_filtered_data()
        
    def add_filter(self, filter_type, **kwargs):
        """Add a new filter to the filter provider. filter_type selects the 
        filter that will be applied, any other parameter must be named and will
        be passed to the actual filter function. When adding a filter, the 
        cached DatasetContainer._filtered_data is updated.
        
        Parameters
        ----------
            filter_type : string
                The filter type to add.
            kwargs : dict
                Any other named parameters will be stored in the kwargs dict
                and passed to the filter function when it gets called.

        Returns
        -------
            None
        """
        self._filters.add_filter(filter_type, **kwargs)
        self._data_up_to_date = False

    def append(self, timestamp, value):
        """Append a Datapoint(timestamp, value) to the dataset. Depending on the
        type, checks for validity are performed, and if invalid, the data point
        may be rejected.
        
        Parameters
        ----------
            timestamp : datetime
                The timestamp of the Datapoint
            value : int, float
                The value to store
        
        Returns
        -------
            None
        """
        dp = Datapoint(timestamp, value)
        if self._accept(dp):
            self._raw_datapoints.append(dp)
            self._data_up_to_date = False

    def __getitem__(self, item):
        """Return list of timestamps when called with 'timestamps' or 0, and 
        list of values when called with 'values' or 1. If any other value is
        passed, an IndexError is raised.
        
        Parameters
        ----------
            item : string or int
                The item name or index of the item to retrieve.
        
        Returns
        -------
            numpy.array
                Depending on the selected item, an array containing the 
                timestamps or values stored in the container are returned. 
        """
        if not self._data_up_to_date:
            self._update_filtered_data()
            self._data_up_to_date = True
        if item == 'timestamps' or item == 0:
            return self._filtered_data['timestamps']
        elif item == 'values' or item == 1:
            return self._filtered_data['values']
        else:
            raise IndexError('Invalid index')
    
    def _update_filtered_data(self):
        """Update the filtered data cache from the raw datapoints.
        
        Parameters
        ----------
            None
            
        Returns
        -------
            None
        """
        timestamps, values = [], []
        for point in self._raw_datapoints:
            timestamps.append(point.timestamp)
            values.append(point.value)
        timestamps, values = self._filters(array(timestamps), 
                                            array(values))
        self._filtered_data = {'timestamps': timestamps, 'values': values}
    
    def __iter__(self):
        """Return self as iterator.
        
        Parameters
        ----------
            None
        
        Returns
        -------
            self : DatasetContainer
        """
        return self
    
    def next(self):
        """Iterate to the next Datapoint in the list.
        
        Parameters
        ----------
            None
        
        Returns
        -------
            Datapoint
                The next Datapoint in the container
        """
        if self._index < len(self._raw_datapoints):
            self._index += 1
            return self._raw_datapoints[self._index - 1]
        else:
            self._index = 0
            raise StopIteration
    
    def time_resolution(self, value = None):
        """Manage the datasets time resolution. If called without a value, 
        return the current time resolution. If a value is passed, it is set as 
        the new time resolution. The value must be >= 1 min, or an error will 
        be raised.
        
        Parameters
        ----------
            value : datetime.timedelta, None
                The new time resolution to set, or None to return the current
                time resolution only.
        
        Returns
        -------
            _time_resolution : datetime.timedelta
                The time resolution of the dataset after the function finishes
        """
        if not value is None:
            if value < timedelta(minutes=1):
                raise ValueError('Time resolution cannot be lower than 1 min.')
            else:
                self._time_resolution = value
            return self._time_resolution
        else:
            return self._time_resolution
    
    def timestamp_start(self):
        """Return first (chronological) timestamp for the dataset.
        
        Parameters
        ----------
            None
        
        Returns
        -------
            datetime.datetime
                The earliest timestamp stored in the dataset
        """
        return min(self['timestamps'])
    
    def timestamp_end(self):
        """Return last (chronological) timestamp for the dataset.
        
        Parameters
        ----------
            None
        
        Returns
        -------
            datetime.datetime
                The latest timestamp stored in the dataset
        """
        return max(self['timestamps'])
    
    def timerange(self):
        """Return the timerange [start, end] of the dataset as a list.
        
        Parameters
        ----------
            None
        
        Returns
        -------
            list
                A list containing the earliest and the latest timestamp in the 
                dataset.
        """
        return [self.timestamp_start(), self.timestamp_end()]
    
    def _downsample_data(self, func):
        """Arbitrary downsample function. Pass a callable that performs the actual
        downsampling. func should accept an array of values and return a single
        number.
        
        Parameters
        ----------
            func : callable
                The downsample function to apply. func should accept numpy.array
                and return a single float or int.
        
        Returns
        -------
            class
                A class that provides plotting of the data set.
        """
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
        return self._plotter(self._type, timestamps=array(res_timestamps), 
                             values=array(res_values))
    
    def downsample_mean(self):
        """Downsample data using the Numpy mean function.

        Parameters
        ----------
            None
        
        Returns
        -------
            class
                A class that provides plotting of the data set.
        """
        return self._downsample_data(mean)
    
    def downsample_median(self):
        """Downsample data using the Numpy median function.

        Parameters
        ----------
            None
        
        Returns
        -------
            class
                A class that provides plotting of the data set.
        """
        return self._downsample_data(median)
    
    def downsample_sum(self):
        """Downsample data using the Numpy sum function.

        Parameters
        ----------
            None
        
        Returns
        -------
            class
                A class that provides plotting of the data set.
        """
        return self._downsample_data(sum)
    
    def downsample_none(self):
        """Don't downsample, just return full-resolution data as saved in the 
        dataset.

        Parameters
        ----------
            None
        
        Returns
        -------
            class
                A class that provides plotting of the data set.
        """
        res_timestamps = self['timestamps'] 
        res_values = self['values']
        return self._plotter(self._type, timestamps=array(res_timestamps), 
                             values=array(res_values))
    
    def downsample_histogram(self, hist_min=None, hist_max=None, 
                             resolution=5):
        """Downsample the data into a 2D histogram of values, where the time
        resolution of the histogram is that of the dataset. I.e., each histogram
        timestemp will contain a 1D histogram of values occuring in that 
        timestep in the dataset.

        Parameters
        ----------
            hist_min : float, None
                The minimal value of the histogram. If None is passed, it is 
                computed dynamically.
                (Default: None)
            hist_max : float, None
                The maximum value of the histogram. If None is passed, it is 
                computed dynamically.
                (Default: None)
            resolution : float
                The bin width of the histogram.
                (Default: 5)
        
        Returns
        -------
            class
                A class that provides plotting of the data set.
        """
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
            #Scale the maximum of each histogram row to 1:
            res_histogram.append(hist/amax(hist))
            cur_time += self.time_resolution()
        res_timestamps.append(self.timestamp_end())
        return self._plotter(self._type, timestamps=array(res_timestamps), 
                             bins=bins, histogram=array(res_histogram))

    def _timeslice_data(self, timestamp_start, timestamp_end):
        """Helper function to perform the actual time slicing common to
        downsampling. Returns a DatasetContainer with the data for which
        timestamp_start <= timestamp < timestamp_end.

        Parameters
        ----------
            timestamp_start : datetime.datetime
                The earliest timestamp to include
            timestamp_end : datetime.datetime
                The first timestamp to exclude
        
        Returns
        -------
            res : DatasetContainer
                A container with the data between the start and end values.
        """
        timestamps = array(self['timestamps']) 
        values = array(self['values'])
        mask = (timestamps >= timestamp_start)*(timestamps < timestamp_end)
        res = DatasetContainer(self._type)
        res.time_resolution(value=self.time_resolution())
        for timestamp, value in column_stack((timestamps[mask], values[mask])):
            res.append(timestamp, value)
        return res
        
class Datapoint:
    """Container for a single data point. Holds Datapoint.timestamp and 
    Datapoint.value. Is iterable to allow for timestamp, value = Datapoint 
    assignments."""
    
    def __init__(self, timestamp, value):
        """Initialize the Datapoint. Pass a timestamp and a value to hold.
        
        Parameters
        ----------
            timestamp : datetime.datetime
                The timestamp of the data point
            value : float
                The value of the data point
        """
        self.timestamp = timestamp
        self.value = value
        self._index = 0
        
    def __iter__(self):
        """Return self as iterator.
        
        Parameters
        ----------
            None
        
        Returns
        -------
            self : Datapoint
                This instance of Datapoint
        """
        return self
    
    def next(self):
        """Iterate over the values. First iteration yields timestamp, second
        iteration yields value.
        
        Parameters
        ----------
            None
        
        Returns
        -------
            datetime.datetime, float
                Returns the timestamp on the first iteration, the value on the
                second one.
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
        