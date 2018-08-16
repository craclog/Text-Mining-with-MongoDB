#-*- coding: utf-8 -*-
# 20131579 Kiyoung Yoon
import datetime
import time
import sys
import MeCab
import operator
from pymongo import MongoClient
from bson import ObjectId
from itertools import combinations

#Connect DB
DBname = "db20131579"
conn = MongoClient('dbpurple.sogang.ac.kr')
db = conn[DBname]
db.authenticate(DBname, DBname)
stop_word = {}

def printMenu():
    print("0. CopyData")
    print("1. Morph")
    print("2. print morphs")
    print("3. print wordset")
    print("4. frequent item set")
    print("5. association rule")

# Read and Use 'wordList.txt' to morphing
def make_stop_word():
    f = open("wordList.txt", 'r')
    while True:
        line = f.readline()
        if not line: break
        stop_word[line.strip('\n')] = line.strip('\n')
    f.close()

def morphing(content):
    t = MeCab.Tagger('-d/usr/local/lib/mecab/dic/mecab-ko-dic')
    nodes = t.parseToNode(content.encode('utf-8'))
    MorpList = []
    while nodes:
        if nodes.feature[0] == 'N' and nodes.feature[1] == 'N':
            w = nodes.surface
            if not w in stop_word:
                try:
                    w = w.encode('utf-8')
                    MorpList.append(w)
                except:
                    pass
        nodes = nodes.next
    return MorpList

#Copy Data from 'news' to 'news_freq'
def p0():
    col1 = db['news']
    col2 = db['news_freq']
    col2.drop()
    for doc in col1.find():
        contentDic = {}
        for key in doc.keys():
            if key != "_id":
                contentDic[key] = doc[key]
        col2.insert(contentDic)

# Update collection with :
# add Key : morph
# delete unnecessary words
def p1():
    for doc in db['news_freq'].find():
        doc['morph'] = morphing(doc['content'])
        db['news_freq'].update({"_id":doc['_id']}, doc)

# Print morph
# input : article-url
def p2(url):
    col1 = db['news_freq']
    for doc in col1.find():
        if doc['url'] == url:
            for x in doc['morph']:
                print(x.encode('utf-8'))

# Make 'news_wordset' collection
def p3():
    col1 = db['news_freq']
    col2 = db['news_wordset']
    col2.drop()
    for doc in col1.find():
        new_doc = {}
        new_set = set()
        for w in doc['morph']:
            new_set.add(w.encode('utf-8'))
        new_doc['word_set'] = list(new_set)
        new_doc['url'] = doc['url']
        col2.insert(new_doc)

# Print wordset       
# input : article-url
def p4(url):
    col1 = db['news_wordset']
    for doc in col1.find():
        if doc['url'] == url:
            for x in doc['word_set']:
                print(x.encode('utf-8'))

