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
from core_algorithms.mongoDB_API import MongoDBClient
import itertools
import tqdm
from core_algorithms.ir_eval.preprocessing import preprocess
import statistics


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
        list_of_papers = client.get_topk_doc_from_index(term)
        term_end_time = time.time()
        print(term, ':', term_end_time-term_start_time)
        doc_nums_term = client.get_df(term)#len(list_of_papers)
        seen_ids = set()
        for relevant_paper in list_of_papers:
            paper_id = relevant_paper['id']
            if paper_id in seen_ids:
                continue
            seen_ids.add(paper_id)
            term_freq = len(relevant_paper['pos'])
            dl = relevant_paper['len']
            score = score_BM25(doc_nums, doc_nums_term, term_freq, k1 = 1.5, dl = dl, avgdl=10.0)
            scores[paper_id] += score
    return sorted(dict(scores).items(), key = lambda x : x[1], reverse=True)


def ranking_query_tfidf_cosine(query_params, client = None):
    terms = query_params['query']
    scores = defaultdict(float)
    #query_result_score = dict()
    doc_nums = TOTAL_NUMBER_OF_SENTENCES
    total_start_time = time.time()
    tf_dict = dict()
    for unique_term in set(terms):
        tmp_tf = sum([term == unique_term for term in set(terms)])
        tf_dict[unique_term] = tmp_tf
    doc_scores = defaultdict(list)
    query_vector = dict()
    query_length = 0
    for term in set(terms):
        term_start_time = time.time()
        list_of_papers = client.get_topk_doc_from_index(term)
        term_end_time = time.time()
        doc_nums_term = client.get_df(term)#len(list_of_papers)
        if doc_nums_term == 0:
            doc_nums_term = 1
        print(term, ':', term_end_time-term_start_time)
        query_score = score_tfidf(doc_nums,doc_nums_term, tf_dict[term])
        query_length += query_score ** 2
        query_vector[term] = query_score
        seen_ids = set()
        for relevant_paper in list_of_papers:
            paper_id = relevant_paper['id']
            if paper_id in seen_ids:
                continue
            seen_ids.add(paper_id)
            term_freq = len(relevant_paper['pos'])
            doc_score = score_tfidf(doc_nums, doc_nums_term, term_freq) 
            doc_scores[paper_id].append(doc_score ** 2) # to calculate length of document
            score = query_score * doc_score 
            scores[paper_id] += score
    for doc_id in scores.keys():
        scores[doc_id] = scores[doc_id] / np.sqrt(sum(doc_scores[doc_id])) / np.sqrt(query_length)
    return sorted(dict(scores).items(), key = lambda x : x[1], reverse=True)


def ranking_query_tfidf(query_params, client = None):
    terms = query_params['query']
    scores = defaultdict(float)
    #query_result_score = dict()
    doc_nums = TOTAL_NUMBER_OF_SENTENCES
    total_start_time = time.time()
    for term in terms:
        term_start_time = time.time()
        list_of_papers = client.get_topk_doc_from_index(term)
        term_end_time = time.time()
        print(term, ':', term_end_time-term_start_time)
        doc_nums_term = client.get_df(term)#len(list_of_papers)
        seen_ids = set()
        for relevant_paper in list_of_papers:
            paper_id = relevant_paper['id']
            if paper_id in seen_ids:
                continue
            seen_ids.add(paper_id)
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
    if len(terms) == 1:
        list_of_papers1 = client.get_topk_doc_from_index(terms[0])
        ids_of_papers = [paper['id'] for paper in list_of_papers1]
        return ids_of_papers
    for i in range(len(terms)-1):
        term = terms[i]
        term_start_time = time.time()
        list_of_papers = client.get_topk_doc_from_index(term)
        print(term, time.time()-term_start_time)
        list_of_docs = [doc['id'] for doc in list_of_papers]
        term1_dict = dict()
        for paper in list_of_papers:
            term1_dict[paper['id']] = paper['pos']
        for j in range(i+1, len(terms)):
            tmp_term = terms[j]
            term_start_time = time.time()
            tmp_list_of_papers = client.get_topk_doc_from_index(tmp_term)
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
        
def phrase_search(query_params, client = None, topk = 2000, start_time=time.time(),tmp_result = []):
    terms = query_params['query']
    scores = defaultdict(float)
    doc_nums = TOTAL_NUMBER_OF_SENTENCES
    max_sec = 7
    if time.time()-start_time > max_sec:
        # if total processing time is over max_sec, it returns fewer results (< 10)
        output_ids = tmp_result
    else:
        print('topk = ',topk)
        if len(terms) == 1:
            list_of_papers1 = client.get_topk_doc_from_index(terms[0],k=topk)
            ids_of_papers = [paper['id'] for paper in list_of_papers1]
            return ids_of_papers
        for i in range(len(terms)-1):
            term1 = terms[i]
            term2 = terms[i+1]
            if i == 0:
                term_start_time = time.time()
                list_of_papers1 = client.get_topk_doc_from_index(term1, k=topk)
                # print(term1, time.time()-term_start_time)
                term1_dict = dict()
                for paper in list_of_papers1:
                    term1_dict[paper['id']] = paper['pos']
            else:
                list_of_papers1 = list_of_papers2
                term1_dict = output_dict
            term2_dict = dict()
            term_start_time = time.time()
            list_of_papers2 = client.get_topk_doc_from_index(term2, k=topk)
            # print(term2, time.time()-term_start_time)
            for paper in list_of_papers2:
                term2_dict[paper['id']] = paper['pos']
            shared_papers = list(set(term1_dict.keys()).intersection(set(term2_dict.keys())))
            output_dict = check_adjacent_words(shared_papers, term1_dict, term2_dict)
        output_ids = list(output_dict.keys())
        # print(len(output_ids))
        if len(output_ids) < 10:
            new_topk = topk * 3
            output_ids = phrase_search(query_params, client, topk=new_topk, start_time=start_time, tmp_result=output_ids)
    print(time.time()-start_time)
    return output_ids


