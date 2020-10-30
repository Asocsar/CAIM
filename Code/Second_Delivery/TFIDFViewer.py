"""
.. module:: TFIDFViewer

TFIDFViewer
******

:Description: TFIDFViewer

    Receives two paths of files to compare (the paths have to be the ones used when indexing the files)

:Authors:
    bejar

:Version: 

:Date:  05/07/2017
"""

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch.client import CatClient
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q

import argparse

import numpy as np
import os
import sys

def search_file_by_path(client, index, path):
    """
    Search for a file using its path

    :param path:
    :return:
    """
    s = Search(using=client, index=index)

    q = Q('match', path=path)  # exact search in the path field
    s = s.query(q)
    result = s.execute()

    lfiles = [r for r in result]
    if len(lfiles) == 0:
        raise NameError(f'File [{path}] not found')
    else:
        return lfiles[0].meta.id


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

    tfidfw = []

    for (t, w),(_, df) in zip(file_tv, file_df):
        tf = w / max_freq
        idf = np.log2(dcount/df)
        tfidfw.append((t, tf*idf))

    return normalize(tfidfw)

def print_term_weigth_vector(twv):
    """
    Prints the term vector and the correspondig weights
    :param twv:
    :return:
    """
    #
    # Program something here
    #
    for (t,w) in twv:
        print(t, w)


def normalize(tw):
    """
    Normalizes the weights in t so that they form a unit-length vector
    It is assumed that not all weights are 0
    :param tw:
    :return:
    """
    mod = np.sqrt(np.sum([x**2 for (_,x) in tw]))
    return [(t,w/mod) for (t,w) in tw]


def cosine_similarity(tw1, tw2):
    """
    Computes the cosine similarity between two weight vectors, terms are alphabetically ordered
    :param tw1:
    :param tw2:
    :return:
    """
    
    ind1 = 0
    ind2 = 0
    results = []
    while ind1 < len(tw1) and ind2 < len(tw2):
        (word1, w1) = tw1[ind1]
        (word2, w2) = tw2[ind2]

        if word1 == word2:
            results.append(w1*w2)
            ind1 += 1
            ind2 += 1

        elif word1 < word2:
            ind1 += 1
        else:
            ind2 += 1

    return np.sum(results)

def doc_count(client, index):
    """
    Returns the number of documents in an index

    :param client:
    :param index:
    :return:
    """
    return int(CatClient(client).count(index=[index], format='json')[0]['count'])


def analyse_files(client, index, file1, file2, print_args):
    try:

        # Get the files ids
        file1_id = search_file_by_path(client, index, file1)
        file2_id = search_file_by_path(client, index, file2)

        # Compute the TF-IDF vectors
        file1_tw = toTFIDF(client, index, file1_id)
        file2_tw = toTFIDF(client, index, file2_id)

        if print_args:
            print(f'TFIDF FILE {file1}')
            print_term_weigth_vector(file1_tw)
            print ('---------------------')
            print(f'TFIDF FILE {file2}')
            print_term_weigth_vector(file2_tw)
            print ('---------------------')

        # print(f"Similarity = {cosine_similarity(file1_tw, file2_tw):3.5f}")
        return cosine_similarity(file1_tw, file2_tw)

    except NotFoundError:
        print(f'Index {index} does not exists')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, required=True, help='Index to search')
    parser.add_argument('--files', default=None, required=False, nargs=2, help='Paths of the files to compare')
    parser.add_argument('--print', default=False, action='store_true', help='Print TFIDF vectors')

    #Indicates if given a file want to compute all the possibilities
    parser.add_argument('--path_all_files', required=False,  help='Determines if compares all the files')

    #Indicates if there is the possibility of stop
    parser.add_argument('--stop', default=False, action='store_true', required=False,  help='Allows to stop the esecution preserving all the information analyzed')

    #Arguments to check when to print and when to stop
    parser.add_argument('--iter', required=False,  help='The number of Iterations between showing the progress and stop if indicated')
    parser.add_argument('--prog', required=False,  help='How has to increase the progress of the analysis in order to show the total progress and stop if indicated')

    args = parser.parse_args()

    


    index = args.index
    client = Elasticsearch()

    if args.files:
        #Original implementation
        file1 = args.files[0]
        file2 = args.files[1]

        similarity = analyse_files(client, index, file1, file2, args.print)
        print("Similarity between", file1.split('\\')[-1], "and", file2.split('\\')[-1], " --> ", similarity)
    
    elif args.path_all_files:
        #Check that args.iter or args.prog has a value, exactly one of them
        if ((args.iter or not args.prog) and (not args.iter or args.prog)):
            raise Exception( 
                "usage: TFIDFViewer.py [-h] --index INDEX [--files FILES FILES] [--print] [--path_all_files PATH_ALL_FILES] [--stop] --iter ITER --prog PROG\n \
                Indicate ITER or PROG values, only one of them" )


        all_results = []
        path = args.path_all_files

        all_files = []
        #We collect the name of each single file
        for (_,_,filenames) in os.walk(path):
            all_files += filenames
        #This is a counter, where when file2 reach the number len(all_files) then file1 will increase by one, and file2 will be set to file1+1
        file1 = 0
        file2 = 1
        p_pre = 0
        #computes all the possibilities by a binomial formula, in order to check the total process
        binom = np.math.factorial(len(all_files))/(np.math.factorial(len(all_files) - 2)*2)
        print("Analizing {} files with {} possibilities...".format(len(all_files), binom ) )
        #While there is still some combination left
        while file1 != file2:
            #complete the path for both files
            file1_path = path + '/' + all_files[file1]
            file2_path = path + '/' + all_files[file2]

            #pick up the name of the files
            name_file1 = file1_path.split('/')[-1]
            name_file2 = file2_path.split('/')[-1]

            #analyses the similarity
            similarity = analyse_files(client, index, file1_path, file2_path, args.print)

            #stores the result
            all_results.append((name_file1, name_file2, similarity))

            #goes to the nexcombination
            file2 += 1

            #if the progress has been of --iter iterations or prog probability is set as true we check if we print the progress and stop
            if args.prog != None or file2 % int(args.iter) == 0:
                #total progress
                p = (  np.round((file1*len(all_files) + file2), 2)  / binom )*50
                #the progress that has been done since the las print
                diff = p - p_pre
                cond = True
                #if prog is set as true we check that the progress made is greater or equal than prog
                if args.prog != None:
                    cond = diff > float(args.prog)
                #if is greater or  equal we print the progress
                if cond:
                    p_pre = p
                    print("Progress", p, "%")
                    #if we want the possibility of stop we check for an answer
                    if args.stop:
                        print("Stop and print all processed information?  Yes/No")
                        R = input()
                        while R != "Yes" and R != "No":
                            print("Introduce Correct Input Yes/No")
                            R = input()
                        #if yes we end the while loop and print all results
                        if R == "Yes":
                            break
            
            if len(all_files) == file2:
                file1 += 1
                file2 = file1
                if file2 < len(all_files) - 1:
                    file2 += 1

        #we print all the information
        print('Printing information in results.txt...')
        fil = open("results_{}.txt".format(index), "w")
        for (f1, f2, sim) in sorted(all_results, key = lambda x : x[2], reverse=True):
           fil.write("Similarity between, {}, and, {},  -->  {}\n\n".format(f1,f2,sim))
        fil.close()
        print('Done')
    
    else:
        print("Please indicate a path to two files or a folder for a set of files in order to be able to compare")
