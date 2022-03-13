from flask import Flask, request
import json
from flask_cors import CORS
from core_algorithms.query_expansion import get_query_extension
from core_algorithms.ir_eval.ranking import ranking_query_tfidf

example_json = open('example.json', 'r')
example_data = json.load(example_json)

app= Flask(__name__)
CORS(app)

## Create DB instance

@app.route("/QE/<query>", methods=['GET', 'POST'])
def query_expansion(query):
    return {"QEResults":list(get_query_extension(query))}

@app.route("/<query>", methods = ['POST', 'GET'])
def get_query_results(query: str):
    query_params = {'query': query.split()}

    # return ranking_query_tfidf(query_params)
    return example_data

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


