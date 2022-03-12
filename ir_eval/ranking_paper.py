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
import itertools
import tqdm


class TimeLimitTerm(Exception): pass
TOTAL_NUMBER_OF_SENTENCES = 23000000


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
        term_end_time = time.time()
        print(term, ':', term_end_time-term_start_time)
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
    
def proximity_search(query_params, client = None, proximity=2):
    terms = query_params['query']
    scores = defaultdict(float)
    doc_nums = TOTAL_NUMBER_OF_SENTENCES
    total_start_time = time.time()
    output_ids = list()
    start = time.time()
    for i in range(len(terms)-1):
        term = terms[i]
        term_start_time = time.time()
        list_of_papers = client.get_doc_from_index(term)
        print(term, time.time()-term_start_time)
        list_of_docs = [doc['id'] for doc in list_of_papers]
        term1_dict = dict()
        for paper in list_of_papers:
            term1_dict[paper['id']] = paper['pos']
        for j in range(i+1, len(terms)):
            tmp_term = terms[j]
            term_start_time = time.time()
            tmp_list_of_papers = client.get_doc_from_index(tmp_term)
            print(tmp_term, time.time()-term_start_time)
            tmp_list_of_docs = [doc['id'] for doc in tmp_list_of_papers]
            term2_dict = dict()
            for paper in tmp_list_of_papers:
                term2_dict[paper['id']] = paper['pos']
            shared_papers = list(set(list_of_docs).intersection(set(tmp_list_of_docs)))
            for shared_paper in tqdm.tqdm(shared_papers, total=len(shared_papers)):
                list_of_pos = term1_dict[shared_paper]
                tmp_list_of_pos = term2_dict[shared_paper]
                if list_of_pos[0] - tmp_list_of_pos[-1] > proximity:
                    continue
                elif tmp_list_of_pos[0] - list_of_pos[-1] > proximity:
                    continue
                for pos1 in list_of_pos:
                    for pos2 in tmp_list_of_pos:
                        if abs(pos1-pos2) <= proximity:
                            output_ids.append(shared_paper)
                        elif pos2 - pos1 > proximity:
                            # move on to next pos1 
                            break
                        else:
                            continue

    return output_ids

def check_adjacent_words(shared_papers, former_pos_dict, later_pos_dict):
    proximity = 1
    output_dict = defaultdict(list)
    for shared_paper in shared_papers:
        list_of_pos1 = former_pos_dict[shared_paper]
        list_of_pos2 = later_pos_dict[shared_paper]
        if list_of_pos1[0] - list_of_pos2[-1] > proximity:
            continue
        elif list_of_pos2[0] - list_of_pos1[-1] > proximity:
            continue
        for pos1 in list_of_pos1:
            for pos2 in list_of_pos2:
                if pos2-pos1 == proximity:
                    output_dict[shared_paper].append(pos2)
                elif pos2 - pos1 > proximity:
                    # move on to next pos1 
                    break
                else:
                    continue
    return dict(output_dict)
        
def phrase_search(query_params, client = None):
    terms = query_params['query']
    scores = defaultdict(float)
    doc_nums = TOTAL_NUMBER_OF_SENTENCES
    for i in range(len(terms)-1):
        term1 = terms[i]
        term2 = terms[i+1]
        if i == 0:
            list_of_papers1 = client.get_doc_from_index(term1)
            term1_dict = dict()
            for paper in list_of_papers1:
                term1_dict[paper['id']] = paper['pos']
        else:
            list_of_papers1 = list_of_papers2
            term1_dict = output_dict
        term2_dict = dict()
        list_of_papers2 = client.get_doc_from_index(term2)
        for paper in list_of_papers2:
            term2_dict[paper['id']] = paper['pos']
        shared_papers = list(set(term1_dict.keys()).intersection(set(term2_dict.keys())))
        output_dict = check_adjacent_words(shared_papers, term1_dict, term2_dict)
    return output_dict.keys()


