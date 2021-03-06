# -*- coding: utf-8 -*-
"""Pubmed.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Gqbxm3r5l4FOI9h6Uljr4JnlCuMQTFcz
"""

from xml2txt import *
import glob
import pubmed_parser
import pandas as pd
from tqdm import tqdm
from ../mongoDB_api_live_index import *
from ../live_index_generator import *
import os
import pickle

def authors_split(list_authors):
    list_a = []
    for author in list_authors:
        f = author['forename'].replace(" ", ". ") + "."
        list_a.append((author["lastname"] + " " + f).strip())
    return ", ".join(list_a)

def live_index():
  if not os.path.exists('Pubmed'):
    os.makedirs('Pubmed')  
  
  os.system("wget -m ftp://ftp.ncbi.nlm.nih.gov/pubmed/updatefiles/* -P ./Pubmed --show-progress")

  client = MongoDBClient("34.142.18.57")

  x = "./Pubmed/ftp.ncbi.nlm.nih.gov/pubmed/"

  update_path = x + 'updatefiles/'
  update_files = glob.glob(join(update_path, '*.xml.gz'))

  file_name = "processed_files.pickle"
  if os.path.exists(file_name):
    with open(file_name, 'rb') as f:
      files_processed = pickle.load(f)
  else:
    files_processed = []


  pending_files = [i for i in update_files if i not in files_processed]

  for file in tqdm(pending_files):
    #print("DF")
    temp = pubmed_parser.parse_medline_xml(file, year_info_only=False, author_list=True)
    #print("DONE")
    temp_df = pd.DataFrame(temp)
    temp_df = temp_df[temp_df['abstract'] != ""]
    temp_df = temp_df[temp_df['languages'].str.contains("eng")]
    
    temp_df.drop(columns=['mesh_terms', 'issue', 'pages', 'journal', 'chemical_list', 
                 'publication_types', 'vernacular_title', 'medline_ta',
                'nlm_unique_id', 'other_id', 'issn_linking', 'languages', 'country', 
                      'references', 'pmc', 'affiliations'], inplace=True, errors='ignore')
    
    temp_df.drop_duplicates('title', keep="last", inplace=True)
    
    temp_df.loc[:, 'authors'] = temp_df['authors'].apply(authors_split)
    temp_df.loc[:, 'pubdate'] = pd.to_datetime(temp_df.pubdate).dt.strftime('%d/%m/%Y')
    temp_df.loc[:, 'url'] = "https://pubmed.ncbi.nlm.nih.gov/" + temp_df['pmid'] + "/"
    temp_df['text'] = ""
    # insert_dataset_data
    if temp_df.empty: continue
    #print("DF Created")

    # Update Index
    indexGen = IndexGenerator(client_ip = "34.142.18.57", activate_stemming = True, activate_stop = False, start_index=0, local_dataset=temp_df, source_name="pubmed", identifier="pmid")
    indexGen.clean_indexing()
    indexGen.run_indexing()

    success_num = client.insert_data(temp_df, "paper", "pubmed", "pmid", overwrite=True)
    #print("# data inserted ", success_num)
    
    with open(file_name, 'wb') as f:
      pickle.dump(update_files, f)