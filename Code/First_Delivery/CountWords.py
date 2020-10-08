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

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from elasticsearch.exceptions import NotFoundError, TransportError
import zips
import heaps
import argparse
import numpy as np

__author__ = 'bejar'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, required=True, help='Index to search')
    parser.add_argument('--alpha', action='store_true', default=False, help='Sort words alphabetically')
    args = parser.parse_args()

    index = args.index
    datos = []
    

    i = -1
    total = 0
    while True:
        j = i
        add = ''
        if i >= 0:
            add = '_' + str(i)
        index_obj = index + add
        print('Loading index ', index_obj)
        try:
            client = Elasticsearch()
            voc = {}
            sc = scan(client, index=index_obj, query={"query" : {"match_all": {}}})
            for s in sc:
                try:
                    tv = client.termvectors(index=index_obj, id=s['_id'], fields=['text'])
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


            local_data = []
            sub_total = 0
            for pal, cnt in sorted(lpal, key=lambda x: x[0 if args.alpha else 1]):
                local_data.append(([pal.decode("utf-8")], cnt))
                if i == -1:
                    total += cnt
                else:
                    sub_total += cnt
                #print(f'{cnt}, {pal.decode("utf-8")}')
            datos.append(local_data)
            #print('--------------------')
            #print(f'{len(lpal)} Words')
            i += 1
            print(total, sub_total)
            if sub_total/total == 1:
                print("Loaded all index")
                break

        except NotFoundError:
            print(f'Index {index} does not exists')
            break


    zips.show(datos[0])
    #heaps.show(datos[1:])