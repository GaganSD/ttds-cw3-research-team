#!/usr/bin/env python

import os
import sys
import json
import pickle
import pandas as pd

import preprocessing
from mongoDB_API import MongoDBClient
import argparse
import logging
from collections import defaultdict

from tqdm import tqdm

logging.basicConfig(filename='result.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class IndexGenerator:
    def __init__(self, activate_stemming = True, activate_stop = False, start_index=0, local_dataset=None):
        """ This class reaeds the documents from db, generates an inverted index and saves it into db.
        
        Keyword Arguments:
            activate_stemming {bool} -- True enables the stemming function over the terms (default: {True})
            activate_stop {bool} -- True enables removing stop words (default: {False})
            local_dataset -- None when we are using mongoDB
        """
        self.activate_stemming = activate_stemming
        self.activate_stop = activate_stop
        self.start = start_index
        self.local_dataset = local_dataset
        self.client = MongoDBClient("34.142.18.57")
        
        self.temp = dict()
    
    def run_indexing(self):
        """ This function gets the sentences from db and updates the inverted index in db by iterating the sentences.
        """

        if self.local_dataset is None:
            if not self.client.success:
                return

            cnt = 0
            cursor, num = self.client.get_data("dataset", {}, ['title', 'description', 'text'])
            t = tqdm(total=num)

            for doc in cursor:
                # print(doc["_id"])
                text = doc.get('title', "") + ' '
                text += str(doc.get('subtitle', "")) + ' ' 
                text += str(doc.get('description', "")) + ' ' 
                text += str(doc.get('abstract', "")) + ' ' 
                text += str(doc.get('text', ""))
                self.__load_tempfile(doc.get('_id'), text)
                t.update()
                cnt += 1
                if cnt % 100000 == 0:
                    self.__save_db()
            if len(self.temp) > 0:
                self.__save_db()

            t.close()

        else:
            for i in range(self.local_dataset.shape[0]):
                dataset = self.local_dataset.iloc[i]
                sentence = str(dataset['title']) + ' ' + str(dataset['subtitle']) + ' ' + str(dataset['description'])
                self.__load_tempfile(ds_id = i, sentence = sentence)
            self.__save_pickle('last')
            

    def __load_tempfile(self, ds_id, sentence):
        preprocessed = preprocessing.preprocess(sentence, stemming=self.activate_stemming, stop=self.activate_stop)
        preprocessed = list(filter(None, preprocessed))

        word_count = len(preprocessing.preprocess(sentence, stemming=False, stop=False))
        
        for term in set(preprocessed):
            positions = [n for n,item in enumerate(preprocessed) if item==term]
            self.temp[term] = self.temp.get(term, {
                'term': term,
                'doc_count': 0,
                'docs': list()
            })
            self.temp[term]['doc_count'] += 1
            self.temp[term]['docs'].append({
                        'id': ds_id,
                        'len': word_count,
                        'pos': positions
                    })
                    

    def __save_pickle(self, name):
        with open(name + '.pickle', 'wb') as handle:
            pickle.dump(list(self.temp.values()), handle, protocol=pickle.HIGHEST_PROTOCOL)
        self.temp.clear()

    def __save_db(self):
        for term, content in tqdm(self.temp.items()):
            self.client.update_index(term, content['docs']);
        self.temp.clear()

def run_with_arguments(stem, stop, start, local_dataset=None):
    if local_dataset is None:
        indexGen = IndexGenerator(activate_stop=stop, activate_stemming=stem, start_index=start, local_dataset=None)
    else:
        df = pd.read_csv(local_dataset)
        indexGen = IndexGenerator(activate_stop=stop, activate_stemming=stem, start_index=start, local_dataset= df)
    indexGen.run_indexing()

parser = argparse.ArgumentParser(description='Inverted Index Generator')
parser.add_argument('--stemming', nargs="?", type=str, default='True', help='Activate stemming')
parser.add_argument('--remove_stopwords', nargs="?", type=str, default='True', help='Remove stopwords')
parser.add_argument('--start', nargs="?", type=int, default=0, help='Start batch index')
parser.add_argument('--local_dataset', type=str, default=True, help='Local dataset path')
args = parser.parse_args()

run_with_arguments(eval(args.stemming), eval(args.remove_stopwords), args.start)