from core_algorithms.query_expansion import get_query_extension
from core_algorithms.ir_eval.ranking import ranking_query_tfidf
from core_algorithms.ir_eval.ranking_paper import ranking_query_tfidf
from core_algorithms.mongoDB_API import MongoDBClient

import pandas as pd

#### Add stuff here that should run one time the server starts . 
#### this can include stuff like connecting to client or loading the index into memory.
#### basically, stuff that shouldn't be repeated.

# client = MongoDBClient("34.142.18.57") (this is an example)



###################### #####################################



def get_database_results(query: str) -> dict:
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
    query_params = {'query': query.split()}
    # Don't worry about input parsing. Use query_params for now.


    return None


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
    query_params = {'query': query.split()}
    # Don't worry about input parsing. Use query_params for now.




    # results = ranking_query_tfidf(query_params)
    # cursor = client.get_one(data_type='paper', filter={'_id':results[0]}, fields=['title', 'abstract']) 
    
    # print(results[:5])
    # print(cursor)
    return None





#### If the functions are working as expected, these functions should work.

query1 = {'query': "covid pandemic".split()}

print(get_papers_results(query1)) # these both should return Dictionary objects in the format given above
print(get_database_results(query1)) 

