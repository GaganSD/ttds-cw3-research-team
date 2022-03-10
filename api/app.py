import time
from flask import Flask
import json
from flask_cors import CORS
example_json = open('../example.json', 'r')
example_data = json.load(example_json)

app= Flask(__name__)
CORS(app)

@app.route("/time")
def get_current_time():
    return {'time': time.time()}

@app.route("/")
def hello_wolrd():
    return "Hello, World!"

@app.route("/test")
def get_test_json():
    return example_data
