# -*- coding: utf-8 -*-

import redactor
from redactor import redactor

def test_rm_genders():
    text = "Today is January 1, 2047 at 8:21:00AM. I have 2 apples at 2AM. We also have pines tomorrow."
    pred_output = ['January','1','2047','8:21:00AM','2','2AM']
    _,act_output = redactor.rm_dates(text)
    assert pred_output == act_output,"Number of date items did not match"
