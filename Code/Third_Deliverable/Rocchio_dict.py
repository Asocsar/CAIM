from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q
import pandas as pd
import numpy as np
from elasticsearch.client import CatClient


def normalize(tw):
    """
    Normalizes the weights in t so that they form a unit-length vector
    It is assumed that not all weights are 0
    :param tw:
    :return:
    """
    mod = np.sqrt(np.sum([x**2 for x in tw.values()]))
    return {t: tw[t]/mod for t in tw.keys()}


def document_term_vector(client, index, id):
    """
    Returns the term vector of a document and its statistics a two sorted list of pairs (word, count)
    The first one is the frequency of the term in the document, the second one is the number of documents
    that contain the term

    :param client:
    :param index:
    :param id:
    :return:
    """
    termvector = client.termvectors(index=index, id=id, fields=['text'],
                                    positions=False, term_statistics=True)

    file_td = {}
    file_df = {}

    if 'text' in termvector['term_vectors']:
        for t in termvector['term_vectors']['text']['terms']:
            file_td[t] = termvector['term_vectors']['text']['terms'][t]['term_freq']
            file_df[t] = termvector['term_vectors']['text']['terms'][t]['doc_freq']
    return sorted(file_td.items()), sorted(file_df.items())


def doc_count(client, index):
    """
    Returns the number of documents in an index

    :param client:
    :param index:
    :return:
    """
    return int(CatClient(client).count(index=[index], format='json')[0]['count'])

def toTFIDF(client, index, file_id):
    """
    Returns the term weights of a document

    :param file:
    :return:
    """

    # Get the frequency of the term in the document, and the number of documents
    # that contain the term
    file_tv, file_df = document_term_vector(client, index, file_id)

    max_freq = max([f for _, f in file_tv])

    dcount = doc_count(client, index)

    tfidfw = {}

    for (t, w),(_, df) in zip(file_tv, file_df):
        tf = w / max_freq
        idf = np.log2(dcount/df)
        tfidfw[t]= tf*idf

    return tfidfw

def div_all_map(elem, value):
    return elem/value

def search(words_set, index, client, K, R):

    s = Search(using=client, index=index)
    set_query_elements = [k+'^'+str(v) for (k,v) in zip(words_set.keys(),words_set.values())]
    
    q = Q('query_string',query=set_query_elements[0]) 
    for elem in set_query_elements[1:]:
        q &= Q('query_string',query=elem)

    s = s.query(q)
    response = s[0:K].execute()
    results = {}
    for r in response:  # only returns a specific number of results
        tfidf = toTFIDF(client, index, r.meta.id)
        results = {t: tfidf.get(t, 0) + results.get(t, 0) for t in set(tfidf) | set(results)}
    
    results = {t: results[t]/K for t in results.keys()}
    return normalize(results)

'''Declaration of variables to be used later'''

index = 'news'
beta = 0.6
alpha = 0.4
initial_query = input().split(' ')
nrounds = int(input())


l1 = [x for x in initial_query if '^' in x]
l2 = [x + '^1' for x in initial_query if '^' not in x]
words = {k.split('^')[0]:int(k.split('^')[1]) for k in l1+l2}
words = normalize(words)
k = 60
client = Elasticsearch()
R = 3
for _ in range(nrounds):
    Res = search(words, index, client, k, R)
    Res = {t:Res[t]*beta for t in Res.keys()}
    words = {k:words[k]*alpha for k in words.keys()}
    words = {t: words.get(t, 0) + Res.get(t, 0) for t in set(words) | set(Res)}
    words = {key: value for key, value in words.items() if value in sorted(set(words.values()), reverse=True)[:R]}
    words = normalize(words)
print(words)

s = Search(using=client, index=index)
set_query_elements = [k+'^'+str(v) for (k,v) in zip(words.keys(),words.values())]
q = Q('query_string',query=set_query_elements[0]) 

for elem in set_query_elements:
    q &= Q('query_string',query=elem)

s = s.query(q)
response = s.execute()
for r in response:  
    print(f'PATH= {r.path}')