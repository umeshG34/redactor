# -*- coding: utf-8 -*-
#import sys
#sys.path.insert(0,'/projects/redactor/redactor')
import redactor
from redactor import redactor

def test_rm_names():
    text ='This is Umesh. The data is 23rd March 2018 or 3/23/2018. I am in Norman, OK, Oklahoma, USA, America. Zarah and Michael are good friends. Sarah-Jane is a neighbor of ours.'
    pred_output = ['Zarah','Michael','Umesh']
    pred_output.sort(key=lambda s: len(s), reverse=True)
    _,act_output = redactor.rm_names(text)
    assert len(pred_output) == len(act_output),"Names do not match."
