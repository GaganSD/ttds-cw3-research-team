############################
# Made for TTDS coursework 3
# Please note this files uses 
# dependencies that only works 
# in linux machines.
############################

from collections import defaultdict
from flask import Flask, request
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from infra.LRUCache import LRUCache
import datetime
import heapq
import time
import nltk
from core_algorithms.query_expansion import get_query_expansion
from core_algorithms.ir_eval.ranking import ranking_query_tfidf as ranking_query_tfidf_dataset
from core_algorithms.ir_eval.ranking_paper import ranking_query_tfidf as ranking_query_tfidf_paper
from core_algorithms.ir_eval.ranking_paper import phrase_search as phrase_search_paper
from core_algorithms.ir_eval.ranking import phrase_search as phrase_search_dataset
from core_algorithms.ir_eval.ranking_paper import proximity_search as proximity_search_paper
from core_algorithms.ir_eval.ranking import proximity_search as proximity_search_dataset
from core_algorithms.ir_eval.ranking import ranking_query_BM25 as ranking_query_bm25_dataset
from core_algorithms.ir_eval.ranking_paper import ranking_query_BM25 as ranking_query_bm25_paper
from core_algorithms.mongoDB_API import MongoDBClient
from core_algorithms.ir_eval.preprocessing import preprocess, author_preprocess
#from core_algorithms.query_expansion import get_query_extension
from core_algorithms.query_spell_check import query_spell_check

print(0.1)
import json
from datetime import datetime
import scann ## NOTE: Only works on linux machines #NOTE:DL
import pandas as pd

nltk.download('omw-1.4')


# Create Flask app
app = Flask(__name__)
CORS(app)

print(0.2)
# Load paper index
searcher = scann.scann_ops_pybind.load_searcher('/home/stylianosc/scann/papers/') #NOTE:DL
print(0.3)
# Load transformer encoder
model = SentenceTransformer('all-MiniLM-L6-v2') #NOTE:DL
print(0.4)
# Load paper indices
df_papers = pd.read_csv("/home/stylianosc/scann/papers/df.csv") #NOTE:DL
print(0.5)

client = MongoDBClient("34.142.18.57")
_preprocessing_cache = LRUCache(1000)
_results_cache = LRUCache(200)
print(0.6)

curr_day = datetime.today()
min_day = datetime.strptime("01-01-1000", '%d-%m-%Y')
_no_match_sample = {"title": "No Matching Documents Were Found", "abstract": "Try expanding your query with our search suggestion", "url":"", "authors":"","date":curr_day.strftime('%d/%m/%Y')}
_no_results_dict = {"Results": [_no_match_sample]}

@app.route("/")
def hello():
    return "hello"

@app.route("/<search_query>", methods = ['POST', 'GET'])
def search_state_machine(search_query):
    print(1)
    results = {"Results":[{}]}

    parameters = _deserialize(request.args['q'])
    print(2)
    print(parameters)
    # {
    # query: search_query : DOME
    # from_date: DD-MM-YYYY (last) : 
    # to_date: DD-MM-YYYY :  
    # Authors: [str1, str2] : DONE
    # search_type: str (default, proximity, phrase, author) : DONE
    # algorithm: str (approx_nn, bm25, tf-idf) : DONE
    # datasets: bool
    # }

    if parameters["search_type"] == "AUTHOR":

        if parameters["datasets"]:
            print("no AUTHOR search for datasets")
        else:
            results = get_author_papers_results(query=parameters['query'], start_date=parameters["start_date"], end_date=parameters["end_date"])

    elif parameters["search_type"] == "PHRASE":

        if parameters["datasets"]:
            results = get_phrase_datasets_results(query=parameters['query'], start_date=parameters["start_date"], end_date=parameters["end_date"])
        else:
            results = get_phrase_papers_results(query=parameters['query'], start_date=parameters["start_date"], end_date=parameters["end_date"])

    elif parameters["search_type"] == "PROXIMITY":
        if parameters["datasets"]:
            results = get_proximity_datasets_results(query=parameters['query'], start_date=parameters["start_date"], end_date=parameters["end_date"])
        else:
            results = get_proximity_papers_results(query=parameters['query'], start_date=parameters["start_date"], end_date=parameters["end_date"])

    elif parameters["search_type"] == "DEFAULT":

        if parameters["datasets"]:

            if parameters["algorithm"] == "APPROX_NN":
                results = get_approx_nn_datasets_results(query=parameters['query'], start_date=parameters["start_date"], end_date=parameters["end_date"])
            elif parameters["algorithm"] == "BM25":
                results = get_dataset_results_bm25(query=parameters['query'], start_date=parameters["start_date"], end_date=parameters["end_date"])
            elif parameters["algorithm"] == "TF_IDF":
                results = get_tf_idf_dataset_results(query=parameters['query'], start_date=parameters["start_date"], end_date=parameters["end_date"])

        else:

            if parameters["algorithm"] == "APPROX_NN": 
                results = get_approx_nn_papers_results(query=parameters['query'], start_date=parameters["start_date"], end_date=parameters["end_date"])
            elif parameters["algorithm"] == "BM25":
                results = get_papers_results_bm25(query=parameters['query'], start_date=parameters["start_date"], end_date=parameters["end_date"])
            elif parameters["algorithm"] == "TF_IDF":
                results = get_paper_results_tf_idf(query=parameters['query'], start_date=parameters["start_date"], end_date=parameters["end_date"])

    return results


