########
# ML microservice
########

from infra.helpers import curr_day, min_day

import scann ## NOTE: Only works on linux machines #NOTE:DL
from flask import Flask, request
from flask_cors import CORS
import pandas as pd

from sentence_transformers import SentenceTransformer #NOTE:DL
from infra.LRUCache import LRUCache
from datetime import datetime

from core_algorithms.mongoDB_API import MongoDBClient

model = SentenceTransformer('all-MiniLM-L6-v2') #NONOTETE:DL


# Create Flask app
app = Flask(__name__)
CORS(app)

client = MongoDBClient("34.142.18.57")


print("This will take some time..")
# Load paper & dataset index.
searcher = scann.scann_ops_pybind.load_searcher('/home/stylianosc/scann/papers/') #NOTE:DL
searcher_dataset = scann.scann_ops_pybind.load_searcher('/home/stylianosc/scann/datasets/')

df = pd.read_csv("core_algorithms/ir_eval/Datasets_dataset.csv", sep='\t')
df.rename(columns={"description":"abstract"}, inplace=True)


print("Loading completed! Ready to serve!")


df_papers = pd.read_csv("/home/stylianosc/scann/papers/df.csv") #NOTE:DL

def get_approx_nn_datasets_results(query: str="", top_n: int=10, start_date:datetime = min_day, end_date:datetime = curr_day) -> dict:
    """
    Input: query (input_type: string)
    Output: search results (dict)
    """
    top_n =int(top_n)
    query = model.encode(query, convert_to_tensor=True)
    neighbors, _ = searcher_dataset.search(query, final_num_neighbors=1000)

    output_dict = {"Results":[]}

    columns = ['title','subtitle', 'abstract', 'ownerUser', 'dataset_slug', 'keyword']
    for result in neighbors[:top_n]:
        output = df.iloc[result][columns].to_dict()
        for key, value in output.items():
            output[key] = str(value)
        output["date"] = ""
        output["authors"] = output["ownerUser"]
#    output["abstract"] = output["description"]
#    output["abstract"] = output["subtitle"] + " " + output["abstract"]

        if not (output["ownerUser"].startswith("http") or output["ownerUser"].startswith("https")):
            output["url"] = "https://kaggle.com/" + output["ownerUser"] + "/" + output['dataset_slug']
        else:
            output["url"] = output["ownerUser"]

        output_dict["Results"].append(output)

    return output_dict

def get_approx_nn_papers_results(query: str="", top_n: int=10, start_date:datetime = min_day, end_date:datetime = curr_day) -> dict:
    """
    Input: query (input_type: string)
    Output: Dictionary (HashMap)
    """
    top_n = int(top_n)
    query = model.encode(query, convert_to_tensor=True)
    neighbors, _ = searcher.search(query, final_num_neighbors=1000)

    output_dict = {}
    outputs = [str(df_papers.iloc[i]._id) for i in neighbors]

    temp_result = list(client.order_preserved_get_data(id_list=outputs,
                                                       start_date=start_date, end_date=end_date,
                                                       fields=['title', 'abstract','authors', 'url', 'date'],
                                                       limit=top_n
                                                      )
                      )
    for result in temp_result:
        result["date"] = result["date"].strftime("%d/%m/%Y")

    output_dict["Results"] = temp_result
    return output_dict


@app.route("/datasets/<query>/<top_n>/<from_date>/<to_date>", methods=['GET', 'POST'])
def serve_datasets(query, top_n, from_date, to_date):
    top_n = int(top_n)
    from_date = datetime.strptime(from_date, '%Y-%m-%d')
    to_date = datetime.strptime(to_date, '%Y-%m-%d')

    return get_approx_nn_datasets_results(query, top_n, from_date, to_date)


@app.route("/papers/<query>/<top_n>/<from_date>/<to_date>", methods=['GET', 'POST'])
def serve_papers(query, top_n, from_date, to_date):
    top_n = int(top_n)

    from_date = datetime.strptime(from_date, '%Y-%m-%d')
    to_date = datetime.strptime(to_date, '%Y-%m-%d')

    return get_approx_nn_papers_results(query, top_n, from_date, to_date)

@app.route("/hello", methods=['GET'])
def say_hello():
     print("Hello, world!")

print("should start now")

#if __name__ == "__main__":
#  app.run(host='0.0.0.0', port=5002,use_reloader=False,  debug=True, threaded=True)
