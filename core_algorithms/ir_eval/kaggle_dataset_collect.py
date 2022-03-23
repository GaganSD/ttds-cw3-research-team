import pandas as pd
import numpy as np
import warnings
import glob
import os
os.system("kaggle command")
warnings.filterwarnings("ignore")
import json
from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()
DEBUG = False
is_old_data = False

latest_path = "kaggle_dataset_df_page500.csv"
if os.path.exists(latest_path):
    latest_data = pd.read_csv(latest_path)
    latest_data_df = latest_data.copy()
    latest_data['url'] = latest_data['ownerUser'].str.cat(latest_data['dataset_slug'], sep="_")
    urls = latest_data['url'].values
    is_old_data = True
    print(len(urls))


meta_cols = ['title', 'subtitle','keyword', 'description', 'totalDownloads', 'totalViews', 'totalVotes', 'ownerUser', 'dataset_slug']
# ownerUser and dataset_slug will be used to get URL of datasets
datasets = list()

list_page = 1
while True:
    if DEBUG:
        if list_page > 1:
            break
    print(f'Page {list_page} started....')
    dataset_list = api.dataset_list(sort_by="updated",page=list_page)#! kaggle datasets list --sort-by updated -p $list_page
    if len(dataset_list) == 0:
        print('finish')
        break
    dataset_list = dataset_list[3:]
    for dataset in dataset_list:
        tmp_title = "/".join(str(dataset).split("/")[1:])
        try:
            metadata = api.dataset_metadata(tmp_title,"./")#! kaggle datasets metadata $tmp_title
        except:
            print("couldn't get meta info")
            continue
        metadata = open('dataset-metadata.json', 'r')
        metadata = json.load(metadata)
        title = metadata['title']
        subtitle = metadata['subtitle']
        keywords = metadata['keywords']
        description = metadata['description']
        totalDownloads = metadata['totalDownloads']
        totalVotes = metadata['totalVotes']
        totalViews = metadata['totalViews']
        ownerUser = metadata['ownerUser']
        dataset_slug = metadata['datasetSlug']
        if is_old_data:
            if ownerUser + "_" + dataset_slug in urls:
                continue
        tmp_meta = [title, subtitle, keywords, description, totalDownloads, totalViews, totalVotes, ownerUser, dataset_slug]
        datasets.append(tmp_meta)
    if list_page % 5 == 0:
        datasets_df = pd.DataFrame(datasets, columns = meta_cols)
        if is_old_data:
            datasets_df = pd.concat([latest_data_df, datasets_df], axis=0)
            datasets_df = datasets_df.reset_index(drop=True)
        datasets_df.to_csv(f'kaggle_dataset_df_page{list_page}.csv', index=False)
        if list_page != 5:
            os.remove(f'kaggle_dataset_df_page{list_page-5}.csv')
    list_page += 1

datasets_df = pd.DataFrame(datasets, columns = meta_cols)   
if is_old_data:
    datasets_df = pd.concat([latest_data_df, datasets_df], axis=0)
    datasets_df = datasets_df.reset_index(drop=True)
datasets_df.to_csv(f'kaggle_dataset_df_page500.csv', index=False)