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
import numpy as np

import argparse

def analyze_index(index, alpha):
    print("ANALYZING INDEX", index)
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


        fil = open("countWords_{}.txt".format(index), "w")
        tot = open("countWords_all.txt", "a")
        maxima = open("countWords_max.txt", "a")
        for pal, cnt in sorted(lpal, key=lambda x: x[0 if alpha else 1]):
            try:
                fil.write("{}, {}\n".format(cnt, pal.decode("utf-8")))
                #print(f'{cnt}, {pal.decode("utf-8")}')
            except:
                pass
        fil.write('\n--------------------\n')
        fil.write('{} Words\n'.format(len(lpal)))
        tot.write('{}, {} Words\n'.format(index, len(lpal)))
        maxima.write('{}, {} Frec\n'.format(index, np.max([cnt for pal, cnt in sorted(lpal, key=lambda x: x[0 if alpha else 1])])))
        fil.close()
        maxima.close()
        tot.close()
        print("END OF ANALYZING INDEX", index)
        # print(f'{len(lpal)} Words')
    except NotFoundError:
        print(f'Index {index} does not exists')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, required=True, help='Index to search')
    parser.add_argument('--alpha', action='store_true', default=False, help='Sort words alphabetically')

    args = parser.parse_args()
    index = args.index
    

    analyze_index(index, args.alpha)

