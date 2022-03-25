#!/usr/bin/env python

import os
import sys
import json
import pickle
import pandas as pd

import preprocessing
import argparse
import logging
from collections import defaultdict

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

        self.temp = dict()
    
    def run_indexing(self):
        """ This function gets the sentences from db and updates the inverted index in db by iterating the sentences.
        """
        if self.local_dataset is None:
            batch = 100000
            for i in range(self.start, 776):
                logging.info("loading: " + str(i+1) + "/" + str(776))
                cursors = database_functions.get_sentences_cursors(i * batch, batch)
                for cursor in cursors:
                    self.__load_tempfile(cursor.get('_id'), cursor.get('sentence'), cursor.get('movie_id'))
                if (i+1)%15 == 0:
                    self.__save_pickle(str(i-14) + "-" + str(i+1) + "-insert")
            self.__save_pickle("last")
        else:
            for i in range(self.local_dataset.shape[0]):
                dataset = self.local_dataset.iloc[i]
                sentence = str(dataset['title']) + ' ' + str(dataset['subtitle']) + ' ' + str(dataset['description'])
                self.__load_tempfile(ds_id = i, sentence = sentence)
            self.__save_pickle('core_algorithms/ir_eval/last')
            

    def __load_tempfile(self, ds_id, sentence):
        preprocessed = preprocessing.preprocess(sentence, stemming=self.activate_stemming, stop=self.activate_stop)
        preprocessed = list(filter(None, preprocessed))

        word_count = len(preprocessing.preprocess(sentence, stemming=False, stop=False))
        
        for term in set(preprocessed):
            positions = [n for n,item in enumerate(preprocessed) if item==term]
            self.temp[term] = self.temp.get(term, {
                'term': term,
                'dataset_count': 0,
                'dataset': defaultdict(dict)
            })
            self.temp[term]['dataset_count'] += 1
            self.temp[term]['dataset'][ds_id] = {
                        'len': word_count,
                        'pos': positions
                    }
                    

    def __save_pickle(self, name):
        with open(name + '.pickle', 'wb') as handle:
            pickle.dump(list(self.temp.values()), handle, protocol=pickle.HIGHEST_PROTOCOL)
        self.temp.clear()

def run_with_arguments(stem, stop, start, local_kaggle_dataset=None, local_paperwithcode_dataset=None,
                       local_uci_dataset=None, local_edi_dataset=None):
    if (local_kaggle_dataset is None) & (local_paperwithcode_dataset is None):
        indexGen = IndexGenerator(activate_stop=stop, activate_stemming=stem, start_index=start, local_dataset=None)
    else:
        kaggle_df = pd.read_csv(local_kaggle_dataset)
        paperwithcode_df = pd.read_csv(local_paperwithcode_dataset)
        paperwithcode_df.rename(columns={"owner":"ownerUser"}, inplace=True)
        uci_df = pd.read_csv(local_uci_dataset)
        uci_df.rename(columns={"Name":"title", "Abstract":"description", "Datapage URL":"ownerUser"}, inplace=True)
        edi_df = pd.read_csv(local_edi_dataset)
        edi_df.rename(columns={"Name":"title", "URL":"ownerUser"}, inplace=True)
        df = pd.concat([kaggle_df, paperwithcode_df, uci_df, edi_df], axis=0)
        df = df.reset_index(drop=True)
        indexGen = IndexGenerator(activate_stop=stop, activate_stemming=stem, start_index=start, local_dataset= df)
    indexGen.run_indexing()

parser = argparse.ArgumentParser(description='Inverted Index Generator')
parser.add_argument('--stemming', nargs="?", type=str, default='True', help='Activate stemming')
parser.add_argument('--remove_stopwords', nargs="?", type=str, default='False', help='Remove stopwords')
parser.add_argument('--start', nargs="?", type=int, default=0, help='Start batch index')
parser.add_argument('--local_kaggle_dataset', type=str, default=True, help='Local Kaggle dataset path')
parser.add_argument('--local_paperwithcode_dataset', type=str, default=True, help='Local paperwithcode dataset path')
parser.add_argument('--local_uci_dataset', type=str, default=True, help='Local UCI dataset path')
parser.add_argument('--local_edi_dataset', type=str, default=True, help='Local edi dataset path')
args = parser.parse_args()

run_with_arguments(eval(args.stemming), eval(args.remove_stopwords), args.start, 
                   args.local_kaggle_dataset, args.local_paperwithcode_dataset, args.local_uci_dataset, args.local_edi_dataset)