import json
import pandas as pd
from collections import defaultdict
from flask import Flask, request
from flask_cors import CORS
from datetime import datetime

from infra.LRUCache import LRUCache

# from core_algorithms.query_expansion import get_query_extension
# from core_algorithms.ir_eval.ranking import ranking_query_tfidf as ranking_query_tfidf_dataset
# from core_algorithms.ir_eval.ranking_paper import ranking_query_tfidf as ranking_query_tfidf_paper
# from core_algorithms.mongoDB_API import MongoDBClient
# from core_algorithms.ir_eval.preprocessing import preprocess



from core_algorithms.query_expansion import get_query_extension
from core_algorithms.ir_eval.ranking import ranking_query_tfidf as ranking_query_tfidf_dataset
from core_algorithms.ir_eval.ranking_paper import ranking_query_tfidf as ranking_query_tfidf_paper
from core_algorithms.ir_eval.ranking_paper import phrase_search as phrase_search_paper
from core_algorithms.ir_eval.ranking import phrase_search as phrase_search_dataset
from core_algorithms.ir_eval.ranking_paper import proximity_search as proximity_search_paper
from core_algorithms.ir_eval.ranking import proximity_search as proximity_search_dataset
from core_algorithms.mongoDB_API import MongoDBClient
from core_algorithms.ir_eval.preprocessing import preprocess


# import scann
# from sentence_transformers import SentenceTransformer


# # Load paper index
# searcher = scann.scann_ops_pybind.load_searcher('/home/stylianosc/scann/papers/glove/')

# # Load transformer encoder
# model = SentenceTransformer('all-MiniLM-L6-v2')

# # Load paper indices
# df_papers = pd.read_csv("/home/stylianosc/scann/papers/df.csv")


#### Add stuff here that should run one time the server starts . 
#### this can include stuff like connecting to client or loading the index into memory.
#### basically, stuff that shouldn't be repeated.

client = MongoDBClient("34.142.18.57") # (this is an example)
_preprocessing_cache = LRUCache(1000)
_results_cache = LRUCache(200)

_today = datetime.today().strftime('%d/%m/%Y')
_no_match_sample = {"title": "No Matching Documents Were Found", "abstract": "Try expanding your query with our search suggestion", "url":"", "authors":"","date":_today}
_no_results_dict = {"Results": [_no_match_sample]}

app= Flask(__name__)
CORS(app)

## Create DB instance

@app.route("/QE/<query>", methods=['GET', 'POST'])
def query_expansion(query):

    expanded_queries = list(get_query_extension(query))
    if not expanded_queries:
        return {"QEResults": ["No matching synonyms were found!", ""]}
    else:
        expanded_queries = ", ".join(expanded_queries)
        return {"QEResults": [expanded_queries, ""]}

@app.route("/<query>", methods = ['POST', 'GET'])
def get_papers_results(query: str) -> dict:
    """
    Input: query (type: string)
    Output: Dictionary (HashMap)
    Output Format:
    { Results:[internal_dict] }
    internal_dict format:
    {
        title: string,
        abstract: string,
        authors: array of strings or empty array,
        url: string
        ...
        any other information
    }
    """
    cached_results = _results_cache.get(query)

    if cached_results != -1:
        return cached_results

    query_params = _preprocess_query(query)
    scores = ranking_query_tfidf_paper(query_params, client)

    output_dict = {"Results":[]}
    for result in scores[:10]:
        output = client.get_one(data_type='paper', filter={'_id':result[0]}, fields=['title', 'abstract','authors', 'url', 'date'])
        output_dict["Results"].append(output)

    _results_cache.put(query, output_dict)

    if len(output_dict['Results']) == 0:
        return _no_results_dict
    else: return output_dict

