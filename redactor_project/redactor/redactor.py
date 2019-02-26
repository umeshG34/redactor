#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import nltk
import glob
import re                   #for phones
import csv
import difflib
from dateutil.parser import parse #for dates
import usaddress
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tokenize.moses import MosesDetokenizer
from nltk.tree import Tree
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

#Reads content of multiple files and return them in a list
def get(src_list):
    #Ned to include try and except
    docs = []
    #print(src_list)
    for src_dir in src_list:
        #for src in src_dir:
        for src in src_dir[0:50]:
            with open(src,'r',encoding='UTF-8') as fyl:
                src_string = fyl.read()
                docs.append(src_string)
    #print("Input", docs)
    return docs

#Censors names of people
def rm_names(doc):
    #print("yes")
    chunk_l = []
    # names of people present in the text
    names_l = []
    for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(doc))): #doc instead of sent
        if type(chunk) == Tree:                     #checking for names using the type of the element
            #print('Tree', chunk[0][0], chunk)
            if chunk.label() == 'PERSON':
                for i in chunk:                      #For Full names we get back a tuple with multiple names so we iterate
                    names_l.append(i[0])             #appending the name of the name to be removed
        #chunk_l.append(chunk)
    names_l = list(set(names_l))
    names_l.sort(key=lambda s: len(s), reverse=True)    #making usre that the longer strings get removed first
    #print(names_l)
    for name in names_l:
        doc = doc.replace(name, '█' * len(name))  #Replacing with "*"
    return doc, names_l

def rm_genders(doc):
#not dress,press,ttress,ness
#End :man,men,woman,women
#start: girl
    gender_corp = [ 'lady','ladies', 'fille', 'daughter','daughters', 'miss', 'female','babe'
        , 'son', 'manly', 'manful', 'male', 'manlike', 'her', 'hers', 'she', 'he'
        , 'him','his', 'guy','guys','gals' 'gal','dad','mom','daddy','mamma'
        , 'lassie', 'dame', 'maiden', 'ladylike', 'womanly','himself','herself'
        , 'mother', 'father', 'sister', 'brother', 'aunt', 'uncle', 'mama', 'queen', 'king'
        , 'mister', 'missus','wife','husband']
    gender_corp = set(gender_corp)
    doc_l = []
    rm_st = []
    sens = doc.split("\n")
    for sent in sens:
        sent_l = []
        for token in nltk.word_tokenize(sent):
            token_lo = token.lower()
            not_ess = r'^\w+dress$|^\w+press$|^\w+ttress$|^\w+ness$'
            r_other = r'^boy\w*$|^girl\w*$|^\w*girl$|^\w*boy$|^\w*men$|^\w*man$'
            if (token_lo in gender_corp) or ((re.match('^\w+ess$', token_lo) is not None) and ((re.match(not_ess, token_lo) is None)))or((re.match(r_other, token_lo) is not None)):
                sent_l.append("█" * len(token))
                rm_st.append(token_lo)
            else:
                sent_l.append(token)
        deto = MosesDetokenizer()
        sent_n = deto.detokenize(sent_l, return_str=True)
        doc_l.append(sent_n)
    doc = "\n".join(doc_l)
    return doc,rm_st

# Works pretty well except when short number are included. Then the date utilparse thinks it is a
def rm_dates(doc):
    rm_str = []
    doc_l = []
    sens = doc.split("\n")
    #print(sens)
    for sent in sens:
        sent_l = []
        for token in nltk.word_tokenize(sent):
            try:                                    #brilliant simple way to detect whether a string has dates in it
                parse(token)
                sent_l.append("█"*len(token))
                rm_str.append(token)
            except ValueError:
                sent_l.append(token)
        #print(sent_l)
        deto = MosesDetokenizer()
        sent_n = deto.detokenize(sent_l,return_str=True)
        #sent_n = " ".join(sent_l)
        doc_l.append(sent_n)
    #print(doc_l)
    doc = "\n".join(doc_l)
    #print(doc)
    return doc, rm_str


