#!/usr/bin/pythonw
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import argparse
import nltk
import glob
import csv
import os
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tree import Tree
from sklearn.feature_extraction import DictVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

##returns a list of docs when given a list of directories/locations
def get(src_list):
    #print("Files being extracted",src_list)
    #Need to include try and except
    docs = []
    for src_dir in src_list:
        for src in src_dir[0:50]:
        #for src in src_dir:
            #print("src",src)
            src_string = open(src, 'r', encoding='utf-8')
            src_string = src_string.read()
            docs.append(src_string)
#    print("Input:",src_string)
    return docs

def find_entity(doc,doc_name):
    p_name = '' #getting the previous name in the document if any
    doc_length = len(doc)
    m = re.findall(r'_(\d{1,2}).txt',doc_name)
    rate = m[0]
    prev_chunk = ('','')
    # names of people present in the text
    names_l = []
    for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(doc))): #doc instead of sent
        if type(chunk) == Tree:       #checking for names using the type of the element
            name = ''
            length_name = 0
            n_wrds = 0
            if chunk.label() == 'PERSON':
                name_dict = {}
                #print(chunk)
                name_l = [0,0,0]
                for ind,i in enumerate(chunk):                   #For Full names we get back a tuple with multiple names so we iterat)e
                    #print(i)
                    name = name + ' ' +i[0]
                    n_wrds += 1
                    if ind < 3:
                        name_l[ind] = len(i[0])      #Captuting the length of each of the words in the name
                name = name[1:]
                tot_nam_len = len(name)
                #print(prev_chunk)
                #prev_c =  '^' if prev_chunk[0] == '>' else prev_chunk[0]
                name_dict = {'name': name,'l_1': name_l[0],'l_2': name_l[1],'l_3':name_l[2], 'no_words': n_wrds ,'name_length':tot_nam_len ,'rating': int(rate),'doc_length': doc_length}#, 'word_b': prev_chunk[0],'word_b_tag' : prev_chunk[1]}
                #print(name_dict)
                    #p_name = name
                names_l.append(name_dict)
        prev_chunk = chunk
    return names_l
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=str, required=True, help="Train Source File location", nargs='*', action='append')
    parser.add_argument("--test", type=str, required=False, help="Test Source File location", nargs='*', action='append')

    args = parser.parse_args()
    #---------------------------------------------------------------------------------TRAIN------------------------------------------------------------------------------
    if args.train:
        #print("training args",args.train)
        train_dirs = []
        for i in args.train:
            train_dirs.append(glob.glob(i[0]))
        #print("Train dirs:",len(train_dirs))
        train = get(train_dirs)
    #print("End",train)
    
    train_fts_d = []
    train_dirs_flat = [item for sublist in train_dirs for item in sublist]

    for ind,doc in enumerate(train):
        train_fts_d = train_fts_d + find_entity(doc,train_dirs_flat[ind])
    print("Train Features Extracted")
    
#creating the training dataset
    target_train = []
    fet_train = []
    for name_dict in train_fts_d:
        #print(name_dict['name'])
        target_train.append(name_dict['name'])
        del name_dict['name']
        #print(name_dict)
        fet_train.append(name_dict)
    #print(y_train,X_train)
    
    target_train = np.array(target_train)
    #target_train = target_train.reshape(-1,1)
    #Creating X in the training set
    v = DictVectorizer(sparse=False)
    fet_train = v.fit_transform(fet_train)
    print("Features:",v.get_feature_names())
#Training the model
    #clf = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(50, 25), random_state=1)
    mod = GaussianNB()
    #clf  = KNeighborsClassifier(n_neighbors=10)
    mod.fit(fet_train, target_train)
    print("Model trained")
#getting the test data
    global get_entity_test
    def get_entity_test(doc,doc_name):
        #print(doc_name)
        name_d = {}
        names_list_t = []
        doc_length = len(doc)
        m = re.findall(r'_(\d{1,2}).txt',doc_name)
        rate = m[0]
        #Initializing the feature variables
        prev_chunk = ' '
        name = ''
        l_1 =0
        l_2 = 0
        l_3 = 0
        n_wrds = 0
        total_length = 0
        chunks = nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(doc)))
        flag = False
        for chunk in chunks:
            #print(chunk)
            #Intiating name collection
            if chunk[0][0] == '█' and flag != True:
                flag = True
                name = name + chunk[0]
                a_prev_chunk = prev_chunk

            if prev_chunk[0][0] == '█' and chunk[0][0] == '█':
                name = name + ' ' +chunk[0]

            elif prev_chunk[0][0] == '█' and chunk[0][0] != '█':
#                name_dict['name'] = name
                n = nltk.word_tokenize(name)
                #print(n)
                n_wrds = len(n)
                l_1 = len(n[0])
                if n_wrds > 1:
                    l_2 = len(n[1])
                if n_wrds > 2:
                    l_3 = len(n[2])
                total_length = len(name)
                #prev_c =  '^' if prev_chunk[0] == '>' else prev_chunk[0]
                #print(a_prev_chunk)
                name_d = {'l_1':l_1,'l_2':l_2,'l_3':l_3,'no_words':n_wrds, 'name_length':total_length,'rating':int(rate),'doc_length':doc_length}#,'word_b':a_prev_chunk[0],'doc_length':doc_length}
                names_list_t.append(name_dict)
                #Resetting values
                l_1,l_2,l_3,n_wrds,tot_nam_len = 0,0,0,0,0
                flag = False
                name = ''
            prev_chunk = chunk
        return names_list_t

#test directroies - test text retreival
    if args.test:
        #print(args.test)
        test_dirs = []
        for i in args.test:
            test_dirs.append(glob.glob(i[0]))
        #print(test_dirs)
        test = get(test_dirs)
    #print(test) 
    test_dir_flat = [item for sublist in test_dirs for item in sublist]
    test_fts_d = []
    count = 0
    for doc in test:
       test_fts_d = test_fts_d + get_entity_test(doc, test_dir_flat[count])
       count += 1
    print("Test Features Extracted")
    #print(test_fts_d)
    fet_test = v.transform(test_fts_d)
    print("Train set size:",fet_train.shape,target_train.shape)
    #print(fts_test)
    target_test_pred =  mod.predict(fet_test)
    #print(target_test_pred)
    print("Accuracy on training set",mod.score(fet_train, target_train))
    print("Test values predicted")
    with open('pred_names.txt', 'w',encoding = 'utf-8') as f:
        f.write("Predicted Names for the redacted test file\n")
        for i in target_test_pred:
            f.write(i+'\n')
    print("pred_names.txt printed")

