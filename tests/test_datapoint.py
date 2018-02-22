#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..dataset_container import datapoint

def test_datapoint_construction():
    dp = datapoint(1, 2)
    assert dp.timestamp == 1 and dp.value == 2

def test_datapoint_iteration():
    dp = datapoint(1, 2)
    ts, val = dp
    assert ts == 1 and val == 2