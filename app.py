import json
import pandas as pd
from collections import defaultdict
from flask import Flask, request
from flask_cors import CORS


from infra.LRUCache import LRUCache

from core_algorithms.query_expansion import get_query_extension
from core_algorithms.ir_eval.ranking import ranking_query_tfidf as ranking_query_tfidf_dataset
from core_algorithms.ir_eval.ranking_paper import ranking_query_tfidf as ranking_query_tfidf_paper
from core_algorithms.mongoDB_API import MongoDBClient
from core_algorithms.ir_eval.preprocessing import preprocess


#### Add stuff here that should run one time the server starts . 
#### this can include stuff like connecting to client or loading the index into memory.
#### basically, stuff that shouldn't be repeated.

client = MongoDBClient("34.142.18.57") # (this is an example)
_preprocessing_cache = LRUCache(1000)
_results_cache = LRUCache(200)

app= Flask(__name__)
CORS(app)

## Create DB instance

@app.route("/QE/<query>", methods=['GET', 'POST'])
def query_expansion(query):
    return {"QEResults":list(get_query_extension(query))}

@app.route("/<query>", methods = ['POST', 'GET'])
def get_papers_results(query: str) -> dict:
    """
    Input: query (type: string)
    Output: Dictionary (HashMap)
    Output Format:
    {
        title: string,
        abstract/description: string,
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
    print(query_params)
    print("msg 1")
    scores = ranking_query_tfidf_paper(query_params, client)
    print("msg 2")

    output_dict = {"Results":[]}
    for result in scores[:10]:
        output = client.get_one(data_type='paper', filter={'_id':result[0]}, fields=['title', 'abstract','authors', 'url', 'date'])
        output_dict["Results"].append(output)

    _results_cache.put(query, output_dict)

    return output_dict

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