if __name__ == '__main__':
    print('Paper search')
    client = MongoDBClient("34.142.18.57")
    output_file = 'core_algorithms/ir_eval/result/paper/'
    # query_params1 = {'query': ["walid","magdy"]}
    query_params1 =  {'query': ["stock","prediction"]}#{'query': ["vision","transformer"]}
    # query_params2 = {'query': ["statistics","health"]}
    # query_params3 = {'query': ["stock","prediction"]}
    query_params_list_old = [query_params1]#, query_params2, query_params3]
    query_params_list = list()
    for query_params in query_params_list_old:
        output_terms = preprocess(' '.join(query_params['query']),True, True)
        query_params_list.append({'query':output_terms})
    print(query_params_list)
    #---------------------------------------------------
    print('1.Phrase search')
    for query_params in query_params_list:
        print(query_params['query'])
        phrase_result_df = pd.DataFrame(columns=['title','abstract'])
        start = time.time()
        outputs = phrase_search(query_params, client)
        end = time.time()
        print('result nums:', len(outputs))
        for idx, result in enumerate(outputs):
            if idx > 20:
                break
            cursor = client.get_one(data_type='paper', filter={'_id':result}, fields=['title', 'abstract'])
            try:
                tmp_df = pd.DataFrame.from_dict(cursor, orient='index').T
                tmp_df['id'] = result[0]
                phrase_result_df = phrase_result_df.append(tmp_df[['id','title','abstract']])
            except:
                print('No such paper in database')
        print(end - start)
        phrase_result_df.to_csv(output_file + '/phrase_result_df_' + '_'.join(query_params['query']) + '.csv', index=False)
    print()
    #---------------------------------------------------
    print('2.Proximity search')
    # 1. covid, 2021
    for query_params in query_params_list:
        print(query_params['query'])
        proximity_result_df = pd.DataFrame(columns=['title','abstract'])
        start = time.time()
        outputs = proximity_search(query_params, client, 3)
        end = time.time()
        print('result nums:', len(outputs))
        for idx, result in enumerate(outputs):
            if idx > 20:
                break
            cursor = client.get_one(data_type='paper', filter={'_id':result}, fields=['title', 'abstract'])
            try:
                tmp_df = pd.DataFrame.from_dict(cursor, orient='index').T
                tmp_df['id'] = result[0]
                proximity_result_df = proximity_result_df.append(tmp_df[['id','title','abstract']])
            except:
                print('No such paper in database')
        print(end - start)
        proximity_result_df.to_csv(output_file + 'proximity_df_' + '_'.join(query_params['query']) + '.csv', index=False)
    print()
    #---------------------------------------------------
    print('3.Ranking algorithm')
    print('1. BM25')
    for idx, query_params in enumerate(query_params_list):
        print(query_params['query'])
        bm25_result_df = pd.DataFrame(columns=['title','abstract'])
        start = time.time()
        bm25_scores = ranking_query_BM25(query_params, client = client)
        end = time.time()
        print(bm25_scores[:10])
        for result in bm25_scores[:10]:
            cursor = client.get_one(data_type='paper', filter={'_id':result[0]}, fields=['title', 'abstract'])
            try:
                tmp_df = pd.DataFrame.from_dict(cursor, orient='index').T
                tmp_df['id'] = result[0]
                bm25_result_df = bm25_result_df.append(tmp_df[['id','title','abstract']])
                print(tmp_df['title'].values)
            except:
                print('No such paper in database')
        print(end-start)
        bm25_result_df.to_csv(output_file + 'paper_bm_25_result_df_' + '_'.join(query_params['query']) + '.csv',index=False)
    print()
    
    print('2. Tfidf')
    for idx, query_params in enumerate(query_params_list):
        print(query_params['query'])
        tfidf_result_df = pd.DataFrame(columns=['title','abstract'])
        start = time.time()
        tfidf_scores = ranking_query_tfidf(query_params, client = client)
        end = time.time()
        print(tfidf_scores[:10])
        for result in tfidf_scores[:10]:
            cursor = client.get_one(data_type='paper', filter={'_id':result[0]}, fields=['title', 'abstract'])
            try:
                tmp_df = pd.DataFrame.from_dict(cursor, orient='index').T
                tmp_df['id'] = result[0]
                tfidf_result_df = tfidf_result_df.append(tmp_df[['id','title','abstract']])
                print(tmp_df['title'].values)
            except:
                print('No such paper in db')
        print(end-start)
        tfidf_result_df.to_csv(output_file + 'paper_tfidf_result_df_' + '_'.join(query_params['query']) + '.csv',index=False)
    