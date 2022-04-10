import json
import pickle5 as pickle #note: for python 3.8+ use "import pickle" instead. 

# from db.DB import get_db_instance
# from pathlib import Path
import math
# import time
import pandas as pd
import numpy as np

from collections import defaultdict
from core_algorithms.ir_eval.preprocessing import preprocess


# class TimeLimitTerm(Exception): pass
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




def ranking_query_BM25(query_params, index_path = 'core_algorithms/ir_eval/last'):
    index = load_file_binary(index_path)
    terms = query_params['query']
    scores = defaultdict(float)
    #query_result_score = dict()
    doc_nums = TOTAL_NUMBER_OF_SENTENCES
#    total_start_time = time.time()
    for term in terms:
#        term_start_time = time.time()
        term_list = [index[i]['term'] for i in range(len(index))]
        if term not in term_list:
            continue
        term_dict = index[term_list.index(term)]
        list_of_datasets = term_dict['dataset']
        doc_nums_term = term_dict['dataset_count'] # document frequency
        # process_start = time.time()
        for dataset_id, relevant_dataset in list_of_datasets.items():
            term_freq = len(relevant_dataset['pos'])
            dl = relevant_dataset['len']
            score = score_BM25(doc_nums, doc_nums_term, term_freq, k1 = 1.5, dl = dl, avgdl=58)
            scores[dataset_id] += score
    return sorted(dict(scores).items(), key = lambda x : x[1], reverse=True)

def ranking_query_tfidf(query_params, index_path = 'core_algorithms/ir_eval/last'):
    index = load_file_binary(index_path)
    terms = query_params['query']
    scores = defaultdict(float)
    #query_result_score = dict()
    doc_nums = TOTAL_NUMBER_OF_SENTENCES
#    total_start_time = time.time()
    for term in terms:
#        term_start_time = time.time()
        term_list = [index[i]['term'] for i in range(len(index))]
        if term not in term_list:
            continue
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

   
def proximity_search(query_params, proximity=2, index_path = 'core_algorithms/ir_eval/last'):
    inverted_index = load_file_binary(index_path)
    terms = query_params['query']
    scores = defaultdict(float)
    doc_nums = TOTAL_NUMBER_OF_SENTENCES
    # total_start_time = time.time()
    output_ids = list()
    # start = time.time()
    term_list = [inverted_index[i]['term'] for i in range(len(inverted_index))]
    if len(terms) == 1:
        if terms[0] not in term_list:
            return list()
        else:
            return list(inverted_index[term_list.index(terms[0])]['dataset'].keys())
    for i in range(len(terms)-1):
        term = terms[i]
#        term_start_time = time.time()
        if term not in term_list:
            continue
        list_of_datasets = inverted_index[term_list.index(term)]['dataset'].keys() # list of dataset ids
        # # print(term, time.time()-term_start_time)
        for j in range(i+1, len(terms)):
            tmp_term = terms[j]
            if tmp_term not in term_list:
                continue
#            term_start_time = time.time()
            tmp_list_of_datasets = inverted_index[term_list.index(tmp_term)]['dataset'].keys() # list of dataset ids
            # # print(tmp_term, time.time()-term_start_time)
            shared_papers = list(set(list_of_datasets).intersection(set(tmp_list_of_datasets)))
            for shared_dataset in shared_papers:
                list_of_pos = inverted_index[term_list.index(term)]['dataset'][shared_dataset]['pos']
                tmp_list_of_pos = inverted_index[term_list.index(tmp_term)]['dataset'][shared_dataset]['pos']
                if list_of_pos[0] - tmp_list_of_pos[-1] > proximity:
                    continue
                elif tmp_list_of_pos[0] - list_of_pos[-1] > proximity:
                    continue
                for pos1 in list_of_pos:
                    for pos2 in tmp_list_of_pos:
                        if abs(pos1-pos2) <= proximity:
                            output_ids.append(shared_dataset)
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
        list_of_pos1 = former_pos_dict[shared_paper]['pos']
        list_of_pos2 = later_pos_dict[shared_paper]['pos']
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
        
def phrase_search(query_params, index_path = 'core_algorithms/ir_eval/last'):
    inverted_index = load_file_binary(index_path)
    terms = query_params['query']
    term_list = [inverted_index[i]['term'] for i in range(len(inverted_index))]
    if len(terms) == 1:
        if terms[0] not in term_list:
            return list()
        else:
            return list(inverted_index[term_list.index(terms[0])]['dataset'].keys())
    for i in range(len(terms)-1):
        term1 = terms[i]
        term2 = terms[i+1]
        if (term1 not in term_list)|(term2 not in term_list):
            return list()
        if i == 0:
