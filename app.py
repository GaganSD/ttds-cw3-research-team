from flask import Flask, request
import json
from flask_cors import CORS


from core_algorithms.query_expansion import get_query_extension
from core_algorithms.ir_eval.ranking import ranking_query_tfidf as ranking_query_tfidf_dataset
from core_algorithms.ir_eval.ranking_paper import ranking_query_tfidf as ranking_query_tfidf_paper
from core_algorithms.mongoDB_API import MongoDBClient
from collections import defaultdict
from core_algorithms.ir_eval.preprocessing import preprocess

import pandas as pd

#### Add stuff here that should run one time the server starts . 
#### this can include stuff like connecting to client or loading the index into memory.
#### basically, stuff that shouldn't be repeated.

client = MongoDBClient("34.142.18.57") # (this is an example)


example_json = open('example.json', 'r')
example_data = json.load(example_json)

app= Flask(__name__)
CORS(app)

## Create DB instance

@app.route("/QE/<query>", methods=['GET', 'POST'])
def query_expansion(query):
    return {"QEResults":list(get_query_extension(query))}

@app.route("/<query>", methods = ['POST', 'GET'])
def get_papers_results(query: str) -> dict:
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
    query = preprocess(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    # Don't worry about input parsing. Use query_params for now.
    scores = ranking_query_tfidf_paper(query_params, client)
    output_dict = {"Results":[]}
    print("yeee")
    for result in scores[:10]:
        output = client.get_one(data_type='paper', filter={'_id':result[0]}, fields=['title', 'abstract','authors', 'url', 'date'])
        output_dict["Results"].append(output)
    
    return output_dict

# @app.route('/<name>')
# def get_results_datasets(query: str):
    
#     return ranking_query_tfidf(query)


# @app.route('/<name>')
# def get_results_papers(query: str):

#     return ranking_query_tfidf(query)

@app.route("/")
def hello_world():
    return "Change PORT to 3000 to access the React frontend!"

@app.route("/test")
def get_test_json():
    return example_data


