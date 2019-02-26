# -*- coding: utf-8 -*-
#import sys
#sys.path.insert(0,'/projects/redactor/redactor')
import redactor
from redactor import redactor

def test_rm_addresses():
    text = "14, Board Dr., Norman, OK is my address. I also live at 113, Summerpointe, East Brooks Street, Norman, OK-73071. I live in Norman. We have apples here."
    pred_output = ['14,', 'Board', 'Dr.,', '113,', 'Summerpointe,', 'East', 'Brooks', 'Street,']
    print(redactor.rm_addresses(text))
    _,act_output = redactor.rm_addresses(text)
    assert pred_output == act_output,"Number of date items did not match"