# Not working perfectly. It is able to detect the address in most cases when it is given in a certain format like "114, E Boyd St., Norman ,OK, USA."
# We are using the usaddress package which tags each of the word using which we are redacting the strings. Our accuracy completely depends on how well
# the package performs.
def rm_addresses(doc):
    doc_l = []
    rm_st = []
    sens = doc.split("\n")
    for sent in sens:
        sent_l = []
        usaddress.parse(sent)
        for tuple2 in usaddress.parse(sent):
           # print(tuple2)
            if tuple2[1] == 'BuildingName' or tuple2[1] == 'Recipient' or tuple2[1] == 'OccupancyType' or tuple2[1] == 'OccupancyIdentifier' or  tuple2[1] == 'LandmarkName':
                sent_l.append(tuple2[0])
            else:
                sent_l.append("█" * len(tuple2[0]))
                rm_st.append(tuple2[0])
        # print(sent_l)
        deto = MosesDetokenizer()
        sent_n = deto.detokenize(sent_l, return_str=True)
        # sent_n = " ".join(sent_l)
        doc_l.append(sent_n)
    # print(doc_l)
    doc = "\n".join(doc_l)
    #print(doc)
    return doc, rm_st

def rm_phones(doc):
    ph_nos = re.findall(r'((\+\d{11,13})|(\+\d{1,3}[\s\-\.])??(\(?\d{3}\)?[\s\.\-]?)?\d{3}[\s\.\-]?\d{4})',doc)
    #print(ph_nos)
    ph_nos.sort(key=lambda s: len(s), reverse=True)
    for no in ph_nos:
        doc = doc.replace(no[0],'█'*len(no[0]))
    #print(doc)
    return doc, ph_nos

def rm_concept(doc,concept):
    concept_syns = []
    rm_count = 0
    for i in wn.synsets(concept):
        concept_syns.append([i])
        concept_syns.append(i.hypernyms())
        concept_syns.append(i.hyponyms())
        concept_syns.append(i.member_holonyms())
        #print("I:",i)
        #print(i.hypernyms())
        # print(i.hyponyms())
        # print(i.member_holonyms())
    concept_syns = sum(concept_syns, [])
    #print(concept_syns)
    lemmas = []
    for syn in concept_syns:
        for lemma in syn.lemmas():
            lemmas.append(lemma.name())
    #print("Words related to the concept:",lemmas)
    doc_l = []
    sens = doc.split("\n")
    #print(sens)
    for sent in sens:
        sent_l = []
        for sent1 in nltk.sent_tokenize(sent):
            flag = 0
            for token in nltk.word_tokenize(sent1):
                token = token.lower()
                if token in lemmas: flag = 1
                #print(token,flag)
            if flag == 1:
                sent_l.append("█" * len(sent1))
                #print("test",sent_l)
                rm_count += 1
            else:
                sent_l.append(sent1)
        #print(sent_l)
        deto = MosesDetokenizer()
        sent_n = deto.detokenize(sent_l, return_str=True)
        # sent_n = " ".join(sent_l)
        doc_l.append(sent_n)
    #print(doc_l)
    doc = "\n".join(doc_l)
    # print(doc)
    return doc,rm_count