if __name__ == '__main__':
    print('Paper search')
    client = MongoDBClient("34.142.18.57")
    #---------------------------------------------------
    print('1.Phrase search')
    # 1. covid, 2021
    query_params = {'query': ["2021","covid"]}
    phrase_result_df = pd.DataFrame(columns=['title','abstract'])
    start = time.time()
    outputs = phrase_search(query_params, client)
    end = time.time()
    for result in outputs:
        cursor = client.get_one(data_type='paper', filter={'_id':result}, fields=['title', 'abstract'])
        try:
            tmp_df = pd.DataFrame.from_dict(cursor, orient='index').T
            tmp_df['id'] = result[0]
            phrase_result_df = phrase_result_df.append(tmp_df[['id','title','abstract']])
        except:
            print('No such paper in database')
    print(end - start)
    phrase_result_df.to_csv('ir_eval/result/phrase_result_df_' + '_'.join(query_params['query']) + '.csv', index=False)
    # 2. food, review
    query_params = {'query': ["cnn", "resnet"]}
    phrase_result_df = pd.DataFrame(columns=['title','abstract'])
    start = time.time()
    outputs = phrase_search(query_params, client)
    end = time.time()
    for result in outputs:
        cursor = client.get_one(data_type='paper', filter={'_id':result}, fields=['title', 'abstract'])
        try:
            tmp_df = pd.DataFrame.from_dict(cursor, orient='index').T
            tmp_df['id'] = result[0]
            phrase_result_df = phrase_result_df.append(tmp_df[['id','title','abstract']])
        except:
            print('No such paper in database')
    print(end - start)
    phrase_result_df.to_csv('ir_eval/result/phrase_result_df_' + '_'.join(query_params['query']) + '.csv', index=False)
    #---------------------------------------------------
    print('2.Proximity search')
    # 1. covid, 2021
    query_params = {'query': ["covid", "2021"]}
    proximity_result_df = pd.DataFrame(columns=['title','abstract'])
    start = time.time()
    outputs = proximity_search(query_params, client, 2)
    end = time.time()
    for result in outputs:
        # cursor = client.get_data('paper',{'_id':result}, fields=['title', 'abstract'],skip=0,limit=1)
        cursor = client.get_one(data_type='paper', filter={'_id':result}, fields=['title', 'abstract'])
        try:
            tmp_df = pd.DataFrame.from_dict(cursor, orient='index').T
            tmp_df['id'] = result[0]
            proximity_result_df = proximity_result_df.append(tmp_df[['id','title','abstract']])
        except:
            print('No such paper in database')
    print(end - start)
    proximity_result_df.to_csv('ir_eval/result/proximity_df_' + '_'.join(query_params['query']) + '.csv', index=False)
    # 2. food, review
    query_params = {'query': ["food", "review"]}
    proximity_result_df = pd.DataFrame(columns=['title','abstract'])
    start = time.time()
    outputs = proximity_search(query_params, client, 2)
    end = time.time()
    for result in outputs:
        # cursor = client.get_data('paper',{'_id':result}, fields=['title', 'abstract'],skip=0,limit=1)
        cursor = client.get_one(data_type='paper', filter={'_id':result}, fields=['title', 'abstract'])
        try:
            tmp_df = pd.DataFrame.from_dict(cursor, orient='index').T
            tmp_df['id'] = result[0]
            proximity_result_df = proximity_result_df.append(tmp_df[['id','title','abstract']])
        except:
            print('No such paper in database')
    print(end - start)
    proximity_result_df.to_csv('ir_eval/result/proximity_df_' + '_'.join(query_params['query']) + '.csv')
    #---------------------------------------------------
    print('3.Ranking algorithm')
    bm25_result_df = pd.DataFrame(columns=['title','abstract'])
    tfidf_result_df = pd.DataFrame(columns=['title','abstract'])
    query_params = {'query': ["covid", "2021"]}
    start = time.time()
    bm25_scores = ranking_query_BM25(query_params, client = client)
    for result in bm25_scores[:10]:
        cursor = client.get_one(data_type='paper', filter={'_id':result}, fields=['title', 'abstract'])
        try:
            tmp_df = pd.DataFrame.from_dict(cursor, orient='index').T
            tmp_df['id'] = result[0]
            bm25_result_df = bm25_result_df.append(tmp_df[['id','title','abstract']])
            print(tmp_df['title'])
        except:
            print('No such paper in database')
    end = time.time()
    print(end-start)
    bm25_result_df.to_csv(f'ir_eval/result/paper_bm_25_result_df_' + '_'.join(query_params['query']) + '.csv')
    start = time.time()
    tfidf_scores = ranking_query_tfidf(query_params, client = client)
    for result in tfidf_scores[:10]:
        cursor = client.get_one(data_type='paper', filter={'_id':result}, fields=['title', 'abstract'])
        try:
            tmp_df = pd.DataFrame.from_dict(cursor, orient='index').T
            tmp_df['id'] = result[0]
            tfidf_result_df = tfidf_result_df.append(tmp_df[['id','title','abstract']])
            print(tmp_df['title'])
        except:
            print('No such paper in db')
    end = time.time()
    print(end-start)
    tfidf_result_df.to_csv(f'ir_eval/result/paper_tfidf_result_df_' + '_'.join(query_params['query']) + '.csv')
    print("---------------------------------------------------")
    query_params = {'query': ["review", "food"]}
    start = time.time()
    bm25_result_df = pd.DataFrame(columns=['title','abstract'])
    tfidf_result_df = pd.DataFrame(columns=['title','abstract'])
    start = time.time()
    bm25_scores = ranking_query_BM25(query_params, client = client)
    for result in bm25_scores[:10]:
        cursor = client.get_one(data_type='paper', filter={'_id':result}, fields=['title', 'abstract'])
        tmp_df = pd.DataFrame.from_dict(cursor, orient='index').T
        tmp_df['id'] = result[0]
        bm25_result_df = bm25_result_df.append(tmp_df[['id','title','abstract']])
        print(tmp_df['title'])
        print(tmp_df['abstract'])
    end = time.time()
    print(end-start)
    bm25_result_df.to_csv(f'ir_eval/result/paper_bm_25_result_df_' + '_'.join(query_params['query']) + '.csv')  
    start = time.time()  
    tfidf_scores = ranking_query_tfidf(query_params, client = client)
    for result in tfidf_scores[:10]:
        cursor = client.get_one(data_type='paper', filter={'_id':result}, fields=['title', 'abstract'])
        tmp_df = pd.DataFrame.from_dict(cursor, orient='index').T
        tmp_df['id'] = result[0]
        tfidf_result_df = tfidf_result_df.append(tmp_df[['id','title','abstract']])
        print(tmp_df['title'])
        print(tmp_df['abstract'])
    end = time.time()
    print(end-start)
    tfidf_result_df.to_csv(f'ir_eval/result/paper_tfidf_result_df_' + '_'.join(query_params['query']) + '.csv')   