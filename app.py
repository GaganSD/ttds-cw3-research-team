############################
# Made for TTDS coursework 3
# Please note this files uses 
# dependencies that only works 
# in linux machines.
############################

from flask import Flask, request
from flask_cors import CORS
from infra.LRUCache import LRUCache
from datetime import datetime

from infra.helpers import curr_day, min_day, deserialize, filter_dates, Formatting

from core_algorithms.ir_eval.ranking_paper import ranking_query_BM25 as ranking_query_bm25_paper
from core_algorithms.ir_eval.ranking_paper import ranking_query_tfidf_cosine as ranking_query_tfidf_paper
from core_algorithms.ir_eval.ranking_paper import phrase_search as phrase_search_paper
from core_algorithms.ir_eval.ranking_paper import proximity_search as proximity_search_paper

from core_algorithms.ir_eval.ranking import ranking_query_tfidf as ranking_query_tfidf_dataset
from core_algorithms.ir_eval.ranking import phrase_search as phrase_search_dataset
from core_algorithms.ir_eval.ranking import proximity_search as proximity_search_dataset
from core_algorithms.ir_eval.ranking import ranking_query_BM25 as ranking_query_bm25_dataset

from core_algorithms.mongoDB_API import MongoDBClient
from core_algorithms.ir_eval.preprocessing import preprocess, author_preprocess
from core_algorithms.adv_query_options import query_spell_check, get_query_expansion

import json
import pandas as pd
import threading
import datetime
import time
import heapq
import requests


curr_formatter = Formatting()

# Create Flask app
app = Flask(__name__)
CORS(app)

print("completed.. your server will be up in less than 5 seconds..")
# Load paper indices
df_papers = pd.read_csv("/home/stylianosc/scann/papers/df.csv")
# Load dataset indices
df_datasets = pd.read_csv("core_algorithms/ir_eval/datasets/indices_dataset.csv")
df_datasets.rename(columns={"description": "abstract"}, inplace=True)


# Load datasets for inverted index
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

df.rename(columns={"description": "abstract"}, inplace=True)

client = MongoDBClient("34.142.18.57")
_preprocessing_cache = LRUCache(1000)
_results_cache = LRUCache(200)


def call_top_n(N, parameters):
    results = {"Results":[]}
    if parameters["search_type"] == "AUTHOR":

        if parameters["datasets"]:
            print("no Author search for datasets")
        else:
            results = get_author_papers_results(query=parameters['query'], 
                start_date=parameters["start_date"], end_date=parameters["end_date"],
                top_n=N)

    elif parameters["algorithm"] == "APPROX_NN":
        if parameters["datasets"]:
            results = requests.get('https://localhost:5000/datasets/' + query + "/" + str(N) + "/" \ 
             + parameters['query'] + "/" + parameters["start_date"] + "/" + parameters["end_date"])

get_approx_nn_datasets_results(query=parameters['query'], top_n=N)
        else:
            results = requests.get('https://localhost:5000/papers/' + query + "/" + str(N) + "/" \ 
             + parameters['query'] + "/" + parameters["start_date"] + "/" + parameters["end_date"])

    elif parameters["datasets"]:
        results = get_datasets_results(query=parameters['query'],
                            input_type = parameters["search_type"], 
                            ranking = parameters["algorithm"], top_n=N)

    else:
        results = get_papers_results(query=parameters['query'],
                            input_type = parameters["search_type"],
                            ranking = parameters["algorithm"],  
                            start_date=parameters["start_date"], 
                            end_date=parameters["end_date"], top_n=N)

    return results

def get_full_result(parameters, id):
    result = call_top_n(1000, parameters)
    _results_cache.put(id, result)
    return result

@app.route("/favicon.ico")
def favicon():
    return ""

@app.route("/<search_query>", methods = ['POST', 'GET'])
def search_state_machine(search_query):
    results = {"Results":[{}]}
    parameters = deserialize(request.args['q'])
    id = request.args['q'].rpartition("/pn=")[0]
    # {
    # query: search_query : DOME
    # from_date: DD-MM-YYYY (last) : 
    # to_date: DD-MM-YYYY :  
    # Authors: [str1, str2] : DONE
    # search_type: str (default, proximity, phrase, author) : DONE
    # algorithm: str (approx_nn, bm25, tf-idf) : DONE
    # datasets: bool
    # page_num: int
    # }
    pn = parameters["page_num"]

    if parameters["page_num"] > 1:
        thread = _results_cache.get(id+'_thread')
        if not thread is None:
            thread.join()
        content = _results_cache.get(id)
        if content is None:
            content = get_full_result(parameters, id)
        results = {"Results" : content['Results'][ (pn-1)*25 : pn*25 ]}
    else:
        content = _results_cache.get(id)
        if not content is None:
            return {"Results" : content['Results'][ (pn-1)*25 : pn*25 ]}

        results = call_top_n(25, parameters)
        thread = threading.Thread(target=get_full_result, args=(parameters, id))
        _results_cache.put(id+'_thread', thread)
        thread.start()
    
    return results

@app.route("/")
def direct_access_to_backend():
    return "Change PORT to 3000 to access the React frontend!"

