import buildindex
import re
import pyrebase
import spacy
import pandas as pd
import numpy as np
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import PunktSentenceTokenizer
from nltk.tokenize import WordPunctTokenizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import sklearn.model_selection
import mglearn
import string
import sys
import pprint
from nltk.corpus import stopwords

#NEED TO TEST MORE.

#input = [file1, file2, ...]
#res = {word: {filename: {pos1, pos2}, ...}, ...}

config = {
    "apiKey": "AIzaSyDP2U8_jTBjt04U_Jt0rFA-FQx4spv0B0Q",
        "authDomain": "assembo-cb212.firebaseapp.com",
            "databaseURL": "https://assembo-cb212.firebaseio.com/",
"storageBucket": "assembo-cb212.appspot.com",
    "serviceAccount": "/Users/YuanShen1/Desktop/projects/Assembo/Unknown"
}

class Query:

	def __init__(self):
		users = self.get_resume_from_firebase()
		self.filenames = users
		self.index = buildindex.BuildIndex(users)
		self.invertedIndex = self.index.totalIndex
		self.regularIndex = self.index.regdex

	def get_resume_from_firebase(self):
		firebase = pyrebase.initialize_app(config)
		db = firebase.database()
		users = db.child("users").get()
		all_users = db.child("users").get()
		users = {}
		for user in all_users.each():
            #print(user.key()) # Morty
            #print(user.val()) # {name": "Mortimer 'Morty' Smith"}
			if("intro" in user.val()):
				users[user.key()] = user.val()['intro']
		return users
    
	def one_word_query(self, word):
		pattern = re.compile('[\W_]+')
		word = pattern.sub(' ',PorterStemmer().stem(word).lower())
		if word in self.invertedIndex.keys():
			return self.rankResults([filename for filename in self.invertedIndex[word].keys()], word, True)
		else:
			return []

	def free_text_query(self, string):
		pattern = re.compile('[\W_]+')
		string = pattern.sub(' ',string)
		result = []
		for word in string.split():
			result += self.one_word_query(word)
		return self.rankResults(list(set(result)), string)

	#inputs = 'query string', {word: {filename: [pos1, pos2, ...], ...}, ...}
	#inter = {filename: [pos1, pos2]}
	def phrase_query(self, string):
		pattern = re.compile('[\W_]+')
		string = pattern.sub(' ',string)
		listOfLists, result = [],[]
		for word in string.split():
			listOfLists.append(self.one_word_query(word))
		setted = set(listOfLists[0]).intersection(*listOfLists)
		for filename in setted:
			temp = []
			for word in [PorterStemmer().stem(word).lower() for word in string.split()]:
				temp.append(self.invertedIndex[word][filename][:])
			for i in range(len(temp)):
				for ind in range(len(temp[i])):
					temp[i][ind] -= i
			if set(temp[0]).intersection(*temp):
				result.append(filename)
		return self.rankResults(result, string, False)

	def make_vectors(self, documents):
		vecs = {}
		for doc in documents:
			docVec = [0]*len(self.index.getUniques())
			for ind, term in enumerate(self.index.getUniques()):
				docVec[ind] = self.index.generateScore(term, doc)
			vecs[doc] = docVec
		return vecs


	def query_vec(self, query):
		pattern = re.compile('[\W_]+')
		query = pattern.sub(' ',query)
		queryls = query.split()
		queryVec = [0]*len(queryls)
		index = 0
		for ind, word in enumerate(queryls):
			queryVec[index] = self.queryFreq(word, query)
			index += 1
		queryidf = [self.index.idf[word] for word in self.index.getUniques()]
		magnitude = pow(sum(map(lambda x: x**2, queryVec)),.5)
		freq = self.termfreq(self.index.getUniques(), query)
		#print('THIS IS THE FREQ')
		tf = [x/magnitude for x in freq]
		final = [tf[i]*queryidf[i] for i in range(len(self.index.getUniques()))]
		#print(len([x for x in queryidf if x != 0]) - len(queryidf))
		return final

	def queryFreq(self, term, query):
		count = 0
		#print(query)
		#print(query.split())
		for word in query.split():
			if word == term:
				count += 1
		return count

	def termfreq(self, terms, query):
		temp = [0]*len(terms)
		for i,term in enumerate(terms):
			temp[i] = self.queryFreq(term, query)
			#print(self.queryFreq(term, query))
		return temp

	def dotProduct(self, doc1, doc2):
		if len(doc1) != len(doc2):
			return 0
		return sum([x*y for x,y in zip(doc1, doc2)])

	def rankResults(self, resultDocs, query, verbose = False):
		vectors = self.make_vectors(resultDocs)
		#print(vectors)
		queryVec = self.query_vec(query)
        #print(queryVec)
		results = [[self.dotProduct(vectors[result], queryVec), result] for result in resultDocs]
        #print(results)
		results.sort(key=lambda x: x[0])
		results.reverse()
		pp = pprint.PrettyPrinter(indent=4)
		semi_results = [x for x in results if x[1] != 0]
		if verbose:
			pp.pprint(semi_results)
		results = [x[1] for x in results]
		return results


if len(sys.argv) != 2:
    print('Usage: python querytexts.py group_requirement_query')
else:
    q = Query()
    q.phrase_query(sys.argv[1])
