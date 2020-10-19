"""
.. module:: CountWords

CountWords
*************

:Description: CountWords

    Generates a list with the counts and the words in the 'text' field of the documents in an index

:Authors: bejar
    

:Version: 

:Created on: 04/07/2017 11:58 

"""

from __future__ import print_function
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from elasticsearch.exceptions import NotFoundError, TransportError

import argparse

def analyze_index(index):
    try:
        client = Elasticsearch()
        voc = {}
        sc = scan(client, index=index, query={"query" : {"match_all": {}}})
        for s in sc:
            try:
                tv = client.termvectors(index=index, id=s['_id'], fields=['text'])
                if 'text' in tv['term_vectors']:
                    for t in tv['term_vectors']['text']['terms']:
                        if t in voc:
                            voc[t] += tv['term_vectors']['text']['terms'][t]['term_freq']
                        else:
                            voc[t] = tv['term_vectors']['text']['terms'][t]['term_freq']
            except TransportError:
                pass
        lpal = []

        for v in voc:
            lpal.append((v.encode("utf-8", "ignore"), voc[v]))


        for pal, cnt in sorted(lpal, key=lambda x: x[0 if args.alpha else 1]):
            try:
                print(f'{cnt}, {pal.decode("utf-8")}')
            except:
                pass
        print('--------------------')
        print(f'{len(lpal)} Words')
    except NotFoundError:
        print(f'Index {index} does not exists')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, required=True, help='Index to search')
    parser.add_argument('--alpha', action='store_true', default=False, help='Sort words alphabetically')
    parser.add_argument('--all_posibilities', required=False, default=False,  action='store_true', help='Analyses all the possible combinations of filter and tokens if generated previously')
    args = parser.parse_args()

    index = args.index

    all_filters = ['lowercase', 'asciifolding', 'stop', 'stemmer', 'porter_stem', 'kstem', 'snowball']
    tokens = ['standard', 'whitespace', 'classic', 'letter']

    if args.all_posibilities:
        for tok in tokens:
            for filt_cant in range(1, len(all_filters)):
                filters = all_filters[:filt_cant]
                index_in = index + '_' + token + '_' + '_'.join([str(x) for x in filters])
                analyze_index(index_in)