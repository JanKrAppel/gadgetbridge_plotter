#!/usr/bin/env python
# -*- coding: utf-8 -*-

datasets = ['heartrate', 'timestamp', 'activity', 'intensity', 'steps']

device_db_mapping = {'MI_BAND': {'table': 'MI_BAND_ACTIVITY_SAMPLE', 
                                'heartrate_col': 'HEART_RATE', 
                                'timestamp_col': 'TIMESTAMP',
                                'activity_col': 'RAW_KIND',
                                'intensity_col': 'RAW_INTENSITY',
                                'steps_col': 'STEPS'}}