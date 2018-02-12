#!/usr/bin/env python
# -*- coding: utf-8 -*-

class dataset_container:
    """
    Contains one single dataset. Holds a list of datapoint instances describing
    the actual data. Depending on the name the dataset was initialized with, 
    processing is performed to reject invalid data when appending new points.
    """
    
    def __init__(self, type, **kwargs):
        """
        Initialize the dataset with the type. Type selects processing for 
        valid data when appending points.
        """
        from datetime import timedelta
        self.type = type
        self.datapoints = []
        self.__index = 0
        if 'time_resolution' in kwargs:
            self.__time_resolution = kwargs['time_resolution']
        else:
            self.__time_resolution = timedelta(minutes=1)

    def append(self, timestamp, value):
        """
        Append a datapoint(timestamp, value) to the dataset. Depending on the
        type, checks for validity are performed, and if invalid, the data point
        may be rejected.
        """
        self.__postprocess_datapoint(datapoint(timestamp, value))

    def __postprocess_datapoint(self, datapoint):
        """
        Call appropriate postprocessing function for the datapoint.
        """
        if self.type == 'heartrate':
            return self.__postprocess_hr(datapoint)
        elif self.type == 'intensity':
            return self.__postprocess_intensity(datapoint)
        else:
            self.datapoints.append(datapoint)
        
    def __postprocess_hr(self, datapoint):
        """
        Postprocess HR datapoints. Do not append values that match the 
        following:
            - HR == 255
            - HR <= 0
        """
        if not (datapoint.value == 255) + (datapoint.value <= 0):
            self.datapoints.append(datapoint)
        
    def __postprocess_intensity(self, datapoint):
        """
        Postprocess intensity datapoints. Do not append values that match the 
        following:
            - intensity == 255
        """
        if not (datapoint.value == 255):
            self.datapoints.append(datapoint)

    def __getitem__(self, item):
        """
        Return list of timestamps when called with 'timestamps' or 0, and 
        list of values when called with 'values' or 1.
        """
        if item == 'timestamps' or item == 0:
            return [point.timestamp for point in self.datapoints]
        elif item == 'values' or item == 1:
            return [point.value for point in self.datapoints]
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
        if self.__index < len(self.datapoints):
            self.__index += 1
            return self.datapoints[self.__index - 1]
        else:
            self.__index = 0
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
                self.__time_resolution = value
        else:
            return self.__time_resolution
    
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
        self.__index = 0
        
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
        if self.__index == 0:
            self.__index += 1
            return self.timestamp
        elif self.__index == 1:
            self.__index += 1
            return self.value
        else:
            self.__index = 0
            raise StopIteration
        