# Make frequent 1,2,3-itemset
# If p5(3) is called before calling p5(1) and p5(2),
# make candidate_L1, candidate_L2 too.
def p5(length):
    col1 = db['news_wordset'] 
    min_sup = 0.1   # set min_sup
    min_sup = col1.find().count() * min_sup
    if 1 <= length <= 3:
        count_L1  = {}
        col2 = db['candidate_L1']
        col2.drop() # Can be changed
        for doc in col1.find():
            for w in doc['word_set']:
                if w in count_L1:
                    count_L1[w] += 1
                else:
                    count_L1[w] = 1
        for w, sup in count_L1.items():
            if sup < min_sup:
                continue
            new_doc = {}
            new_set = set()
            new_set.add(w.encode('utf-8'))
            new_doc['item_set'] = list(new_set)
            new_doc['support'] = sup
            col2.insert(new_doc)

    if 2 <= length <= 3:
        count_L2 = {}
        col3 = db['candidate_L2']
        col3.drop() # Can be changed
        for doc in col1.find():
            for i in range(len(doc['word_set'])):
                #Check valid
                if count_L1[doc['word_set'][i]] < min_sup:
                    continue
                for j in range(i+1, len(doc['word_set'])):
                    #check valid
                    if count_L1[doc['word_set'][j]] < min_sup:
                        continue            
                    fs = frozenset([doc['word_set'][i], doc['word_set'][j]])
                    if fs in count_L2:
                        count_L2[fs] += 1
                    else:
                        count_L2[fs] = 1
        for w, sup in count_L2.items():
            w = list(w)
            #check valid
            if sup < min_sup:
                continue
            new_doc = {}
            new_doc['item_set'] = w
            new_doc['support'] = sup
            col3.insert(new_doc)
                     
    if length == 3:
        count_L3 = {}
        col4 = db['candidate_L3']
        col4.drop() # Can be...
        for doc in col1.find():
            for i in range(len(doc['word_set'])):
                for j in range(i+1, len(doc['word_set'])):
                    fs = frozenset([doc['word_set'][i], doc['word_set'][j]])
                    #check valid
                    if fs not in count_L2:
                        continue
                    if count_L2[fs] < min_sup:
                        continue
                    for k in range(j+1, len(doc['word_set'])):
                        fs = frozenset([doc['word_set'][i], doc['word_set'][k]])
                        if fs not in count_L2:
                            continue
                        if count_L2[fs] < min_sup:
                            continue
                        fs = frozenset([doc['word_set'][j], doc['word_set'][k]])
                        if fs not in count_L2:
                            continue
                        if count_L2[fs] < min_sup:
                            continue
                        
                        fs = frozenset([doc['word_set'][i], doc['word_set'][j], doc['word_set'][k]])
                        if fs in count_L3:
                            count_L3[fs] += 1
                        else:
                            count_L3[fs] = 1
        for w, sup in count_L3.items():
            w = list(w)
            if sup < min_sup:
                continue
            new_doc = {}
            new_doc['item_set'] = w
            new_doc['support'] = sup
            col4.insert(new_doc)
        
    else: return 0

# Print frequent n-th item set with strong asscocation rule
# n : length
def p6(length):
    min_conf = 0.5
    count_L1 = {}
    count_L2 = {}
    count_L3 = {}
    col1 = db['candidate_L1']
    col2 = db['candidate_L2']
    col3 = db['candidate_L3']
    for doc in col1.find():
        fs = frozenset(doc['item_set'])
        count_L1[fs] = doc['support']
    for doc in col2.find():
        fs = frozenset(doc['item_set'])
        count_L2[fs] = doc['support']
    for doc in col3.find():
        fs = frozenset(doc['item_set'])
        count_L3[fs] = doc['support']

    # key type : frozenset
    keys_L1 = count_L1.keys()
    keys_L2 = count_L2.keys()
    keys_L3 = count_L3.keys()
    if length == 1:
        pass

    elif length == 2:
        for k2 in keys_L2:
            denominator = float(count_L2[k2])
            k2 = list(k2)
            result = denominator / count_L1[ frozenset([k2[0]]) ]
            if result > min_conf:
                print("{} =>{}\t{}".format(k2[0], k2[1], result))
            result = denominator / count_L1[ frozenset([k2[1]]) ]
            if result > min_conf:
                print("{} =>{}\t{}".format(k2[1], k2[0], result))
    
    elif length == 3:
        for k3 in keys_L3:
            deno3 = float(count_L3[k3])
            k3 = list(k3)
            for i in range(3):
                i %= 3
                j = (i + 1) % 3
                m = (i + 2) % 3
                fs = frozenset([k3[i], k3[j]])
                result = deno3 / float(count_L2[fs])
                if result > min_conf:
                    print("{} ,{} =>{}\t{}".format(k3[i], k3[j], k3[m], result))
                result = deno3 / float(count_L1[ frozenset([k3[m]]) ])
                if result > min_conf:
                    print("{} =>{} ,{}\t{}".format(k3[m], k3[i], k3[j], result))
                    

if __name__ == "__main__":
    make_stop_word()
    printMenu()
    selector = input()
    # CopyData
    if selector == 0:
        p0()
    # Morph
    elif selector == 1:
        p1()
        p3()
    # Print Morphs
    elif selector == 2:
        url = str(raw_input("input news url:"))
        p2(url)
    # Print wordset
    elif selector == 3:
        url = str(raw_input("input news url:"))
        p4(url)
    # Frequent item set
    elif selector == 4:
        length = int(raw_input("input length of the frequent item:"))
        p5(length)
    # Association rule
    elif selector == 5:
        length = int(raw_input("input length of the frequent item:"))
        p6(length)


