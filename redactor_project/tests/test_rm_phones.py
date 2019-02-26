#import sys
#sys.path.insert(0,'/projects/redactor/redactor')
import redactor
from redactor import redactor

def test_rm_phones():
    text = " 000-000-0000 2432 asda  000 000 0000 is my phone number  000.000.0000asdasda\n sadas 1324 (000)000-0000 is Umesh's number.\n (000)000 0000    (000)000.0000     (000) 000-0000       (000) 000 0000                 (000) 000.0000    000-0000    000 0000      000.0000                000 0000                 0000000000                  (000)0000000                     +910011001000               9100000000                 +91 001 100 1000            11++91-000-100-1000+121.      1231+011-000-000-0000123asda"
    pred_output = 20 #phone numbers
#    print(redactor.rm_phones(text))
    _,act_output = redactor.rm_phones(text)
    assert pred_output == len(act_output),"Number of date items did not match"
