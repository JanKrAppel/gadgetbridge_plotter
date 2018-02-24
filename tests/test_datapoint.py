#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..dataset_container import datapoint
from datetime import datetime

def test_datapoint_construction():
    """Test that datapoints correctly store the values passed to them."""
    dp = datapoint(datetime(2018, 1, 1, 12, 0, 0), 2)
    assert dp.timestamp == datetime(2018, 1, 1, 12, 0, 0) and dp.value == 2

def test_datapoint_iteration():
    """Test that data points correctly return values when iterated over"""
    dp = datapoint(datetime(2018, 1, 1, 12, 0, 0), 2)
    ts, val = dp
    assert ts == datetime(2018, 1, 1, 12, 0, 0) and val == 2