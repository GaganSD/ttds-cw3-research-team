from core_algorithms.query_expansion import get_query_expansion
from core_algorithms.ir_eval.ranking import ranking_query_tfidf as ranking_query_tfidf_dataset
from core_algorithms.ir_eval.ranking_paper import ranking_query_tfidf as ranking_query_tfidf_paper
from core_algorithms.ir_eval.ranking_paper import phrase_search as phrase_search_paper
from core_algorithms.ir_eval.ranking import phrase_search as phrase_search_dataset
from core_algorithms.ir_eval.ranking_paper import proximity_search as proximity_search_paper
from core_algorithms.ir_eval.ranking import proximity_search as proximity_search_dataset
from core_algorithms.ir_eval.ranking import ranking_query_BM25 as ranking_query_bm25_dataset
from core_algorithms.ir_eval.ranking_paper import ranking_query_BM25 as ranking_query_bm25_paper
from core_algorithms.mongoDB_API import MongoDBClient
from collections import defaultdict
from core_algorithms.ir_eval.preprocessing import preprocess, author_preprocess
from core_algorithms.query_expansion import get_query_expansion
from core_algorithms.query_spell_check import query_spell_check

import pandas as pd
import heapq

# import scann
# from sentence_transformers import SentenceTransformer

#### Add stuff here that should run one time the server starts . 
#### this can include stuff like connecting to client or loading the index into memory.
#### basically, stuff that shouldn't be repeated.

client = MongoDBClient("34.142.18.57") # (this is an example)

'''
# Load paper index
searcher = scann.scann_ops_pybind.load_searcher('/home/stylianosc/scann/papers/glove/')
# Load dataset index
searcher_dataset = scann.scann_ops_pybind.load_searcher('core_algorithms/ir_eval/datasets/')
# Load transformer encoder
model = SentenceTransformer('all-MiniLM-L6-v2')
# Load paper indices
df_papers = pd.read_csv("/home/stylianosc/scann/papers/df.csv")
# Load dataset indices
df_datasets = pd.read_csv("core_algorithms/ir_eval/datasets/indices_dataset.csv")
###################### #####################################
'''