#            term_start_time = time.time()
            list_of_dataset1 = inverted_index[term_list.index(term1)]['dataset'].keys()
            # print(term1, time.time()-term_start_time)
            term1_dict = inverted_index[term_list.index(term1)]['dataset']
        else:
            list_of_dataset1 = list_of_dataset2
            term1_dict = output_dict
        list_of_dataset2 = inverted_index[term_list.index(term2)]['dataset'].keys()
        # print(term2, time.time()-term_start_time)
        term2_dict = inverted_index[term_list.index(term2)]['dataset']
        shared_datasets = list(set(list_of_dataset1).intersection(set(list_of_dataset2)))
        output_dict = check_adjacent_words(shared_datasets, term1_dict, term2_dict)
    return list(output_dict.keys())


if __name__ == '__main__':
#    start = time.time()
    output_path = 'core_algorithms/ir_eval/result/dataset/'
    kaggle_df = pd.read_csv('core_algorithms/ir_eval/kaggle_dataset_df_page500.csv')
    kaggle_df['Source'] = 'Kaggle'
    paperwithcode_df = pd.read_csv('core_algorithms/ir_eval/paperwithcode_df.csv')
    paperwithcode_df.rename(columns={"owner":"ownerUser"}, inplace=True)
    paperwithcode_df['Source'] = 'Paper_with_code'
    uci_df = pd.read_csv("core_algorithms/ir_eval/uci_dataset_test.csv")
    uci_df.rename(columns={"Name":"title", "Abstract":"description", "Datapage URL":"ownerUser"}, inplace=True)
    uci_df['Source'] = 'uci'
    edi_df = pd.read_csv("core_algorithms/ir_eval/edinburgh_research_datasets_info.csv")
    edi_df.rename(columns={"Name":"title", "URL":"ownerUser"}, inplace=True)
    edi_df['Source'] = 'Edi'
    df = pd.concat([kaggle_df, paperwithcode_df, uci_df, edi_df], axis=0)
    df = df.reset_index(drop=True)
    query_params1 = {'query': ["haskell"]}
    # query_params2 = {'query': ["statistics","health"]}
    # query_params3 = {'query': ["stock","prediction"]}
    query_params_list_old = [query_params1]#, query_params2, query_params3]
    query_params_list = list()
    for query_params in query_params_list_old:
        output_terms = preprocess(' '.join(query_params['query']),True, True)
        query_params_list.append({'query':output_terms})
    # print(query_params_list)
    #---------------------------------------------------
    # print('1.BM25')
    for query_params in query_params_list:
        # print(query_params['query'])
#        start = time.time()
        bm25_result_df = pd.DataFrame(columns=['title','subtitle','description'])
        bm25_scores = ranking_query_BM25(query_params)
 #       end = time.time()
        # print(end-start)
        for result in bm25_scores[:10]:
            tmp_df = df.iloc[result[0]]
            bm25_result_df = bm25_result_df.append(tmp_df[['title','subtitle','description', 'Source']])
            # print(tmp_df['title'])
            # print(tmp_df['subtitle'])
            # # print(tmp_df['description'])
        bm25_result_df.to_csv(output_path + 'bm25_df_' + '_'.join(query_params['query']) + '.csv', index=False)
    # print("---------------------------------------------------")
    # print('2. Tfidf')
    for query_params in query_params_list:
        # print(query_params['query'])
    #    start = time.time()
        tfidf_result_df = pd.DataFrame(columns=['title','subtitle','description'])
        tfidf_scores = ranking_query_tfidf(query_params)
     
     #   end = time.time()
        # print(end-start)
        # # print(scores[:10])
        for result in tfidf_scores[:10]:
            tmp_df = df.iloc[result[0]]
            tfidf_result_df = tfidf_result_df.append(tmp_df[['title','subtitle','description','Source']])
            # print(tmp_df['title'])
            # print(tmp_df['subtitle'])
            # # print(len(str(tmp_df['description'])))
        tfidf_result_df.to_csv(output_path + 'tfidf_df_' + '_'.join(query_params['query']) + '.csv', index=False)
    # print("---------------------------------------------------")
    # print('3.Pharase search')
    for query_params in query_params_list:
        # print(query_params['query'])
        phrase_result_df = pd.DataFrame(columns=['title','subtitle','description'])
        phrase_outputs = phrase_search(query_params)
#        end = time.time()
        # print(end-start)
        for result in phrase_outputs[:30]:
            tmp_df = df.iloc[result]
            phrase_result_df = phrase_result_df.append(tmp_df[['title','subtitle','description', 'Source']])
            # print(tmp_df['title'])
            # print(tmp_df['subtitle'])
            # # print(tmp_df['description'])
        phrase_result_df.to_csv(output_path + 'phrase_df_' + '_'.join(query_params['query']) + '.csv', index=False)
    


    
