"""
.. module:: IndexFiles

IndexFiles
******

:Description: IndexFiles

    Indexes a set of files under the directory passed as a parameter (--path)
    in the index name passed as a parameter (--index)

    If the index exists it is dropped and created new

    The documents are created with a 'path' and a 'text' fields

:Authors:
    bejar

:Version: 

:Date:  23/06/2017
"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Index
from Clean import *
import argparse
import os
import codecs

__author__ = 'bejar'


def generate_files_list(path):
	"""
		Generates a list of all the files inside a path (recursivelly)
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


# Reads all the documents in a directory tree and generates an index operation for each
def indexTree(obj, lfiles):
	ldocs = []
	for f in lfiles:
		ftxt = codecs.open(f, "r", encoding='iso-8859-1')
		text = ''
		for line in ftxt:
			text += line

		# Insert operation for a document with fields' path' and 'text'
		ldocs.append({'_op_type': 'index', '_index': index, 'path': f, 'text': obj(text).clean()})
	return ldocs


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--path', required=True, default=None, help='Path to the files')
	parser.add_argument('--index', required=True, default=None, help='Index for the files')

	args = parser.parse_args()

	path = args.path
	index = args.index

	lfiles = generate_files_list(path)
	print('Indexing %d files' % len(lfiles))
	print('Reading files ...')

	obj = Arxiv
	if index == "news":
		obj = News
	elif index == "novels":
		obj = Novels
	ldocs = indexTree(obj, lfiles)
	#number of subindex
	iterations = int(len(ldocs)/10)
	nsub = [x for x in range(1, len(ldocs), iterations)]
	print(nsub)
	if iterations-1 not in nsub:
		nsub += [iterations-1]

	# Working with ElasticSearch
	client = Elasticsearch()

	#create subindices
	sub_data = []
	sub_ind = []
	for i, selec in enumerate(nsub):
		name = index + '_' + str(i)
		all_sub_data = []
		for j in range(0, selec):
			data = ldocs[j].copy()
			data['_index'] = name
			all_sub_data.append(data)
		
		sub_data.append(all_sub_data)
		try:
			ind = Index(name, using=client)
			ind.delete()
			ind.settings(number_of_shards=1)
			ind.create()
			print('Indexing subindex', i)
			bulk(client, sub_data[i])
			
		except NotFoundError:
			print('created ', name)
			ind.settings(number_of_shards=1)
			ind.create()
			print('Indexing subindex', i)
			bulk(client, sub_data[i])

	# then create it
	try:
		# Drop index if it exists
		ind = Index(index, using=client)
		ind.delete()
	except NotFoundError:
		pass

	ind.settings(number_of_shards=1)
	ind.create()

	# Bulk execution of elasticsearch operations (faster than executing all one by one)
	print('Indexing ...')
	bulk(client, ldocs)
