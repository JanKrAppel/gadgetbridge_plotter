#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..filter_provider import dataset_filter
from numpy import array

def test_addition():
    """Test adding a valid filter to the dataset_filter class. The filter should
    get added.
    """
    ds_filter = dataset_filter()
    ds_filter.add_filter('heartrate')
    assert len(ds_filter._filters) == 1 and ds_filter._filters[0] == 'heartrate'

def test_invalid_addition():
    """Test adding an invalid filter to the dataset_filter class. The filter 
    should not be added.
    """
    ds_filter = dataset_filter()
    ds_filter.add_filter('not defined as filter name')
    assert len(ds_filter._filters) == 0

def test_double_addition():
    """Test adding the same filter twice to the dataset_filter class. Expected
    behaviour is that the filter only gets added once.
    """
    ds_filter = dataset_filter()
    ds_filter.add_filter('heartrate')
    ds_filter.add_filter('heartrate')
    assert len(ds_filter._filters) == 1
    
def test_get_count():
    """Test returning the number of filters from dataset_filter.get_count()."""
    ds_filter = dataset_filter()
    assert ds_filter.count() == 0
    assert ds_filter.count() == len(ds_filter._filters)
    ds_filter.add_filter('heartrate')
    assert ds_filter.count() == len(ds_filter._filters)
    assert ds_filter.count() == 1

def test_param_passing():
    """Test passing parameters to filters. The parameters should be stored 
    correctly in the dataset_filter._filter_params dictionary.
    """
    ds_filter = dataset_filter()
    ds_filter.add_filter('heartrate')
    assert len(ds_filter._filter_params) == 1
    assert len(ds_filter._filter_params['heartrate'].keys()) == 0
    ds_filter = dataset_filter()
    ds_filter.add_filter('heartrate', test_param=1)
    assert len(ds_filter._filter_params) == 1
    assert len(ds_filter._filter_params['heartrate'].keys()) == 1
    assert ds_filter._filter_params['heartrate']['test_param'] == 1

def test_heartrate_filter():
    """Test the function of the heartrate filter."""
    ds_filter = dataset_filter()
    ds_filter.add_filter('heartrate')    
    test_times = array((1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
    test_values = array((50, 52, 51, 101, 53, 52, 50, 106, 51, 52))
    res_times, res_values = ds_filter(test_times, test_values)
    assert (test_times == res_times).all()
    assert (res_values == array((50, 52, 51, 50, 53, 52, 50, 106, 51, 52))).all()

def test_no_filter():
    """Test that no filter returns the dataset unmodified."""
    ds_filter = dataset_filter()
    test_times = array((1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
    test_values = array((50, 52, 51, 101, 53, 52, 50, 106, 51, 52))
    res_times, res_values = ds_filter(test_times, test_values)
    assert (test_times == res_times).all()
    assert (test_values == res_values).all()
