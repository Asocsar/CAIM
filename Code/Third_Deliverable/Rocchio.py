from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q
import pandas as pd
import numpy as np
from elasticsearch.client import CatClient


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


def search(words_set, index, client, K, R):

    s = Search(using=client, index=index)
    
    query_elements = [k + '^' + str(words_set[k].values[0]) for k in words_set.columns]
   

    q = Q('query_string',query=query_elements[0]) 

    for elem in query_elements[1:]:
   
        q &= Q('query_string',query=elem)

    s = s.query(q)
    response = s[0:K].execute()
    results = pd.DataFrame(index=['Weight'])
    for r in response:  # only returns a specific number of results
        df = pd.DataFrame(toTFIDF(client, index, r.meta.id), index=['Weight'])
        df = df.div(np.sqrt(df.pow(2).sum(axis=1)), axis=0)
        results = results.add(df, fill_value=0)
    
    results = results.div(K).sort_values(by ='Weight', axis=1, ascending=False)

    return results
        

'''Declaration of variables to be used later'''

index = 'news'
beta = 0.7
alpha = 0.3
initial_query = input().split(' ')
words = pd.DataFrame(index=['Weight'])
for elem in initial_query:
    if '^' in elem:
        words[elem.split('^')[0]] = int(elem.split('^')[1])
    else:
        words[elem.split('^')[0]] = 1
words = words.div(np.sqrt(words.pow(2).sum(axis=1)), axis=0)
k = 60
client = Elasticsearch()
R = 4
nrounds = int(input())
for _ in range(nrounds):
    Res = search(words, index, client, k, R)*beta
    words = words*alpha
    words = words.div(np.sqrt(words.pow(2).sum(axis=1)), axis=0)
    words = words.add(Res, fill_value=0).sort_values(by ='Weight', axis=1, ascending=False)
    words = words[words.columns[:R]]
print(words)



s = Search(using=client, index=index)
q = Q('query_string',query=words.columns[0] + '^' + str(words[words.columns[0]].values[0])) 

for elem in words.columns[1:]:
    q &= Q('query_string',query=elem + '^' + str(words[elem].values[0]))

s = s.query(q)
response = s.execute()
for r in response:  # only returns a specific number of results
    print(f'PATH= {r.path}')
