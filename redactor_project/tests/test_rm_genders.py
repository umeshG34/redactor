
#import sys
#sys.path.insert(0,'/projects/redactor/redactor')
import redactor
from redactor import redactor
def test_rm_genders():
        text ='She was going to the mall to buy some clothes for him. He was a Fireman. She was an Actress and a Countess. Hence, she was regal.'
        pred_output = ['she','him','he','fireman','she','actress','countess','she']
        _,act_output = redactor.rm_genders(text)
        assert len(pred_output) == len(act_output),"Number of redacted items did not match"
