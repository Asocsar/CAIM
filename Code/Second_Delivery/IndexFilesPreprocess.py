"""
.. module:: IndexFilesPreprocess

IndexFiles
******

:Description: IndexFilesPreprocess

    Indexes a set of files under the directory passed as a parameter (--path)
    in the index name passed as a parameter (--index)

    Add configuration of the default analizer: tokenizer  (--token) and filter (--filter)

    --filter must be always the last flag

    If the index exists it is dropped and created new

    Documentation for the analyzer configuration:

    https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis.html


"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import NotFoundError
import argparse
import os
import codecs
from elasticsearch_dsl import Index, analyzer, tokenizer
import CountWords
import matplotlib.pyplot as plt
import numpy as np

def generate_files_list(path):
    """
    Generates a list of all the files inside a path
    :param path:
    :return:
    """
    if path[-1] == '/':
        path = path[:-1]

    lfiles = []

    for lf in os.walk(path):
        if lf[2]:
            for f in lf[2]:
                lfiles.append(lf[0] + '/' + f)
    return lfiles



def generate_index(index, ldocs, token, filters, all_pos):
    """
    Generates a index given a name for the index, a set of documents, a posible token, a filter and in case
    that all_pos is true it prints some information in order to visualize the process
    :param index, ldocs, toke, filters, all_pos:
    :return nothing, only generates an index:
    """

    if all_pos:
        print("GENERATING INDEX...", index)
    
    client = Elasticsearch()

    # Tokenizers: whitespace classic standard letter
    my_analyzer = analyzer('default',
                           type='custom',
                           tokenizer=tokenizer(token),
                           filter=filters
                           )

    try:
        # Drop index if it exists
        ind = Index(index, using=client)
        ind.delete()
    except NotFoundError:
        pass
    # then create it
    ind.settings(number_of_shards=1)
    ind.create()
    ind = Index(index, using=client)

    # configure default analyzer
    ind.close()  # index must be closed for configuring analyzer
    ind.analyzer(my_analyzer)

    # configure the path field so it is not tokenized and we can do exact match search
    client.indices.put_mapping(doc_type='document', index=index, include_type_name=True, body={
        "properties": {
            "path": {
                "type": "keyword",
            }
        }
    })

    ind.save()
    ind.open()
    print("Index settings=", ind.get_settings())
    # Bulk execution of elastic search operations (faster than executing all one by one)
    print('Indexing ...')
    bulk(client, ldocs)
    client.transport.close()
    
    
def plot_data(all_words_data, title):
    """
    Plot a file with the strucutre (DocumentName, Number) in a a bar plot for example in order to see the  
    maximum frequency or amount of words
    :param path:
    :return:
    """
    type_an = np.array([x.split(',')[0] for x in all_words_data])
    words_cant = np.array([int(x.split(',')[1].split(' ')[1]) for x in all_words_data])

    

    fig, ax = plt.subplots(figsize=(16,6))
    ax.set_title(title)
    plt.yticks(fontsize='xx-small')
    plt.xticks(rotation='vertical')
    ax.barh(type_an, words_cant, color = ['gray' for _ in range(7)] + ['coral' for _ in range(7)] + 
                                        ['mediumorchid' for _ in range(7)] + ['gold' for _ in range(7)])

    plt.show() 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True, default=None, help='Path to the files')
    parser.add_argument('--index', required=True, default=None, help='Index for the files')
    parser.add_argument('--token', default='standard', choices=['standard', 'whitespace', 'classic', 'letter'],
                        help='Text tokenizer')
    parser.add_argument('--all_posibilities', required=False, default=False,  action='store_true', help='Generate all the possible combinations individuale and finally creates one\
                                                                                                        with the size of each possibility')
    parser.add_argument('--filter', default=['lowercase'], nargs=argparse.REMAINDER, help='Text filter: lowercase, '
                                                                                          'asciifolding, stop, porter_stem, kstem, snowball')

    args = parser.parse_args()

    path = args.path
    index = args.index

    # check if the filters are valid
    for f in args.filter:
        if f not in ['lowercase', 'asciifolding', 'stop', 'stemmer', 'porter_stem', 'kstem', 'snowball']:
            raise NameError(
                'Invalid filter must be a subset of: lowercase, asciifolding, stop, porter_stem, kstem, snowball')
    
    ldocs = []

    # Reads all the documents in a directory tree and generates an index operation for each
    lfiles = generate_files_list(path)
    print('Indexing %d files' % len(lfiles))
    print('Reading files ...')
    for f in lfiles:
        ftxt = codecs.open(f, "r", encoding='iso-8859-1')
        text = ''
        for line in ftxt:
            text += line
        # Insert operation for a document with fields' path' and 'text'
        ldocs.append({'_op_type': 'index', '_index': index, 'path': f, 'text': text})
    
    #check if we want to compute all the possibilities (this is a lite version in order to speed-up the program)
    if args.all_posibilities:
        all_filters = ['lowercase', 'asciifolding', 'stop', 'stemmer', 'porter_stem', 'kstem', 'snowball']
        for tok in ['standard', 'whitespace', 'classic', 'letter']:
            for filt_select in all_filters:
                #creates a new name indicating which filters have been used and which token has been used
                index_in = index + '_' + tok + '_' + filt_select
                #changes the index for all the documents
                ldocs_mod = [{'_op_type' : L['_op_type'], '_index': index_in, 'path': L['path'], 'text': L['text']} for L in ldocs]
                #generate the index
                generate_index(index_in, ldocs_mod, tok, filt_select, True)
                print("END OF GENERATING INDEX...", index_in)
                #call COuntWords to analyze the frequences and the number of word, maximum rec, and store it all into a file
                CountWords.analyze_index(index_in, False)

        all_words = open('countWords_all.txt', 'r')
        all_words_data = all_words.readlines()
        all_words.close()

        #print the bar for the number of different words
        plot_data(all_words_data, "Number of words")

        all_words = open('countWords_max.txt', 'r')
        all_words_data = all_words.readlines()
        all_words.close()
        #print the bar for the number of Maximum Frec
        plot_data(all_words_data, "MaximumFrec")
        


    else:
        #original implementation
        generate_index(index, ldocs, args.token, args.filter, False)


