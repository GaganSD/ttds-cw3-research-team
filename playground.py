from core_algorithms.query_expansion import get_query_extension
from core_algorithms.ir_eval.ranking import ranking_query_tfidf as ranking_query_tfidf_dataset
from core_algorithms.ir_eval.ranking_paper import ranking_query_tfidf as ranking_query_tfidf_paper
from core_algorithms.ir_eval.ranking_paper import phrase_search as phrase_search_paper
from core_algorithms.ir_eval.ranking import phrase_search as phrase_search_dataset
from core_algorithms.ir_eval.ranking_paper import proximity_search as proximity_search_paper
from core_algorithms.ir_eval.ranking import proximity_search as proximity_search_dataset
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
    # Don't worry about input parsing. Use query_params for now.
    scores = ranking_query_tfidf_dataset(query_params)
    output_dict = {'Results':[]}
    
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
        output_dict['Results'].append(output)
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
    for result in scores[:10]:
        output = client.get_one(data_type='paper', filter={'_id':result[0]}, fields=['title', 'abstract','authors', 'url', 'date'])
        output_dict["Results"].append(output)
    
    return output_dict

def get_phrase_papers_results(query: str) -> dict:
    """
    This is used when the user provides the query & wants to query different papers.
    This function is using phrase search, not ranking algorithm
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
    outputs = phrase_search_paper(query_params, client) # return: list of ids of paper
    output_dict = {"Results":[]}
    for result in outputs[:10]:
        output = client.get_one(data_type='paper', filter={'_id':result}, fields=['title', 'abstract','authors', 'url', 'date'])
        output_dict["Results"].append(output)
    
    return output_dict

def get_phrase_datasets_results(query: str) -> dict:
    """
    This is used when the user provides the query & wants to query different papers.
    This function is using phrase search, not ranking algorithm
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
    
    # These parts (getting dataset info like subtitle) must be changed to mongodb in the future
    kaggle_df = pd.read_csv('core_algorithms/ir_eval/kaggle_dataset_df_page500.csv')
    kaggle_df['Source'] = 'Kaggle'
    paperwithcode_df = pd.read_csv('core_algorithms/ir_eval/paperwithcode_df.csv')
    paperwithcode_df['Source'] = 'Paper_with_code'
    df = pd.concat([kaggle_df, paperwithcode_df])
    df = df.reset_index(drop=True)
    
    # Don't worry about input parsing. Use query_params for now.
    outputs = phrase_search_dataset(query_params) # return: list of ids of paper
    output_dict = {"Results":[]}
    for result in outputs[:10]:
        output = df.iloc[result][['title','subtitle','description']].to_dict()
        output_dict['Results'].append(output)
    return output_dict

def get_proximity_papers_results(query: str, proximity=10) -> dict:
    """
    This is used when the user provides the query & wants to query different papers.
    This function is using proximity search, not ranking algorithm.
    By default, this function get the result of proximity=10
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
    outputs = proximity_search_paper(query_params, client, proximity=proximity) # return: list of ids of paper
    output_dict = {"Results":[]}
    for result in outputs[:10]:
        output = client.get_one(data_type='paper', filter={'_id':result}, fields=['title', 'abstract','authors', 'url', 'date'])
        output_dict["Results"].append(output)
    
    return output_dict

def get_proximity_datasets_results(query: str, proximity=10) -> dict:
    """
    This is used when the user provides the query & wants to query different papers.
    This function is using proximity search, not ranking algorithm
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
    
    # These parts (getting dataset info like subtitle) must be changed to mongodb in the future
    kaggle_df = pd.read_csv('core_algorithms/ir_eval/kaggle_dataset_df_page500.csv')
    kaggle_df['Source'] = 'Kaggle'
    paperwithcode_df = pd.read_csv('core_algorithms/ir_eval/paperwithcode_df.csv')
    paperwithcode_df['Source'] = 'Paper_with_code'
    df = pd.concat([kaggle_df, paperwithcode_df])
    df = df.reset_index(drop=True)
    
    # Don't worry about input parsing. Use query_params for now.
    outputs = proximity_search_dataset(query_params, proximity=proximity) # return: list of ids of paper
    output_dict = {"Results":[]}
    for result in outputs[:10]:
        output = df.iloc[result][['title','subtitle','description']].to_dict()
        output_dict['Results'].append(output)
    return output_dict


#### If the functions are working as expected, these functions should work.

# query1 = {'query': "covid pandemic".split()}
query1 = "stock prediction"
print(query1)

print('Phrase search for dataset')
for i in get_phrase_datasets_results(query1)['Results']:
    print(i['title'])

print('Phrase search for paper')
for i in get_phrase_papers_results(query1)['Results']:
    print(i['url'])
    
print('Proximity search for dataset')
for i in get_proximity_datasets_results(query1)['Results']:
    print(i['title'])

print('Proximity search for paper')
for i in get_proximity_papers_results(query1)['Results']:
    print(i['url'])

print('Ranking for dataset')
for i in get_database_results(query1)['Results']:
    print(i['title'])

print('Ranking for paper')
for i in get_papers_results(query1)['Results']:
    print(i['url'])

