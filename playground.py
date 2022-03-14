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
    query = preprocess(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    print(query_params)
    # Don't worry about input parsing. Use query_params for now.
    scores = ranking_query_tfidf_dataset(query_params)
    output_dict = dict()
    
    # These parts (getting dataset info like subtitle) must be changed to mongodb in the future
    kaggle_df = pd.read_csv('core_algorithms/ir_eval/kaggle_dataset_df_page500.csv')
    kaggle_df['Source'] = 'Kaggle'
    paperwithcode_df = pd.read_csv('core_algorithms/ir_eval/paperwithcode_df.csv')
    paperwithcode_df['Source'] = 'Paper_with_code'
    df = pd.concat([kaggle_df, paperwithcode_df])
    df = df.reset_index(drop=True)
    
    # tfidf result is linked to index in pandas dataframe
    for result in scores[:10]:
        output = df.iloc[result[0]][['title','subtitle','description']].to_dict()
        output_dict[result[0]] = output
    return output_dict


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






#### If the functions are working as expected, these functions should work.

# query1 = {'query': "covid pandemic".split()}
query1 = "haskel haskel"
print(query1)

 # these both should return Dictionary objects in the format given above
print(get_database_results(query1)) 


for i in get_papers_results(query1)['Results']:
    print(i['url'])