# def get_papers_results_deep(query: str) -> dict:
#     """
#     This is used when the user provides the query & wants to query different papers.
#     Input: query (type: string)
#     Example: "covid" or "covid vaccine"
#     Output: Dictionary (HashMap)
#     Format:
#     {
#         title: string,
#         abstract/description: string,
#         authors: array of strings or empty array,
#         url: string
#         ...
#         any other information
#     } 
#     """
#     query = model.encode(query, convert_to_tensor=True)
#     neighbors, distances = searcher.search(query, final_num_neighbors=100)
#     neighbors = list(reversed(neighbors))

#     output_dict = {"Results":[]}

#     for i in neighbors[:100]:
#         id = str(df_papers.iloc[i]._id)
#         output = client.get_one(data_type='paper', filter={'_id':id}, fields=['title', 'abstract','authors', 'url', 'date'])
#         output_dict["Results"].append(output)
    
#     return output_dict

@app.route("/dataset/<query>", methods = ['POST', 'GET'])
def get_dataset_results(query: str) -> dict:
    """
    Input: query (str)
    Output: dict
    """
    cached_results = _results_cache.get(query)

    if cached_results != -1:
        return cached_results

    processed_query = _preprocess_query(query)

    scores = ranking_query_tfidf_dataset(processed_query, client)
    output_dict = {"Results":[]}

    for result in scores[:10]:
        output = client.get_one(data_type='dataset', filter={'_id':result[0]}, fields=['title', 'abstract','authors', 'url', 'date'])
        output_dict["Results"].append(output)

    _results_cache.put(query, output_dict)

    if len(output_dict['Results']) == 0:
        return _no_results_dict
    else: return output_dict

@app.route("/papers/proximity/<query>", methods = ['POST', 'GET'])
def get_proximity_papers_results(query: str, proximity=10) -> dict:
    """
    By default, this function get the result of proximity=10
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
    query = preprocess(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    # Don't worry about input parsing. Use query_params for now.
    outputs = proximity_search_paper(query_params, client, proximity=proximity) # return: list of ids of paper
    output_dict = {"Results":[]}
    for result in outputs[:10]:
        output = client.get_one(data_type='paper', filter={'_id':result}, fields=['title', 'abstract','authors', 'url', 'date'])
        output_dict["Results"].append(output)
    
    return output_dict

def get_phrase_papers_results(query: str) -> dict:
    """
    This is used when the user provides the query & wants to query different papers.
    This function is using phrase search, not ranking algorithm
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
    query = preprocess(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    # Don't worry about input parsing. Use query_params for now.
    outputs = phrase_search_paper(query_params, client) # return: list of ids of paper
    output_dict = {"Results":[]}
    for result in outputs[:10]:
        output = client.get_one(data_type='paper', filter={'_id':result}, fields=['title', 'abstract','authors', 'url', 'date'])
        output_dict["Results"].append(output)
    
    return output_dict

def get_phrase_datasets_results(query: str) -> dict:
    """
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
    query = preprocess(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    
    # These parts (getting dataset info like subtitle) must be changed to mongodb in the future
    kaggle_df = pd.read_csv('core_algorithms/ir_eval/kaggle_dataset_df_page500.csv')
    kaggle_df['Source'] = 'Kaggle'
    paperwithcode_df = pd.read_csv('core_algorithms/ir_eval/paperwithcode_df.csv')
    paperwithcode_df['Source'] = 'Paper_with_code'
    df = pd.concat([kaggle_df, paperwithcode_df])
    df = df.reset_index(drop=True)
    
    # Don't worry about input parsing. Use query_params for now.
    outputs = phrase_search_dataset(query_params) # return: list of ids of paper
    output_dict = {"Results":[]}
    for result in outputs[:10]:
        output = df.iloc[result][['title','subtitle','description']].to_dict()
        output_dict['Results'].append(output)
    return output_dict
    
def _preprocess_query(query: str) -> dict:
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
        query_params = preprocess(query,True, True) # stemming, removing stopwords
        query_params = {'query': query_params}
        _preprocessing_cache.put(query, query_params)

    return query_params

@app.route("/")
def hello_world():
    return "Change PORT to 3000 to access the React frontend!"