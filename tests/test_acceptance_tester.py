#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..filter_provider import acceptance_tester
from ..dataset_container import datapoint
from datetime import datetime

def test_heartrate_accept():
    """Test the correct acceptance for a valid heartrate datapoint."""
    acc_tester = acceptance_tester('heartrate')
    dp = datapoint(datetime(2018, 1, 1, 12, 0, 0), 1)
    assert acc_tester(dp) is True

def test_heartrate_reject():
    """Test the correct rejection for invalid heartrate datapoints."""
    acc_tester = acceptance_tester('heartrate')
    dp = datapoint(datetime(2018, 1, 1, 12, 0, 0), 0)
    assert acc_tester(dp) is False
    dp = datapoint(datetime(2018, 1, 1, 12, 0, 0), -1)
    assert acc_tester(dp) is False
    dp = datapoint(datetime(2018, 1, 1, 12, 0, 0), 255)
    assert acc_tester(dp) is False
    dp = datapoint(datetime(2018, 1, 1, 12, 0, 0), 256)
    assert acc_tester(dp) is False

def test_intensity_reject():
    """Test the correct rejection for invalid intensity datapoints."""
    acc_tester = acceptance_tester('intensity')
    dp = datapoint(datetime(2018, 1, 1, 12, 0, 0), 255)
    assert acc_tester(dp) is False
    dp = datapoint(datetime(2018, 1, 1, 12, 0, 0), 256)
    assert acc_tester(dp) is False

def test_intensity_accept():
    """Test the correct acceptance for a valid intensity datapoint."""
    acc_tester = acceptance_tester('intensity')
    dp = datapoint(datetime(2018, 1, 1, 12, 0, 0), 1)
    assert acc_tester(dp) is True

def test_steps_accept():
    """Test the correct acceptance for valid steps datapoints."""
    acc_tester = acceptance_tester('steps')
    dp = datapoint(datetime(2018, 1, 1, 12, 0, 0), 1)
    assert acc_tester(dp) is True
    dp = datapoint(datetime(2018, 1, 1, 12, 0, 0), 0)
    assert acc_tester(dp) is True
    dp = datapoint(datetime(2018, 1, 1, 12, 0, 0), 256)
    assert acc_tester(dp) is True

def test_steps_reject():
    """Test the correct rejection for an invalid steps datapoint."""
    acc_tester = acceptance_tester('steps')
    dp = datapoint(datetime(2018, 1, 1, 12, 0, 0), -1)
    assert acc_tester(dp) is False

def test_nofilter():
    """Test the correct acceptance for a non-specified datapoint."""
    acc_tester = acceptance_tester('')
    dp = datapoint(datetime(2018, 1, 1, 12, 0, 0), 1)
    assert acc_tester(dp) is True
