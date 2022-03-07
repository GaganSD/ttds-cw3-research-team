from audioop import avg
from cmath import nan
import json
import pickle
import sys
# from db.DB import get_db_instance
from pathlib import Path
import math
import time
import pandas as pd
import numpy as np

from collections import defaultdict


class TimeLimitTerm(Exception): pass
TOTAL_NUMBER_OF_SENTENCES = 9498


def json_load(path):
    """ It loads and returns a json data in dictionary structure.
    Arguments:
        path {string} -- the path of the json data
    Returns:
        dictionary -- the dictionary created from the json data.
    """
    return json.load(open(path))


def load_file_binary(file_name):
    with open(file_name + '.pickle', 'rb') as f:
        return pickle.load(f)


def idf(term, docs_for_term, doc_nums):
    """
    Calculates and return the IDF for the term. Returns 0 if DF is 0.
    Parameters:
        term (string): a single term
    """
    df = len(docs_for_term)
    if df == 0:
        return 0
    return math.log10(doc_nums / df)




def ranking_query_BM25(query_params, index=None):
    terms = query_params['query']
    scores = defaultdict(float)
    #query_result_score = dict()
    doc_nums = TOTAL_NUMBER_OF_SENTENCES
    total_start_time = time.time()
    for term in terms:
        term_start_time = time.time()
        term_list = [index[i]['term'] for i in range(len(index))]
        term_dict = index[term_list.index(term)]
        list_of_datasets = term_dict['dataset']
        doc_nums_term = term_dict['dataset_count'] # document frequency
        # process_start = time.time()
        for dataset_id, relevant_dataset in list_of_datasets.items():
            term_freq = len(relevant_dataset['pos'])
            dl = relevant_dataset['len']
            score = score_BM25(doc_nums, doc_nums_term, term_freq, k1 = 1.5, dl = dl, avgdl=4.82)
            scores[dataset_id] += score
    return sorted(dict(scores).items(), key = lambda x : x[1], reverse=True)

def ranking_query_tfidf(query_params, index=None):
    terms = query_params['query']
    scores = defaultdict(float)
    #query_result_score = dict()
    doc_nums = TOTAL_NUMBER_OF_SENTENCES
    total_start_time = time.time()
    for term in terms:
        term_start_time = time.time()
        term_list = [index[i]['term'] for i in range(len(index))]
        term_dict = index[term_list.index(term)]
        list_of_datasets = term_dict['dataset']
        doc_nums_term = term_dict['dataset_count'] # document frequency
        # process_start = time.time()
        for dataset_id, relevant_dataset in list_of_datasets.items():
            term_freq = len(relevant_dataset['pos'])
            score = score_tfidf(doc_nums, doc_nums_term, term_freq)
            scores[dataset_id] += score
    return sorted(dict(scores).items(), key = lambda x : x[1], reverse=True)

def score_tfidf(doc_nums, doc_nums_term, term_freq):
    return (1+np.log10(term_freq)) * np.log10(doc_nums/doc_nums_term)


def score_BM25(doc_nums, doc_nums_term, term_freq, k1, dl, avgdl):
    K = compute_K(k1, dl, avgdl)
    idf_param = math.log( (doc_nums-doc_nums_term+0.5) / (doc_nums_term+0.5) )
    next_param = (term_freq) / (K + term_freq + 0.5)
    return float("{0:.4f}".format(next_param * idf_param))


def compute_K(k1, dl, avgdl):
    return k1 * dl / avgdl


if __name__ == '__main__':
    start = time.time()
    index_path = 'last'
    inverted_index = load_file_binary(index_path)
    bm25_result_df = pd.DataFrame(columns=['title','subtitle','description'])
    tfidf_result_df = pd.DataFrame(columns=['title','subtitle','description'])
    kaggle_df = pd.read_csv('kaggle_dataset_df_page500.csv')
    kaggle_df['Source'] = 'Kaggle'
    paperwithcode_df = pd.read_csv('paperwithcode_df.csv')
    paperwithcode_df['Source'] = 'Paper_with_code'
    df = pd.concat([kaggle_df, paperwithcode_df])
    df = df.reset_index(drop=True)
    # query_params = {'query': ["father"]} #, "boy", "girl"]}
    query_params = {'query': ["covid", "2021"]}
    bm25_scores = ranking_query_BM25(query_params, index=inverted_index)
    end = time.time()
    print(end-start)
    # print(scores[:10])
    for result in bm25_scores[:10]:
        tmp_df = df.iloc[result[0]]
        bm25_result_df = bm25_result_df.append(tmp_df[['title','subtitle','description', 'Source']])
        print(tmp_df['title'])
        print(tmp_df['subtitle'])
        print(tmp_df['description'])
    bm25_result_df.to_csv(f'bm_25_result_df_covid_2021.csv',index=False)
    tfidf_scores = ranking_query_tfidf(query_params, index=inverted_index)
    end = time.time()
    print(end-start)
    # print(scores[:10])
    for result in tfidf_scores[:10]:
        tmp_df = df.iloc[result[0]]
        tfidf_result_df = tfidf_result_df.append(tmp_df[['title','subtitle','description','Source']])
        print(tmp_df['title'])
        print(tmp_df['subtitle'])
        print(len(str(tmp_df['description'])))
    tfidf_result_df.to_csv(f'tfidf_result_df_covid_2021.csv',index=False)

    print("---------------------------------------------------")
    bm25_result_df = pd.DataFrame(columns=['title','subtitle','description'])
    tfidf_result_df = pd.DataFrame(columns=['title','subtitle','description'])
    # query_params = {"year": "2000-2001"}
    query_params = {'query': ["review", "food"]}
    start = time.time()
    scores = ranking_query_BM25(query_params, inverted_index)
    end = time.time()
    print(end-start)
    # print(scores[:10])
    for result in scores[:10]:
        tmp_df = df.iloc[result[0]]
        bm25_result_df = bm25_result_df.append(tmp_df[['title','subtitle','description','Source']])
        print(tmp_df['title'])
        print(tmp_df['subtitle'])
        print(len(str(tmp_df['description'])))
        
    tfidf_scores = ranking_query_tfidf(query_params, index=inverted_index)
    end = time.time()
    print(end-start)
    # print(scores[:10])
    for result in tfidf_scores[:10]:
        tmp_df = df.iloc[result[0]]
        tfidf_result_df = tfidf_result_df.append(tmp_df[['title','subtitle','description','Source']])
        print(tmp_df['title'])
        print(tmp_df['subtitle'])
        print(len(str(tmp_df['description'])))
    bm25_result_df.to_csv(f'bm_25_result_df_review_food.csv',index=False)
    tfidf_result_df.to_csv(f'tfidf_result_df_review_food.csv',index=False)   
    