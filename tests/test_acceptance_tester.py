#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..filter_provider import acceptance_tester
from ..dataset_container import datapoint

def test_heartrate_accept():
    acc_tester = acceptance_tester('heartrate')
    dp = datapoint(1, 1)
    assert acc_tester(dp) is True

def test_heartrate_reject():
    acc_tester = acceptance_tester('heartrate')
    dp = datapoint(1, 0)
    assert acc_tester(dp) is False
    dp = datapoint(1, -1)
    assert acc_tester(dp) is False
    dp = datapoint(1, 255)
    assert acc_tester(dp) is False
    dp = datapoint(1, 256)
    assert acc_tester(dp) is False

def test_intensity_reject():
    acc_tester = acceptance_tester('intensity')
    dp = datapoint(1, 255)
    assert acc_tester(dp) is False
    dp = datapoint(1, 256)
    assert acc_tester(dp) is False

def test_intensity_accept():
    acc_tester = acceptance_tester('intensity')
    dp = datapoint(1, 1)
    assert acc_tester(dp) is True

def test_steps_accept():
    acc_tester = acceptance_tester('steps')
    dp = datapoint(1, 1)
    assert acc_tester(dp) is True
    dp = datapoint(1, 0)
    assert acc_tester(dp) is True
    dp = datapoint(1, 256)
    assert acc_tester(dp) is True

def test_steps_reject():
    acc_tester = acceptance_tester('steps')
    dp = datapoint(1, -1)
    assert acc_tester(dp) is False

def test_nofilter():
    acc_tester = acceptance_tester('')
    dp = datapoint(1, 1)
    assert acc_tester(dp) is True
