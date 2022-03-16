
from flask import Flask, request
from flask_cors import CORS
from datetime import datetime

print(1)

# Create Flask app
app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
    return "hello"

@app.route('/<query>', methods=['GET', 'POST']) 
def run_this_bad_boi(query: str):
    print("bad brokne", _deserialize(request.args['q']))
    return {"Results":[]}

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