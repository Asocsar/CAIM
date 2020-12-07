"""
.. module:: MRKmeansDef

MRKmeansDef
*************

:Description: MRKmeansDef

    

:Authors: bejar
    

:Version: 

:Created on: 17/07/2017 7:42 

"""

from mrjob.job import MRJob
from mrjob.step import MRStep

import numpy as np
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class MRKmeansStep(MRJob):
    prototypes = {}
    

    def jaccard(self, prot, doc):
        """
        Compute here the Jaccard similarity between  a prototype and a document
        prot should be a list of pairs (word, probability)
        doc should be a list of words
        Words must be alphabeticaly ordered

        The result should be always a value in the range [0,1]
        """
        
        
        '''cross = 0
        sqn1 = 0
        sqn2 = 0
                                
        
        i, j = (0,0)

        while i < len(prot) and j < len(doc):
            if prot[i][0] == doc[j]:
                cross = cross + prot[i][1]
                sqn1 += prot[i][1]**2
                sqn2 += 1
                i += 1
                j += 1

            elif prot[i][0] < doc[j]:
                sqn1 += prot[i][1]**2
                i += 1
            
            elif prot[i][0] > doc[j]:
                sqn2 += 1
                j += 1
        
        
        while i < len(prot):
            sqn1 += prot[i][1]**2
            i += 1
        
        while j < len(doc):
            sqn2 += 1
            j+= 1'''
        

        cross = sum([p for (w,p) in prot if w in doc])
        sqn1 = sum([1 for _ in doc])
        sqn2 = sum([x**2 for (_,x) in prot])

        return cross / (sqn1 + sqn2 - cross)

    def configure_args(self):
        """
        Additional configuration flag to get the prototypes files

        :return:
        """
        super(MRKmeansStep, self).configure_args()
        self.add_file_arg('--prot')

    def load_data(self):
        """
        Loads the current cluster prototypes

        :return:
        """
        f = open(self.options.prot, 'r', encoding='utf8')
        for line in f:
            cluster, words = line.split(':')
            cp = []
            for word in words.split():
                cp.append((word.split('+')[0], float(word.split('+')[1])))
            self.prototypes[cluster] = cp

        f.close()


    def assign_prototype(self, _, line):
        """
        This is the mapper it should compute the closest prototype to a document

        Words should be sorted alphabetically in the prototypes and the documents

        This function has to return at list of pairs (prototype_id, document words)

        You can add also more elements to the value element, for example the document_id
        """

        # Each line is a string docid:wor1 word2 ... wordn
        doc, words = line.split(':')
        lwords = words.split()
        #
        # Compute map here
        #
        minDistance = -1
        assignedPrototype = ''
        for k in self.prototypes:
            distance = self.jaccard(self.prototypes[k], lwords)
            if minDistance == -1 or distance < minDistance:
                minDistance = distance
                assignedPrototype = k


        # Return pair key, value
        yield assignedPrototype, (doc,lwords)

    def aggregate_prototype(self, key, values):
        """
        input is cluster and all the documents it has assigned
        Outputs should be at least a pair (cluster, new prototype)

        It should receive a list with all the words of the documents assigned for a cluster

        The value for each word has to be the frequency of the word divided by the number
        of documents assigned to the cluster

        Words are ordered alphabetically but you will have to use an efficient structure to
        compute the frequency of each word

        :param key:
        :param values:
        :return:
        """
        documents = []
        frequencyWords = {}
        for (doc, words) in values:
            documents.append(doc)
            for word in words:
                if word in frequencyWords:
                    frequencyWords[word] += 1
                else:
                    frequencyWords[word] = 1
        
        newPrototype = list(sorted([(word, frequencyWords[word]/len(documents)) for word in frequencyWords], key=lambda x: x[1]))
        yield key, (sorted(documents), newPrototype)

    def steps(self):
        return [MRStep(mapper_init=self.load_data, mapper=self.assign_prototype,
                       reducer=self.aggregate_prototype)
            ]


if __name__ == '__main__':
    MRKmeansStep.run()