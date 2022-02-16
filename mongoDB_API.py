from pymongo import MongoClient, errors
from pymongo.errors import ConnectionFailure
import pymongo
import pandas as pd

db_name = "TTDS_test"
paper_collec_name = "papers_col_test"
dataset_collec_name = "dataset_col_test"

paper_fields = ['title', '#citations', 'date', 'abstract',
                'text', 'authors', 'keywords']
dataset_fields = ['title', 'subtitle', 'keywords', 'description', '#downloads', 
                '#views', '#votes', 'owner', 'dataset_slug']

class MongoDBClient():
    def __init__(self):
        GCP_CONNECTION_STRING_INTERNAL = "mongodb://10.154.0.4:27017"
        self.client = MongoClient(GCP_CONNECTION_STRING_INTERNAL)
        try:
            self.client.admin.command('ping')
        except ConnectionFailure:
            print("Server not available")
            raise
        pass
        
    # TODO Avoid repeat data from different source (can be removed later)
    def insert_dataset_data(self, df, source_identifier, identifier_field_name):
        # check fields
        missing_field = list()
        for field_name in dataset_fields:
            if field_name not in set(df.columns):
                missing_field.append(field_name)

        if len(missing_field) > 0:
            print("important fields missing in dataframe! missing list: ", missing_field)
            return -1

        # rename unique identifier field
        df["_id"] = df[identifier_field_name].map(
            lambda x: self.create_unique_identifier(source_identifier, x) )
        total_num = df.shape[0]
        error_num = 0
        try:
            ret = self.client[db_name][dataset_collec_name].insert_many(df.to_dict('records'), ordered=False)
        except errors.BulkWriteError as e:
            error_num = len(e.details['writeErrors'])
            panic_list = list(filter(lambda x: x['code'] != 11000, e.details['writeErrors']))
            if len(panic_list) > 0:
                print(f"these are not duplicate errors {panic_list}")
            print(f"Errors: {error_num - len(panic_list)} data duplicated, {len(panic_list)} data with other errors.")
        return total_num-error_num

    def get_data(self):
        raise NotImplementedError

    def update_data(self):
        raise NotImplementedError

    def create_unique_identifier(self, source_name, ori_ui):
        return str(source_name) + '-' + str(ori_ui)

if __name__ == "__main__":    
    client = MongoDBClient()
    dataset_df_ = pd.read_csv('kaggle_dataset_df_page500.csv')
    # dict_ = dataset_df_.to_dict('records')
    print(dataset_df_.head())
    success_num = client.insert_dataset_data(dataset_df_, "kaggle", "dataset_slug")
    print(success_num)