#Checks two directories above to see if the location is the same and then writes the file
def output(output_dir,input_dirs,docs):
    dirs_flat = [item for sublist in input_dirs for item in sublist]
    m_out = re.search(r'(/\w*/\w*)/$',output_dir)
    for ind,doc in enumerate(docs):
        #print(dirs_flat[ind])
        m_in = re.search(r'(\w*/\w*)/\d{1,5}_\d{1,2}.txt',dirs_flat[ind])
        op_loc = m_out.groups()[0]
        f_name = re.search('/(\d{1,5}_\d{1,2}).txt',dirs_flat[ind])
        f_name = f_name.group(1)
        #print(f_name)
        #print(m_in)
        if op_loc == (m_in.groups())[0]:
            f_name = f_name + '.redacted.txt'
            op_loc = output_dir + f_name
        else:
            f_name = f_name
            op_loc = output_dir + f_name + '.txt'
        text_file = open(op_loc,'w',encoding = 'UTF-8')
        text_file.write(doc)
        text_file.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Source File location", nargs='*', action='append')

    parser.add_argument("--names", required=False, help="Removes Names", action='store_true')
    parser.add_argument("--genders", required=False, help="Removes genders and gender references", action='store_true')
    parser.add_argument("--dates",  required=False, help="Removes dates", action='store_true')
    parser.add_argument("--addresses", required=False, help="Removes addresses", action='store_true')
    parser.add_argument("--phones", required=False, help="Removes phone numbers", action='store_true')
    parser.add_argument("--stats", type = str,required=False, help="Gives statistics for redacted files")

    parser.add_argument("--concept", type=str, required=False, help="Concept word removal")
     
    parser.add_argument("--output", type=str, required=True, help="Output File location")

    args = parser.parse_args()
    #print(args)
    
    if args.input:
        dirs = []
        for i in args.input:
            dirs.append(glob.glob(i[0]))
        #print("Directories:",dirs)
        docs = get(dirs)

    dirs_flat = [item for sublist in dirs for item in sublist]
    names_stat = []
    if args.names:
        docs_names = []
        count = 0
        for doc in docs:
            doc_r, name_red  = rm_names(doc)
            docs_names.append(doc_r)
            name_stat_d = [dirs_flat[count],len(name_red)]
            names_stat.append(name_stat_d)
            count += 1
        print("->Names Redacted")
        docs = docs_names
        #print(docs)
    #print(names_stat)

    genders_stat = []
    if args.genders:
        docs_gen = []
        count = 0
        for doc in docs:
            doc_r,gender_red = rm_genders(doc)
            docs_gen.append(doc_r)
            gender_stat_d = [dirs_flat[count],len(gender_red)]
            genders_stat.append(gender_stat_d)
            count += 1
        print("->genders redacted")
        docs = docs_gen

    phones_stat = []
    if args.phones:
        phones_stat = []
        docs_ph = []
        count = 0
        for doc in docs:
            doc_r,phones_red = rm_phones(doc)
            docs_ph.append(doc_r)
            phones_stat_d = [dirs_flat[count],len(phones_red)]
            phones_stat.append(phones_stat_d)
            count += 1
        print("->Phones redacted")
        docs = docs_ph
        #print(docs)
    dates_stat = []
    if args.dates:
        docs_dates = []
        count = 0
        for doc in docs:
            doc_r, dates_red = rm_dates(doc)
            docs_dates.append(doc_r)
            dates_stat_d = [dirs_flat[count], len(dates_red)]
            dates_stat.append(dates_stat_d)
            count += 1
        print("->dates redacted")
        docs = docs_dates
        #print(docs)

    adds_stat= []
    if args.addresses:
        docs_add = []
        count = 0
        for doc in docs:
            doc_r, adds_red = rm_addresses(doc)
            docs_add.append(doc_r)
            adds_stat_d = [dirs_flat[count],len(adds_red)]
            adds_stat.append(adds_stat_d)
            count += 1
        print("->addresses redacted")
        docs = docs_add

    if args.concept:
        docs_add = []
        for doc in docs:
            doc_r, _ = rm_concept(doc, args.concept)
            docs_add.append(doc_r)
        print("->concepts redacted")
        #print(docs)
        docs = docs_add

    if args.stats:
        with open('output_stats.txt', 'w',encoding = 'utf-8') as f:
            writer = csv.writer(f, delimiter = 'þ',quoting=csv.QUOTE_NONE)
            f.write('NUMBER OF NAMES REDACTED IN EACH FILE\n')
            writer.writerows(names_stat)
            f.write('NUMBER OF GENDER REFERENCES REDACTED IN EACH FILE\n')
            writer.writerows(genders_stat)
            f.write('NUMBER OF PHONE NUMBERS REDACTED IN EACH FILE\n')
            writer.writerows(phones_stat)
            f.write('NUMBER OF DATE RELATED REDACTIONS IN EACH FILE\n')
            writer.writerows(dates_stat)
            f.write('NUMBER OF ADDRESSE RELATED REDACTIONS IN EACH FILE\n')
            writer.writerows(adds_stat)
        if args.stats.lower() == 'stdout':
            print('\nNUMBER OF NAMES REDACTED IN EACH FILE','\n',names_stat,'\nNUMBER OF GENDER REFERENCES REDACTED IN EACH FILE','\n',genders_stat)
            print('\nNUMBER OF PHONE NUMBERS REDACTED IN EACH FILE','\n',phones_stat)
            print('\nNUMBER OF DATE RELATED REDACTIONS IN EACH FILE','\n',dates_stat)
            print('\nNUMBER OF ADDRESSE RELATED REDACTIONS IN EACH FILE','\n',adds_stat)

    if args.output:
        output(args.output, dirs,docs)
        print("->Output Done")
