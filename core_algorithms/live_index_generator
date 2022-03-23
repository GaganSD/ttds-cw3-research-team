#!/usr/bin/env python

from math import ceil
import os
import sys
import json
import pickle
import pandas as pd

import preprocessing
sys.path.append("..")
from mongoDB_api_live_index import MongoDBClient
import argparse
import logging
from collections import defaultdict

from concurrent.futures import ThreadPoolExecutor
import multiprocessing

from tqdm import tqdm

logging.basicConfig(filename='result.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class IndexGenerator:
    def __init__(self, client_ip = "34.142.18.57", activate_stemming = True, activate_stop = False, start_index=0, local_dataset=None, source_name="", identifier=""):
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
        self.client = MongoDBClient(client_ip)
        self.source_name = source_name
        self.identifier = identifier
        self.temp = dict()

    def clean_indexing(self):
        for i in range(self.local_dataset.shape[0]):
            dataset = self.local_dataset.iloc[i]

            temp_id = self.client.create_unique_identifier(self.source_name, dataset[self.identifier])
            
            matches = list(self.client.get_one("paper", {'_id': temp_id}, fields: list))
            
            if len(matches) > 0:
                sentence = str(dataset['title']) + ' ' + str(dataset['abstract']) + ' ' + str(dataset['text'])

                preprocessed = preprocessing.preprocess(sentence, stemming=self.activate_stemming, stop=self.activate_stop)
                preprocessed = list(filter(None, preprocessed))

                for term in set(preprocessed):
                    self.client.remove_doc_index(term=term, doc_id=temp_id)
    
    def run_indexing(self):
        """ This function gets the sentences from db and updates the inverted index in db by iterating the sentences.
        """

        if self.local_dataset is None:
            if not self.client.success:
                return

            chunk_size = 100000
            chunk_num = ceil(23254165/chunk_size)
            for i in tqdm(range(chunk_num)):
                if i < self.start:
                    continue
#                 executor = ThreadPoolExecutor()

                # logger.info("processing chunk %i / %i", i, chunk_num)
                cursor= self.client.get_data("paper", {}, ['title', 'abstract', 'text'], 
                                i*chunk_size, chunk_size)
                
#                 m = multiprocessing.Manager()
#                 lock = m.Lock()

                for doc in cursor:
                    text = doc.get('title', "") + ' ' 
                    text += str(doc.get('abstract', "")) + ' ' 
                    text += str(doc.get('text', ""))
                    id = doc.get('_id')
#                     executor.submit(self.__load_tempfile, id, text, lock)
                    self.__load_tempfile(id, text)

#                 executor.shutdown(wait=True)
                # logger.info("saving chunk to db %i / %i", i, chunk_num)
                self.__save_db()

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
#             with lock:
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
#         executor = ThreadPoolExecutor()
        for term, content in tqdm(self.temp.items()):
#             executor.submit(self.client.update_index, term, content['docs'])
            self.client.update_index(term, content['docs'])
#         executor.shutdown(wait=True)
        self.temp.clear()

def run_with_arguments(stem, stop, start, local_dataset=None):
    if local_dataset is None:
        indexGen = IndexGenerator(activate_stop=stop, activate_stemming=stem, start_index=start, local_dataset=None)
    else:
        df = pd.read_csv(local_dataset)
        indexGen = IndexGenerator(activate_stop=stop, activate_stemming=stem, start_index=start, local_dataset= df)
    indexGen.run_indexing()


if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='Inverted Index Generator')
    parser.add_argument('--stemming', nargs="?", type=str, default='True', help='Activate stemming')
    parser.add_argument('--remove_stopwords', nargs="?", type=str, default='True', help='Remove stopwords')
    parser.add_argument('--start', nargs="?", type=int, default=0, help='Start batch index')
    parser.add_argument('--local_dataset', type=str, default=True, help='Local dataset path')
    args = parser.parse_args()

    run_with_arguments(eval(args.stemming), eval(args.remove_stopwords), args.start)