@app.route("/")
def direct_access_to_backend():
    return "Change PORT to 3000 to access the React frontend!"
print(0.6)
######################### Search Functions ########################

def get_author_papers_results(query: str, top_n: int=100, preprocess: bool=True, start_date:datetime = min_day, end_date:datetime = curr_day) -> dict:
    '''
    Sorting order in cases of equalities: 
    1 - Descending order of number of authors matching query (if more than 1 authors)
    2 - Ascending order of position of author in the author list (sum of positions if more than 1 authors matching)
    3 - Ascending order of term appearance in the query
    '''
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

    dict_occur = dict(heapq.nsmallest(top_n, dict_occur.items(), key=lambda x: (-x[1][0],x[1][1])))
    temp_ids = list(dict_occur.keys())

    output_dict = {}

    temp_result = list(client.get_data('paper', {'_id':{"$in" : temp_ids}}, ['title', 'abstract','authors', 'url', 'date']))
    temp_result = {i['_id'] : i for i in temp_result}
    output_dict["Results"] = [temp_result[i] for i in temp_ids]

    return output_dict

def filter_dates(output: dict={'Results':[]}, start_date:datetime = min_day, end_date:datetime = curr_day):
    output_dict = {}
    output_dict['Results'] = [i for i in output['Results'] 
                            if i['date']>= start_date  and 
                            i['date'] <= end_date]
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

def get_phrase_datasets_results(query: str, top_n: int=10, spell_check=True,qe=False, start_date:datetime = min_day, end_date:datetime = curr_day) -> dict:
    """
    Uses phrase search, not ranking algorithm
    Input: query (type: string)
    Output: search results (dict)
    """
    original_query = query
    if qe:
        query = query + ' ' + ' '.join(get_query_extension(query))
    query = preprocess(query,True, True) # stemming, removing stopwords #TODO
    query_params = {'query': query}

    # These parts (getting dataset info like subtitle) must be changed to mongodb in the future
    kaggle_df = pd.read_csv('core_algorithms/ir_eval/kaggle_dataset_df_page500.csv')
    kaggle_df['Source'] = 'Kaggle'

    paperwithcode_df = pd.read_csv('core_algorithms/ir_eval/paperwithcode_df.csv')
    paperwithcode_df['Source'] = 'Paper_with_code'

    df = pd.concat([kaggle_df, paperwithcode_df])
    df = df.reset_index(drop=True)

    outputs = phrase_search_dataset(query_params) # return: list of ids of paper
    if spell_check&(len(outputs)< 25):
        new_query = ' '.join(query_spell_check(original_query))
        new_query = preprocess(new_query)
        new_query_params = {'query': new_query}
        outputs = phrase_search_dataset(new_query_params)
    output_dict = {"Results":[]}
    for result in outputs[:top_n]:
        output = df.iloc[result][['title','subtitle','description']].to_dict()
        output_dict['Results'].append(output)
    return output_dict