######################### Search Functions ########################
def get_datasets_results(query: str, top_n: int=10, spell_check=False, qe=False, 
    input_type :str = "DEFAULT", ranking: str = "TF_IDF",) -> dict:
    if spell_check:
        query = ' '.join(query_spell_check(query))
    if qe:
        query = query + ' ' + ' '.join(get_query_expansion(query))
    query_params = _preprocess_query(query,True, True) # stemming, removing stopwords

    if input_type == "DEFAULT":
        if ranking == "TF_IDF":
            scores = ranking_query_tfidf_dataset(query_params)
        else:
            scores = ranking_query_bm25_dataset(query_params)
        outputs = [i[0] for i in scores[:top_n]]

    elif input_type == "PHRASE":
        outputs = phrase_search_dataset(query_params, start_time=time.time()) # return: list of ids of paper
    elif input_type == "PROXIMITY":
        outputs = proximity_search_dataset(query_params,  proximity=10) # return: list of ids of paper

    output_dict = {"Results":[]}
    columns = ['title','subtitle','abstract', 'ownerUser', 'dataset_slug', 'keyword']
    for result in outputs[:top_n]:
        output = df.iloc[result][columns].to_dict()
        # output["abstract"] = output["description"]
        for key, value in output.items():
            output[key] = str(value)
        output["date"] = ""
        output["authors"] = output["ownerUser"]
        output["abstract"] = curr_formatter.remove_markdown(output['abstract']) #TODO:YUTO
        output["url"] = "https://kaggle.com/" + output["ownerUser"] + "/" + output['dataset_slug']
        output_dict["Results"].append(output)
    return output_dict

def get_papers_results(query: str, top_n: int=10, spell_check=True, qe=False, 
    input_type :str = "DEFAULT", ranking: str = "TF_IDF", 
    start_date:datetime = min_day, end_date:datetime = curr_day) -> dict:

    # if spell_check:
    #     query = ' '.join(query_spell_check(query))
    if qe:
        query = query + ' ' + ' '.join(get_query_expansion(query))

    query_params = _preprocess_query(query, True, True) # stemming, removing stopwords


    if input_type == "DEFAULT":
        if ranking == "TF_IDF":
            scores = ranking_query_tfidf_paper(query_params, client)
        else:
            scores = ranking_query_bm25_paper(query_params, client)
        outputs = [i[0] for i in scores]
    elif input_type == "PHRASE":
        outputs = phrase_search_paper(query_params, client, start_time=time.time()) # return: list of ids of paper
    elif input_type == "PROXIMITY":
        outputs = proximity_search_paper(query_params, client, proximity=10)

    output_dict = {}

    temp_result = list(client.order_preserved_get_data(id_list= outputs,
                                                       start_date=start_date, end_date=end_date,
                                                       fields=['title', 'abstract','authors', 'url', 'date'],
                                                       limit=top_n
                                                      )
                      )

    for result in temp_result:
        result["date"] = result["date"].strftime("%d/%m/%Y")

    output_dict["Results"] = temp_result
    return output_dict

def get_author_papers_results(query: str, top_n: int=100, preprocess: bool=True, start_date:datetime = min_day, end_date:datetime = curr_day) -> dict:
    '''
    Sorting order in cases of equalities: 
    1 - Descending order of number of authors matching query (if more than 1 authors)
    2 - Ascending order of position of author in the author list (sum of positions if more than 1 authors matching)
    3 - Ascending order of term appearance in the query
    '''
    date_changed = start_date != min_day or end_date != curr_day
    if preprocess:
      query = author_preprocess(query)

    query_params = {'query': query}

    dict_occur = {}

    for author in query:
        temp_list = list(client.get_doc_from_index(term=author, index_table='a_index'))
        # Sort based on order of author
        temp_list = sorted(temp_list, key=lambda d: d['pos'][0]) 

        for i in temp_list:
          id = i['id']
          if id not in dict_occur: dict_occur[id] = [0, 0]
          dict_occur[id][0] += 1
          dict_occur[id][1] += i['pos'][0]

    dict_occur = dict(heapq.nsmallest(top_n if not date_changed else len(dict_occur), dict_occur.items(), key=lambda x: (-x[1][0],x[1][1])))
    outputs = list(dict_occur.keys())

    output_dict = {}

    temp_result = list(client.order_preserved_get_data(id_list= outputs,
                                                       start_date=start_date, end_date=end_date,
                                                       fields=['title', 'abstract','authors', 'url', 'date'],
                                                       limit=top_n
                                                      )
                      )
    for result in temp_result:
        result["date"] = result["date"].strftime("%d/%m/%Y")

    output_dict["Results"] = temp_result
    
    return output_dict


def authors_extensions(query: str, top_n: int=100, docs_searched: int=10, author_search_result: dict={'Results':[]}) -> dict:
    '''
    Call using author_search_result (results of regular author search) to avoid recalculating
    '''
    authors  = set(author_preprocess(query))
    coauthors = [author_preprocess(i['authors'])[:10] for i in author_search_result["Results"][:docs_searched]]
    merged_coauthors = [item for sublist in coauthors for item in sublist if item not in authors]
    merged_coauthors = list(dict.fromkeys(merged_coauthors))

    results = get_author_papers_results(merged_coauthors, top_n=100, preprocess=False)
    
    return results


@app.route("/QE/<query>", methods=['GET', 'POST'])
def query_expansion(query: str):
    """
    Recommends synonyms to users
    """
    expanded_queries = list(get_query_expansion(query))
    if not expanded_queries:
        return {"QEResults": ["No matching synonyms were found!", ""]}
    else:
        expanded_queries = ", ".join(expanded_queries)
        return {"QEResults": [expanded_queries, ""]}

def _preprocess_query(query: str, stemming=True, remove_stopwords=True) -> dict:
    """
    Input: query (str)
    Output: dict
    Helper function to preprocess queries efficiently with local cache.
    """
    cached_data = _preprocessing_cache.get(query)
    query_params = None

    if cached_data is not None:
        query_params = cached_data
    else:
        query_params = preprocess(query, stemming, remove_stopwords) # stemming, removing stopwords
        query_params = {'query': query_params}
        _preprocessing_cache.put(query, query_params)

    return query_params
