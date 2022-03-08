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
from mongoDB_API import MongoDBClient


class TimeLimitTerm(Exception): pass
TOTAL_NUMBER_OF_SENTENCES = 20000000


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




def ranking_query_BM25(query_params, client = None):
    terms = query_params['query']
    scores = defaultdict(float)
    #query_result_score = dict()
    doc_nums = TOTAL_NUMBER_OF_SENTENCES
    total_start_time = time.time()
    for term in terms:
        term_start_time = time.time()
        list_of_papers = client.get_doc_from_index(term)
        doc_nums_term = len(list_of_papers)
        # process_start = time.time()
        for relevant_paper in list_of_papers:
            paper_id = relevant_paper['id']
            term_freq = len(relevant_paper['pos'])
            dl = relevant_paper['len']
            score = score_BM25(doc_nums, doc_nums_term, term_freq, k1 = 1.5, dl = dl, avgdl=4.82)
            scores[paper_id] += score
    return sorted(dict(scores).items(), key = lambda x : x[1], reverse=True)

def ranking_query_tfidf(query_params, client = None):
    terms = query_params['query']
    scores = defaultdict(float)
    #query_result_score = dict()
    doc_nums = TOTAL_NUMBER_OF_SENTENCES
    total_start_time = time.time()
    for term in terms:
        term_start_time = time.time()
        list_of_papers = client.get_doc_from_index(term)
        doc_nums_term = len(list_of_papers)
        # process_start = time.time()
        for relevant_paper in list_of_papers:
            paper_id = relevant_paper['id']
            term_freq = len(relevant_paper['pos'])
            score = score_tfidf(doc_nums, doc_nums_term, term_freq)
            scores[paper_id] += score
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
    client = MongoDBClient("34.142.18.57")
    bm25_result_df = pd.DataFrame(columns=['title','abstract'])
    tfidf_result_df = pd.DataFrame(columns=['title','abstract'])
    query_params = {'query': ["covid", "2021"]}
    bm25_scores = ranking_query_BM25(query_params, client = client)
    end = time.time()
    print(end-start)
    for result in bm25_scores[:10]:
        cursor = client.get_data('paper',{'_id':result[0]}, fields=['title', 'abstract'],skip=0,limit=1)
        for doc in cursor:
            tmp_df = pd.DataFrame.from_dict(doc, orient='index').T
        bm25_result_df = bm25_result_df.append(tmp_df[['title','abstract']])
    bm25_result_df.to_csv(f'ir_eval/result/paper_bm_25_result_df_covid_2021.csv',index=False)
    start = time.time()
    tfidf_scores = ranking_query_tfidf(query_params, client = client)
    end = time.time()
    print(end-start)
    # print(scores[:10])
    for result in tfidf_scores[:10]:
        cursor = client.get_data('paper',{'_id':result[0]}, fields=['title', 'abstract'],skip=0,limit=1)
        for doc in cursor:
            tmp_df = pd.DataFrame.from_dict(doc, orient='index').T
        tfidf_result_df = tfidf_result_df.append(tmp_df[['title','abstract']])
        print(tmp_df['title'])

    tfidf_result_df.to_csv(f'ir_eval/result/paper_tfidf_result_df_covid_2021.csv',index=False)

    print("---------------------------------------------------")
    start = time.time()
    bm25_result_df = pd.DataFrame(columns=['title','subtitle','description'])
    tfidf_result_df = pd.DataFrame(columns=['title','abstract'])
    query_params = {'query': ["review", "food"]}
    start = time.time()
    bm25_scores = ranking_query_BM25(query_params, client = client)
    end = time.time()
    print(end-start)
    for result in bm25_scores[:10]:
        cursor = client.get_data('paper',{'_id':result[0]}, fields=['title', 'abstract'],skip=0,limit=1)
        for doc in cursor:
            tmp_df = pd.DataFrame.from_dict(doc, orient='index').T
        bm25_result_df = bm25_result_df.append(tmp_df[['title','abstract']])
        print(tmp_df['title'])
        print(tmp_df['abstract'])
    bm25_result_df.to_csv(f'ir_eval/result/paper_bm_25_result_df_review_food.csv',index=False)  
    start = time.time()  
    tfidf_scores = ranking_query_tfidf(query_params, client = client)
    end = time.time()
    print(end-start)
    # print(scores[:10])
    for result in tfidf_scores[:10]:
        cursor = client.get_data('paper',{'_id':result[0]}, fields=['title', 'abstract'],skip=0,limit=1)
        for doc in cursor:
            tmp_df = pd.DataFrame.from_dict(doc, orient='index').T
        tfidf_result_df = tfidf_result_df.append(tmp_df[['title','abstract']])
        print(tmp_df['title'])
        print(tmp_df['abstract'])
    # bm25_result_df.to_csv(f'bm_25_result_df_review_food.csv',index=False)
    tfidf_result_df.to_csv(f'ir_eval/result/paper_tfidf_result_df_review_food.csv',index=False)   