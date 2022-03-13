from core_algorithms.query_expansion import get_query_extension
from core_algorithms.ir_eval.ranking import ranking_query_tfidf
from core_algorithms.mongoDB_API import MongoDBClient


def get_query_results(query: str):
    query_params = {'query': query.split()}

    results = ranking_query_tfidf(query_params)
    cursor = client.get_one(data_type='paper', filter={'_id':results[0]}, fields=['title', 'abstract']) 

    # print(results[:5])
    print(cursor)
    # return {"Results":results}
client = MongoDBClient("34.142.18.57")
print(get_query_results("covid"))