#import sys
#sys.path.insert(0,'/projects/redactor/redactor')
import redactor
from redactor import redactor

def test_rm_concept():
    text = "We like to eat dinner. We had quiet a feast yesterday. The food was good for lunch. We need to get more people though."
    pred_output = 2 # number of expcetd redacted lines
    _,act_output = redactor.rm_concept(text,'dinner')
    assert pred_output == act_output,"Number of redacted lines did not match"
