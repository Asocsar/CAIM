"""
.. module:: MRKmeans

MRKmeans
*************

:Description: MRKmeans

    Iterates the MRKmeansStep script

:Authors: bejar
    

:Version: 

:Created on: 17/07/2017 10:16 

"""

from MRKmeansStep import MRKmeansStep
import shutil
import argparse
import os
import time
from mrjob.util import to_lines
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prot', default='prototypes.txt', help='Initial prototpes file')
    parser.add_argument('--docs', default='documents.txt', help='Documents data')
    parser.add_argument('--iter', default=20, type=int, help='Number of iterations')
    parser.add_argument('--ncores', default=4, type=int, help='Number of parallel processes to use')

    args = parser.parse_args()
    assign = {}

    # Copies the initial prototypes
    cwd = os.getcwd()
    print(cwd)
    shutil.copy(cwd + '/' + args.prot, cwd + '/prototypes0.txt')

    nomove = False  # Stores if there has been changes in the current iteration
    for i in range(args.iter):
        tinit = time.time()  # For timing the iterations

        # Configures the script
        print('Iteration %d ...' % (i + 1))
        # The --file flag tells to MRjob to copy the file to HADOOP
        # The --prot flag tells to MRKmeansStep where to load the prototypes from
        mr_job1 = MRKmeansStep(args=['-r', 'local', args.docs,
                                     '--file', cwd + '/prototypes%d.txt' % i,
                                     '--prot', cwd + '/prototypes%d.txt' % i,
                                     #'--vocab', cwd + '/vocabulary.txt',
                                     '--num-cores', str(args.ncores)])

        # Runs the script
        with mr_job1.make_runner() as runner1:
            runner1.run()
            new_assign = {}
            new_proto = {}
            # Process the results of the script iterating the (key,value) pairs
            for cluster, vector in mr_job1.parse_output(runner1.cat_output()):
                #print(vector)
                new_assign[cluster] = vector[0]
                new_proto[cluster] = vector[1]
                # You should store things here probably in a datastructure

            list_1 = sorted(list(new_assign.values()))
            list_2 = sorted(list(assign.values()))
            nomove = (list_1 == list_2)
            assign = new_assign

            # If your scripts returns the new assignments you could write them in a file here
            f = open(cwd + '/assign%d.txt' % i, 'w')
            for k in sorted(new_assign):
                f.write('Cluster {}:'.format(k))
                for doc in new_assign[k]:
                    f.write('\t File {}\n'.format(doc))
            f.close()

            # You should store the new prototypes here for the next iteration
            f = open(cwd + '/prototypes%d.txt' % (i+1), 'w')
            for k in sorted(new_proto):
                S = k + ':'
                for (word,weight) in new_proto[k]:
                    S += word + '+' + str(weight) + ' '
                f.write(S[:-1] + '\r\n')
            f.close()
            # If you have saved the assignments, you can check if they have changed from the previous iteration

        print("Time= {} seconds".format((time.time() - tinit)))

        if args.iter-1 == i or nomove:  # If there is no changes in two consecutive iteration we can stop
            f = open(cwd + '/prototypes_final.txt', 'w')
            for k in sorted(new_proto):
                S = k + ':'
                for (word,weight) in new_proto[k]:
                    S += word + '+' + str(weight) + ' '
                f.write(S[:-1] + '\r\n')
            f.close()
            print("Algorithm converged")
            break

    # Now the last prototype file should have the results
