#import sys
#sys.path.insert(0,'/projects/redactor/redactor')
import redactor
from redactor import unredactor

def test_get_entity():
    text = "My name is John Von. Your name is Jack Neeman."
    pred_output = [{'name': 'John Von', 'l_1': 4, 'l_2': 3, 'l_3': 0, 'no_words': 2, 'name_length': 8, 'rating': 5, 'doc_length': 46}, {'name': 'Jack Neeman', 'l_1': 4, 'l_2': 6, 'l_3': 0, 'no_words': 2, 'name_length': 11, 'rating': 5, 'doc_length': 46}]
    #print(unredactor.find_entity(text,'/trainfiles/pos/111_5.txt'))
    act_output = unredactor.find_entity(text,'/trainfiles/pos/111_5.txt')
    assert pred_output == act_output,"Features extracted not same"
