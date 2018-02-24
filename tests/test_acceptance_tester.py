#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..filter_provider import AcceptanceTester
from ..dataset_container import Datapoint
from datetime import datetime

def test_heartrate_accept():
    """Test the correct acceptance for a valid heartrate Datapoint."""
    acc_tester = AcceptanceTester('heartrate')
    dp = Datapoint(datetime(2018, 1, 1, 12, 0, 0), 1)
    assert acc_tester(dp) is True

def test_heartrate_reject():
    """Test the correct rejection for invalid heartrate datapoints."""
    acc_tester = AcceptanceTester('heartrate')
    dp = Datapoint(datetime(2018, 1, 1, 12, 0, 0), 0)
    assert acc_tester(dp) is False
    dp = Datapoint(datetime(2018, 1, 1, 12, 0, 0), -1)
    assert acc_tester(dp) is False
    dp = Datapoint(datetime(2018, 1, 1, 12, 0, 0), 255)
    assert acc_tester(dp) is False
    dp = Datapoint(datetime(2018, 1, 1, 12, 0, 0), 256)
    assert acc_tester(dp) is False

def test_intensity_reject():
    """Test the correct rejection for invalid intensity datapoints."""
    acc_tester = AcceptanceTester('intensity')
    dp = Datapoint(datetime(2018, 1, 1, 12, 0, 0), 255)
    assert acc_tester(dp) is False
    dp = Datapoint(datetime(2018, 1, 1, 12, 0, 0), 256)
    assert acc_tester(dp) is False

def test_intensity_accept():
    """Test the correct acceptance for a valid intensity Datapoint."""
    acc_tester = AcceptanceTester('intensity')
    dp = Datapoint(datetime(2018, 1, 1, 12, 0, 0), 1)
    assert acc_tester(dp) is True

def test_steps_accept():
    """Test the correct acceptance for valid steps datapoints."""
    acc_tester = AcceptanceTester('steps')
    dp = Datapoint(datetime(2018, 1, 1, 12, 0, 0), 1)
    assert acc_tester(dp) is True
    dp = Datapoint(datetime(2018, 1, 1, 12, 0, 0), 0)
    assert acc_tester(dp) is True
    dp = Datapoint(datetime(2018, 1, 1, 12, 0, 0), 256)
    assert acc_tester(dp) is True

def test_steps_reject():
    """Test the correct rejection for an invalid steps Datapoint."""
    acc_tester = AcceptanceTester('steps')
    dp = Datapoint(datetime(2018, 1, 1, 12, 0, 0), -1)
    assert acc_tester(dp) is False

def test_nofilter():
    """Test the correct acceptance for a non-specified Datapoint."""
    acc_tester = AcceptanceTester('')
    dp = Datapoint(datetime(2018, 1, 1, 12, 0, 0), 1)
    assert acc_tester(dp) is True
