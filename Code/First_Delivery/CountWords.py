

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from elasticsearch.exceptions import NotFoundError, TransportError
import zips
import heaps
import argparse
import numpy as np


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, required=True, help='Index to search')
    parser.add_argument('--alpha', action='store_true', default=False, help='Sort words alphabetically')
    args = parser.parse_args()

    index = args.index
    datos_zips = []
    datos_heaps = []
    

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


            local_data_zips = []
            local_data_heaps = []
            sub_total = 0
            for pal, cnt in sorted(lpal, key=lambda x: x[0 if args.alpha else 1]):
                local_data_zips.append(([pal.decode("utf-8")], cnt))
                local_data_heaps.append(cnt)
                if i == -1:
                    total += cnt
                else:
                    sub_total += cnt
                #print(f'{cnt}, {pal.decode("utf-8")}')
            datos_zips.append(local_data_zips)
            datos_heaps.append(local_data_heaps)
            #print('--------------------')
            #print(f'{len(lpal)} Words')
            i += 1
            if sub_total/total == 1:
                print("Loaded all index")
                break

        except NotFoundError:
            print(f'Index {index} does not exists')
            break


    zips.show(datos_zips[0], index)
    heaps.show(datos_heaps[1:], index)