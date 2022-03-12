import time
from flask import Flask, request
import json
from flask_cors import CORS
 
example_json = open('../example.json', 'r')
example_data = json.load(example_json)

app= Flask(__name__)
CORS(app)

## Create DB instance

@app.route("/time")
def get_current_time():
    return {'time': time.time()}

@app.route("/", methods=['GET', 'POST'])
def query_expansion():
    return "hello"


# @app.route('/<name>')
# def get_results_datasets(query: str):
    
#     return ranking_query_tfidf(query)


# @app.route('/<name>')
# def get_results_papers(query: str):

#     return ranking_query_tfidf(query)


@app.route("/")
def hello_wolrd():
    return "Hello, World!"

@app.route("/test")
def get_test_json():
    return example_data