def get_database_results(query: str, top_n: int=10, spell_check=True,qe=True) -> dict:
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
    original_query = query
    if qe:
        query = query + ' ' + ' '.join(get_query_expansion(query))
    query = preprocess(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    # Don't worry about input parsing. Use query_params for now.
    scores = ranking_query_tfidf_dataset(query_params)
    output_dict = {'Results':[]}
    if spell_check&(len(scores) < 25):
        new_query = ' '.join(query_spell_check(original_query))
        new_query = preprocess(new_query)
        new_query_params = {'query': new_query}
        scores = ranking_query_tfidf_dataset(new_query_params)
    # These parts (getting dataset info like subtitle) must be changed to mongodb in the future
    kaggle_df = pd.read_csv('core_algorithms/ir_eval/kaggle_dataset_df_page500.csv')
    kaggle_df['Source'] = 'Kaggle'
    paperwithcode_df = pd.read_csv('core_algorithms/ir_eval/paperwithcode_df.csv')
    paperwithcode_df['Source'] = 'Paper_with_code'
    df = pd.concat([kaggle_df, paperwithcode_df])
    df = df.reset_index(drop=True)
    
    # tfidf result is linked to index in pandas dataframe
    for result in scores[:top_n]:
        output = df.iloc[result[0]][['title','subtitle','description']].to_dict()
        output_dict['Results'].append(output)
    return output_dict


def get_papers_results(query: str, top_n: int=10, spell_check=False,qe=False) -> dict:
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
    original_query = query
    if qe:
        query = query + ' ' + ' '.join(get_query_expansion(query))
    query = preprocess(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    # Don't worry about input parsing. Use query_params for now.
    scores = ranking_query_tfidf_paper(query_params, client)
    if spell_check&(len(scores) < 25):
        new_query = ' '.join(query_spell_check(original_query))
        new_query = preprocess(new_query)
        new_query_params = {'query': new_query}
        scores = ranking_query_tfidf_paper(new_query_params, client)
    output_dict = {}
    
    temp_ids = [i[0] for i in scores[:top_n]]
    
    temp_result = list(client.get_data('paper', {'_id':{"$in" : temp_ids}}, ['title', 'abstract','authors', 'url', 'date']))
    temp_result = {i['_id'] : i for i in temp_result}
    output_dict["Results"] = [temp_result[i] for i in temp_ids]
   
    return output_dict

def get_database_results_bm25(query: str, top_n: int=10, spell_check=True,qe=True) -> dict:
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
    original_query = query
    if qe:
        query = query + ' ' + ' '.join(get_query_expansion(query))
    query = preprocess(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    # Don't worry about input parsing. Use query_params for now.
    scores = ranking_query_bm25_dataset(query_params)
    if spell_check&(len(scores) < 25):
        new_query = ' '.join(query_spell_check(original_query))
        new_query = preprocess(new_query)
        new_query_params = {'query': new_query}
        scores = ranking_query_bm25_dataset(new_query_params)
    output_dict = {'Results':[]}
    
    # These parts (getting dataset info like subtitle) must be changed to mongodb in the future
    kaggle_df = pd.read_csv('core_algorithms/ir_eval/kaggle_dataset_df_page500.csv')
    kaggle_df['Source'] = 'Kaggle'
    paperwithcode_df = pd.read_csv('core_algorithms/ir_eval/paperwithcode_df.csv')
    paperwithcode_df['Source'] = 'Paper_with_code'
    df = pd.concat([kaggle_df, paperwithcode_df])
    df = df.reset_index(drop=True)
    
    # tfidf result is linked to index in pandas dataframe
    for result in scores[:top_n]:
        output = df.iloc[result[0]][['title','subtitle','description']].to_dict()
        output_dict['Results'].append(output)
    return output_dict


def get_papers_results_bm25(query: str, top_n: int=10, spell_check=True,qe=False) -> dict:
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
    original_query = query
    if qe:
        query = query + ' ' + ' '.join(get_query_expansion(query))
    query = preprocess(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    # Don't worry about input parsing. Use query_params for now.
    scores = ranking_query_bm25_paper(query_params, client)
    if spell_check&(len(scores) < 25):
        new_query = ' '.join(query_spell_check(original_query))
        new_query = preprocess(new_query)
        new_query_params = {'query': new_query}
        scores = ranking_query_bm25_paper(new_query_params, client)
    output_dict = {}
    temp_ids = [i[0] for i in scores[:top_n]]
    
    temp_result = list(client.get_data('paper', {'_id':{"$in" : temp_ids}}, ['title', 'abstract','authors', 'url', 'date']))
    temp_result = {i['_id'] : i for i in temp_result}
    output_dict["Results"] = [temp_result[i] for i in temp_ids]
   
    return output_dict

def get_phrase_papers_results(query: str, top_n: int=10, spell_check=False,qe=False) -> dict:
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
    if spell_check:
        query = ' '.join(query_spell_check(query))
    if qe:
        query = query + ' ' + ' '.join(get_query_expansion(query))
    query = preprocess(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    # Don't worry about input parsing. Use query_params for now.
    outputs = phrase_search_paper(query_params, client) # return: list of ids of paper
    
    output_dict = {}
    
    temp_result = list(client.get_data('paper', {'_id':{"$in" : outputs[:top_n]}}, ['title', 'abstract','authors', 'url', 'date']))
    temp_result = {i['_id'] : i for i in temp_result}
    output_dict["Results"] = [temp_result[i] for i in outputs[:top_n]]
    
    return output_dict

def get_phrase_datasets_results(query: str, top_n: int=10, spell_check=False,qe=False) -> dict:
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
    if spell_check:
        query = ' '.join(query_spell_check(query))
    if qe:
        query = query + ' ' + ' '.join(get_query_expansion(query))
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
    for result in outputs[:top_n]:
        output = df.iloc[result][['title','subtitle','description']].to_dict()
        output_dict['Results'].append(output)
    return output_dict

def get_proximity_papers_results(query: str, proximity: int=10, top_n: int=10, spell_check=False,qe=False) -> dict:
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
    if spell_check:
        query = ' '.join(query_spell_check(query))
    if qe:
        query = query + ' ' + ' '.join(get_query_expansion(query))
    query = preprocess(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    # Don't worry about input parsing. Use query_params for now.
    outputs = proximity_search_paper(query_params, client, proximity=proximity) # return: list of ids of paper
    
    output_dict = {}

    temp_result = list(client.get_data('paper', {'_id':{"$in" : outputs[:top_n]}}, ['title', 'abstract','authors', 'url', 'date']))
    temp_result = {i['_id'] : i for i in temp_result}
    output_dict["Results"] = [temp_result[i] for i in outputs[:top_n]]
    
    return output_dict

def get_proximity_datasets_results(query: str, proximity: int=10, top_n: int=10, spell_check=False,qe=False) -> dict:
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
    if spell_check:
        query = ' '.join(query_spell_check(query))
    if qe:
        query = query + ' ' + ' '.join(get_query_expansion(query))
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
    for result in outputs[:top_n]:
        output = df.iloc[result][['title','subtitle','description']].to_dict()
        output_dict['Results'].append(output)

    return output_dict
'''
def get_papers_results_deep(query: str, top_n: int=10) -> dict:
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
    query = model.encode(query, convert_to_tensor=True)
    neighbors, distances = searcher.search(query, final_num_neighbors=100)

    output_dict = {}
    temp_ids = [str(df_papers.iloc[i]._id) for i in neighbors[:top_n]]
    temp_result = list(client.get_data('paper', {'_id':{"$in" : temp_ids}}, ['title', 'abstract','authors', 'url', 'date']))
    temp_result = {i['_id'] : i for i in temp_result}
    output_dict["Results"] = [temp_result[i] for i in temp_ids]
    
    return output_dict


def get_datasets_results_deep(query: str, top_n: int=100) -> dict:
    """
    This is used when the user provides the query & wants to query different datasets.
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
    query = model.encode(query, convert_to_tensor=True)
    neighbors, distances = searcher_dataset.search(query, final_num_neighbors=1000)

    output_dict = {}
    columns = ['title','subtitle','description', 'url']
    output_dict["Results"] = [df_datasets.iloc[i][columns].to_dict() for i in neighbors[:top_n]]
    
    return output_dict
'''
def get_papers_authors(query: str, top_n: int=100, preprocess: bool=True) -> dict:
    '''
    Sorting order in cases of equalities: 
    1 - Descending order of number of authors matching query (if more than 1 authors)
    2 - Ascending order of position of author in the author list (sum of positions if more than 1 authors matching)
    3 - Ascending order of term appearance in the query
    '''
    if preprocess:
      query = author_preprocess(query)
    
    query_params = {'query': query}
    
    dict_occur = {}

    for author in query:
        temp_list = list(client.get_doc_from_index(term=author, index_table='a_index'))
        # Sort based on order of author
        temp_list = sorted(temp_list, key=lambda d: d['pos'][0]) 

        for i in temp_list:
          id = i['id']
          if id not in dict_occur: dict_occur[id] = [0, 0]
          dict_occur[id][0] += 1
          dict_occur[id][1] += i['pos'][0]
                    
    
    dict_occur = dict(heapq.nsmallest(top_n, dict_occur.items(), key=lambda x: (-x[1][0],x[1][1])))
    temp_ids = list(dict_occur.keys())
    
    output_dict = {}
        
    temp_result = list(client.get_data('paper', {'_id':{"$in" : temp_ids}}, ['title', 'abstract','authors', 'url', 'date']))
    temp_result = {i['_id'] : i for i in temp_result}
    output_dict["Results"] = [temp_result[i] for i in temp_ids]

    return output_dict

def authors_extensions(query: str, top_n: int=100, docs_searched: int=10, author_search_result: dict={'Results':[]}) -> dict:
  authors  = set(author_preprocess(query))
  coauthors = [author_preprocess(i['authors'])[:10] for i in sol["Results"][:docs_searched]]
  merged_coauthors = [item for sublist in coauthors for item in sublist if item not in authors]
  merged_coauthors = list(dict.fromkeys(merged_coauthors))
  
  results = get_papers_authors(merged_coauthors, top_n=100, preprocess=False)
  return results



#### If the functions are working as expected, these functions should work.

# query1 = {'query': "covid pandemic".split()}
query1 = "vision transformer"
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

print('Ranking for dataset - Tfi-df')
for i in get_database_results(query1)['Results']:
    print(i['title'])

print('Ranking for paper - Tfi-df')
for i in get_papers_results(query1)['Results']:
    print(i['url'])
    
print('Ranking for dataset - BM25 model')
for i in get_database_results_bm25(query1)['Results']:
    print(i['title'])

print('Ranking for paper - Bm25 model')
for i in get_papers_results_bm25(query1)['Results']:
    print(i['url'])
   
''' 
print('Ranking for paper - Deep Learning Model')
for i in  get_papers_results_deep(query=query1, top_n=100)['Results']:
    print(i['url'])
    
print('Ranking for datasets - Deep Learning Model')
for i in  get_datasets_results_deep(query=query1, top_n=100)['Results']:
    print(i['title'])
'''  
print('Papers by authors')
auth = get_papers_authors(query="walid", top_n=100)
for i in auth['Results']:    
    print(i['url'])

print('Papers by authors extension')
for i in authors_extensions(query="walid", top_n=100, docs_searched=10, author_search_result=auth)['Results']:
    print(i['url'])