def get_phrase_papers_results(query: str, top_n: int=10, spell_check=True,qe=False, start_date:datetime = min_day, end_date:datetime = curr_day) -> dict:
    """
    This function is using phrase search, not ranking algorithm
    Input: query (type: string)
    Output: dict
    """
    original_query = query
    if qe:
        query = query + ' ' + ' '.join(get_query_extension(query))
    query = preprocess(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    outputs = phrase_search_paper(query_params, client, start_time=time.time()) # return: list of ids of paper
    if spell_check&(len(outputs)< 25):
        new_query = ' '.join(query_spell_check(original_query))
        new_query = preprocess(new_query)
        new_query_params = {'query': new_query}
        outputs = phrase_search_paper(new_query_params)
    output_dict = {}
    temp_result = list(client.get_data('paper', {'_id':{"$in" : outputs[:top_n]}}, ['title', 'abstract','authors', 'url', 'date']))
    temp_result = {i['_id'] : i for i in temp_result}
    output_dict["Results"] = [temp_result[i] for i in outputs[:top_n]]
    
    return output_dict


def get_proximity_datasets_results(query: str, proximity: int=10, top_n: int=10, spell_check=True,qe=False, start_date:datetime = min_day, end_date:datetime = curr_day) -> dict:
    """
    Uses proximity search, not ranking algorithm
    Input: query (type: string)
    Output: search results (dict)
    """
    original_query = query
    if qe:
        query = query + ' ' + ' '.join(get_query_extension(query))
    query = preprocess(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    
    kaggle_df = pd.read_csv('core_algorithms/ir_eval/kaggle_dataset_df_page500.csv')
    kaggle_df['Source'] = 'Kaggle'
    paperwithcode_df = pd.read_csv('core_algorithms/ir_eval/paperwithcode_df.csv')
    paperwithcode_df['Source'] = 'Paper_with_code'
    df = pd.concat([kaggle_df, paperwithcode_df])
    df = df.reset_index(drop=True)
    
    outputs = proximity_search_dataset(query_params, proximity=proximity) # return: list of ids of paper
    if spell_check&(len(outputs)< 25):
        new_query = ' '.join(query_spell_check(original_query))
        new_query = preprocess(new_query)
        new_query_params = {'query': new_query}
        outputs = proximity_search_dataset(new_query_params, proximity=proximity)
    output_dict = {"Results":[]}
    for result in outputs[:top_n]:
        output = df.iloc[result][['title','subtitle','description']].to_dict()
        output_dict['Results'].append(output)

    return output_dict



def get_proximity_papers_results(query: str, proximity: int=10, top_n: int=10, spell_check=True,qe=False, start_date:datetime = min_day, end_date:datetime = curr_day) -> dict:
    """
    This function is using proximity search, not ranking algorithm.
    By default, this function get the result of proximity=10
    Input: query (type: string)
    Output: search results (dict)
    """
    original_query = query
    if qe:
        query = query + ' ' + ' '.join(get_query_extension(query))
    query = _preprocess_query(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    outputs = proximity_search_paper(query_params, client, proximity=proximity) # return: list of ids of paper
    if spell_check&(len(outputs)< 25):
        new_query = ' '.join(query_spell_check(original_query))
        new_query = preprocess(new_query)
        new_query_params = {'query': new_query}
        outputs = proximity_search_paper(new_query_params, proximity=proximity)
    output_dict = {}

    temp_result = list(client.get_data('paper', {'_id':{"$in" : outputs[:top_n]}}, ['title', 'abstract','authors', 'url', 'date']))
    temp_result = {i['_id'] : i for i in temp_result}
    output_dict["Results"] = [temp_result[i] for i in outputs[:top_n]]
    
    return output_dict
#NOTE:DL
def get_approx_nn_datasets_results(query: str, top_n: int=100, start_date:datetime = min_day, end_date:datetime = curr_day) -> dict:
    """
    Input: query (type: string)
    Output: search results (dict)
    """
    query = model.encode(query, convert_to_tensor=True)
    neighbors, distances = searcher_dataset.search(query, final_num_neighbors=1000)

    output_dict = {}
    columns = ['title','subtitle','description', 'url']
    output_dict["Results"] = [df_datasets.iloc[i][columns].to_dict() for i in neighbors[:top_n]]
    
    return output_dict


def get_dataset_results_bm25(query: str, top_n: int=10, spell_check=True,qe=True, start_date:datetime = min_day, end_date:datetime = curr_day) -> dict:
    """
    This is used when the user provides the query & wants to query different databases.
    Input: query (type: string)
    Example: "covid" or "covid vaccine"

    Output: Dictionary (HashMap)
    Format:
    {
        title: string,
        abstract/description: string,
        authors: array of strings or empty array,
        url: string
        ...
        any other information
    } 
    """
    original_query = query
    if qe:
        query = query + ' ' + ' '.join(get_query_extension(query))
    query = _preprocess_query(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    scores = ranking_query_bm25_dataset(query_params)
    output_dict = {'Results':[]}
    if spell_check&(len(scores)< 25):
        new_query = ' '.join(query_spell_check(original_query))
        new_query = _preprocess_query(new_query)
        new_query_params = {'query': new_query}
        scores = ranking_query_bm25_dataset(new_query_params)
    # These parts (getting dataset info like subtitle) must be changed to mongodb in the future
    kaggle_df = pd.read_csv('core_algorithms/ir_eval/kaggle_dataset_df_page500.csv')
    kaggle_df['Source'] = 'Kaggle'
    paperwithcode_df = pd.read_csv('core_algorithms/ir_eval/paperwithcode_df.csv')
    paperwithcode_df['Source'] = 'Paper_with_code'
    df = pd.concat([kaggle_df, paperwithcode_df])
    df = df.reset_index(drop=True)
    
    # tfidf result is linked to index in pandas dataframe
    for result in scores[:top_n]:
        output = df.iloc[result[0]][['title','subtitle','description']].to_dict()
        output_dict['Results'].append(output)
    return output_dict



def get_tf_idf_dataset_results(query: str, top_n: int=10, spell_check=True,qe=True, start_date:datetime = min_day, end_date:datetime = curr_day) -> dict:
    """
    This is used when the user provides the query & wants to query different databases.
    Input: query (type: string)
    Example: "covid" or "covid vaccine"

    Output: Dictionary (HashMap)
    Format:
    {
        title: string,
        abstract/description: string,
        authors: array of strings or empty array,
        url: string
        ...
        any other information
    } 
    """
    original_query = query
    if qe:
        query = query + ' ' + ' '.join(get_query_extension(query))
    query = _preprocess_query(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    scores = ranking_query_tfidf_dataset(query_params)
    output_dict = {'Results':[]}
    if spell_check&(len(scores) < 25):
        new_query = ' '.join(query_spell_check(original_query))
        new_query = _preprocess_query(new_query)
        new_query_params = {'query': new_query}
        scores = ranking_query_tfidf_dataset(new_query_params)
    # These parts (getting dataset info like subtitle) must be changed to mongodb in the future
    kaggle_df = pd.read_csv('core_algorithms/ir_eval/kaggle_dataset_df_page500.csv')
    kaggle_df['Source'] = 'Kaggle'
    paperwithcode_df = pd.read_csv('core_algorithms/ir_eval/paperwithcode_df.csv')
    paperwithcode_df['Source'] = 'Paper_with_code'
    df = pd.concat([kaggle_df, paperwithcode_df])
    df = df.reset_index(drop=True)
    
    # tfidf result is linked to index in pandas dataframe
    for result in scores[:top_n]:
        output = df.iloc[result[0]][['title','subtitle','description']].to_dict()
        output_dict['Results'].append(output)
    return output_dict


#NOTE:DL
def get_approx_nn_papers_results(query: str, top_n: int=10, start_date:datetime = min_day, end_date:datetime = curr_day) -> dict:
    """
    This is used when the user provides the query & wants to query different papers.
    Input: query (type: string)
    Example: "covid" or "covid vaccine"

    Output: Dictionary (HashMap)
    Format:
    {
        title: string,
        abstract/description: string,
        authors: array of strings or empty array,
        url: string
        ...
        any other information
    } 
    """
    query = model.encode(query, convert_to_tensor=True)
    neighbors, distances = searcher.search(query, final_num_neighbors=100)

    output_dict = {}
    temp_ids = [str(df_papers.iloc[i]._id) for i in neighbors[:top_n]]
    temp_result = list(client.get_data('paper', {'_id':{"$in" : temp_ids}}, ['title', 'abstract','authors', 'url', 'date']))
    temp_result = {i['_id'] : i for i in temp_result}
    output_dict["Results"] = [temp_result[i] for i in temp_ids]
    
    return output_dict


def get_papers_results_bm25(query: str, top_n: int=10, spell_check=True,qe=False, start_date:datetime = min_day, end_date:datetime = curr_day) -> dict:
    """
    This is used when the user provides the query & wants to query different papers.
    Input: query (type: string)
    Example: "covid" or "covid vaccine"

    Output: Dictionary (HashMap)
    Format:
    {
        title: string,
        abstract/description: string,
        authors: array of strings or empty array,
        url: string
        ...
        any other information
    } 
    """
    original_query = query
    if qe:
        query = query + ' ' + ' '.join(get_query_extension(query))
    query = _preprocess_query(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    scores = ranking_query_bm25_paper(query_params, client)
    if spell_check&(len(scores) < 25):
        new_query = ' '.join(query_spell_check(original_query))
        new_query = _preprocess_query(new_query)
        new_query_params = {'query': new_query}
        scores = ranking_query_bm25_paper(new_query_params, client)
    output_dict = {}
    temp_ids = [i[0] for i in scores[:top_n]]
    temp_result = list(client.get_data('paper', {'_id':{"$in" : temp_ids}}, ['title', 'abstract','authors', 'url', 'date']))
    temp_result = {i['_id'] : i for i in temp_result}
    output_dict["Results"] = [temp_result[i] for i in temp_ids]
   
    return output_dict

def get_paper_results_tf_idf(query: str, top_n: int=10, spell_check=True,qe=False, start_date:datetime = min_day, end_date:datetime = curr_day) -> dict:
    """
    This is used when the user provides the query & wants to query different papers.
    Input: query (type: string)
    Example: "covid" or "covid vaccine"

    Output: Dictionary (HashMap)
    Format:
    {
        title: string,
        abstract/description: string,
        authors: array of strings or empty array,
        url: string
        ...
        any other information
    } 
    """
    original_query = query
    if qe:
        query = query + ' ' + ' '.join(get_query_extension(query))
    query = _preprocess_query(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    scores = ranking_query_tfidf_paper(query_params, client)
    output_dict = {}
    if spell_check&(len(scores) < 25):
        new_query = ' '.join(query_spell_check(original_query))
        new_query = _preprocess_query(new_query)
        new_query_params = {'query': new_query}
        scores = ranking_query_tfidf_paper(new_query_params, client)
    temp_ids = [i[0] for i in scores[:top_n]]
    temp_result = list(client.get_data('paper', {'_id':{"$in" : temp_ids}}, ['title', 'abstract','authors', 'url', 'date']))
    temp_result = {i['_id'] : i for i in temp_result}
    output_dict["Results"] = [temp_result[i] for i in temp_ids]
   
    return output_dict

@app.route("/QE/<query>", methods=['GET', 'POST'])
def query_expansion(query):

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

    if cached_data != -1:
        query_params = cached_data
    else:
        query_params = preprocess(query, stemming, remove_stopwords) # stemming, removing stopwords
        query_params = {'query': query_params}
        _preprocessing_cache.put(query, query_params)

    return query_params

def _deserialize(query: str) -> dict:
    print("ori", query)
    return_dict = {
        "query" :"",
        "start_date" :    datetime.min.date(),
        "end_date" :   datetime.today().date(),
        "search_type" : "DEFAULT",
        "algorithm" : "APROX_NN",
        "datasets": False,
        "start_num": 0,
        "end_num" : 0

    }

    queries = query.split("/")[:-1]

    for i in range(len(queries)):
        if i == 0:
            return_dict["query"] = queries[i].replace("+", " ")
        if i == 1:
            from_date = queries[i][3:]
            if from_date != "inf":
                return_dict["start_date"] =   datetime.strptime(from_date, '%d-%m-%Y').date()
        if i == 2:
            to_date = queries[i][3:]
            if to_date != "inf":
                return_dict["end_date"] =   datetime.strptime(to_date, '%d-%m-%Y').date()
        if i ==3:
            st = queries[i][4:]
            return_dict["algorithm"] = st.replace("+","_")
        if i == 4:
            alg = queries[i][8:]
            return_dict["search_type"] = alg.replace("+","_")
        if i == 5:
            ds = queries[i][3:]
            if ds == "true":
                return_dict["datasets"] = True

    return return_dict
