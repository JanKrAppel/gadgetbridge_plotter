#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..dataset_container import DatasetContainer, Datapoint
from datetime import datetime, timedelta
from numpy import array
import pytest

@pytest.fixture
def dataset_container():
    """Return a default DatasetContainer instance to run tests against. Activity
    as a typeshould not have any filters or acceptance testing associated.
    """
    return DatasetContainer('activity')

def test_add_filter(dataset_container):
    """Test that filters get correctly assigned."""
    dataset_container.add_filter('heartrate')
    assert dataset_container._filters.count() == 1

def test_append(dataset_container):
    """Test that data points get appended correctly."""
    dataset_container.append(datetime(2018, 1, 1, 12, 0, 0), 1)
    assert len(dataset_container._datapoints) == 1
    assert dataset_container._datapoints[0].value == 1 \
        and dataset_container._datapoints[0].timestamp == datetime(2018, 
                                                                   1, 
                                                                   1, 
                                                                   12, 0, 0)

def test_iteration(dataset_container):
    """Test that iteration correctly returns the sequence of datapoints 
    stored.
    """
    datapoints = [Datapoint(datetime(2018, 1, 1, 12, 0, 0), 1), 
                  Datapoint(datetime(2018, 1, 1, 12, 1, 0), 2),
                  Datapoint(datetime(2018, 1, 1, 12, 2, 0), 3)]
    dataset_container.append(datetime(2018, 1, 1, 12, 0, 0), 1)
    dataset_container.append(datetime(2018, 1, 1, 12, 1, 0), 2)
    dataset_container.append(datetime(2018, 1, 1, 12, 2, 0), 3)
    for test_datapoint, stored_datapoint in zip(dataset_container, datapoints):
        assert test_datapoint.timestamp == stored_datapoint.timestamp \
            and test_datapoint.value == stored_datapoint.value

def test_get_timeresolution(dataset_container):
    """Test reading out the time resolution."""
    assert dataset_container.time_resolution() == timedelta(minutes=1)

def test_set_timeresolution(dataset_container):
    """Test setting the time resolution."""
    timeres = timedelta(hours=1)
    assert dataset_container.time_resolution(timeres) == timeres

def test_get_timestamps(dataset_container):
    """Test getting the stored timestamps."""
    dataset_container.append(datetime(2018, 1, 1, 12, 0, 0), 1)
    dataset_container.append(datetime(2018, 1, 1, 12, 1, 0), 2)
    dataset_container.append(datetime(2018, 1, 1, 12, 2, 0), 3)
    expected_timestamps = array((datetime(2018, 1, 1, 12, 0, 0),
                                 datetime(2018, 1, 1, 12, 1, 0),
                                 datetime(2018, 1, 1, 12, 2, 0)))
    assert (dataset_container[0] == expected_timestamps).all()
    assert (dataset_container['timestamps'] == expected_timestamps).all()

def test_get_values(dataset_container):
    """Test getting the stored values."""
    dataset_container.append(datetime(2018, 1, 1, 12, 0, 0), 1)
    dataset_container.append(datetime(2018, 1, 1, 12, 1, 0), 2)
    dataset_container.append(datetime(2018, 1, 1, 12, 2, 0), 3)
    expected_values = array((1, 2, 3))
    assert (dataset_container[1] == expected_values).all()
    assert (dataset_container['values'] == expected_values).all()

def test_get_timestamp_start(dataset_container):
    """Test that timestamp_start returns the correct timestamp."""
    dataset_container.append(datetime(2018, 1, 1, 12, 0, 0), 1)
    dataset_container.append(datetime(2018, 1, 1, 12, 1, 0), 2)
    dataset_container.append(datetime(2018, 1, 1, 12, 2, 0), 3)
    assert dataset_container.timestamp_start() == datetime(2018, 1, 1, 12, 0, 0)

def test_get_timestamp_end(dataset_container):
    """Test that timestamp_end returns the correct timestamp."""
    dataset_container.append(datetime(2018, 1, 1, 12, 0, 0), 1)
    dataset_container.append(datetime(2018, 1, 1, 12, 1, 0), 2)
    dataset_container.append(datetime(2018, 1, 1, 12, 2, 0), 3)
    assert dataset_container.timestamp_end() == datetime(2018, 1, 1, 12, 2, 0)

def test_get_timerange(dataset_container):
    """Test that timerange returns a list with the correct timestamps."""
    dataset_container.append(datetime(2018, 1, 1, 12, 0, 0), 1)
    dataset_container.append(datetime(2018, 1, 1, 12, 1, 0), 2)
    dataset_container.append(datetime(2018, 1, 1, 12, 2, 0), 3)
    timerange = dataset_container.timerange() 
    assert timerange == [datetime(2018, 1, 1, 12, 0, 0), 
                         datetime(2018, 1, 1, 12, 2, 0)] 
