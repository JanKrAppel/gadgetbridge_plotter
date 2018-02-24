#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..plotting import Plotter, InvalidArgumentsException
from datetime import datetime
from numpy import array
import pytest

def test_lineplot_construction():
    """Test that instances for lineplots get constructed correctly."""
    test_times = array((datetime(2018, 1, 1, 12, 0, 0), 
                        datetime(2018, 1, 1, 12, 1, 0), 
                        datetime(2018, 1, 1, 12, 2, 0), 
                        datetime(2018, 1, 1, 12, 3, 0), 
                        datetime(2018, 1, 1, 12, 4, 0), 
                        datetime(2018, 1, 1, 12, 5, 0), 
                        datetime(2018, 1, 1, 12, 6, 0), 
                        datetime(2018, 1, 1, 12, 7, 0), 
                        datetime(2018, 1, 1, 12, 8, 0), 
                        datetime(2018, 1, 1, 12, 9, 0)))
    test_values = array((1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
    plotter = Plotter('test plot', timestamps=test_times, values=test_values)
    assert plotter._plotfunc == plotter._line_plot
    assert (plotter._timestamps == test_times).all()
    assert (plotter._values == test_values).all()
    assert plotter._type == 'test plot'

def test_histogram_construction():
    """Test that instances for histogram plots get constructed correctly."""
    test_times = array((datetime(2018, 1, 1, 12, 0, 0), 
                        datetime(2018, 1, 1, 12, 1, 0), 
                        datetime(2018, 1, 1, 12, 2, 0), 
                        datetime(2018, 1, 1, 12, 3, 0), 
                        datetime(2018, 1, 1, 12, 4, 0), 
                        datetime(2018, 1, 1, 12, 5, 0), 
                        datetime(2018, 1, 1, 12, 6, 0), 
                        datetime(2018, 1, 1, 12, 7, 0), 
                        datetime(2018, 1, 1, 12, 8, 0), 
                        datetime(2018, 1, 1, 12, 9, 0)))
    test_bins = array((1, 2, 3, 4, 5))
    test_histogram = array([[1, 2, 3, 4, 5],
                            [1, 2, 3, 4, 5],
                            [1, 2, 3, 4, 5],
                            [1, 2, 3, 4, 5],
                            [1, 2, 3, 4, 5],
                            [1, 2, 3, 4, 5],
                            [1, 2, 3, 4, 5],
                            [1, 2, 3, 4, 5],
                            [1, 2, 3, 4, 5],
                            [1, 2, 3, 4, 5]])
    plotter = Plotter('test plot', timestamps=test_times, bins=test_bins, 
                      histogram=test_histogram)
    assert plotter._plotfunc == plotter._hist_plot
    assert (plotter._timestamps == test_times).all()
    assert (plotter._bins == test_bins).all()
    assert (plotter._histogram == test_histogram).all()
    assert plotter._type == 'test plot'
    
def test_invalid_construction():
    """Test that instantiation with incorrect arguments raise an exception."""
    with pytest.raises(InvalidArgumentsException):
        plotter = Plotter('test plot', foo=1, bar=1)