from pymongo import MongoClient, errors
from pymongo.errors import ConnectionFailure
import pymongo
import pandas as pd

db_name = "TTDS"
collec_name = dict()
fields_name = dict()

collec_name["paper"] = "papers_info"
collec_name["dataset"] = "datasets_info"

fields_name["paper"] = ['title', '#citations', 'date', 'abstract',
                'text', 'authors', 'keywords']
fields_name["dataset"] = ['title', 'subtitle', 'keywords', 'description', '#downloads', 
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

    # Insert_data

    ## Input
    # df: The data to be inserted. Type: pandas.Dataframe
    # data_type: The type of data. Should either be "paper" or "dataset". Type:string
    # source_identifier: name of the source, e.g. "Kaggle", "arvix". Type:string
    # identifier_field_name: name of the field of identifier in the df, could be the "url", or "title"
    #                   should be unique for each datapoint, better be breif. Type:string
    #
    ## Output(Return)
    # number of documents successfully inserted

    def insert_data(self, df, data_type ,source_identifier, identifier_field_name):
        if data_type not in ["paper", "dataset"]:
            print("type must be \"paper\" or  \"dataset\"")
            return -1

        # check fields
        missing_field = list()
        for field_name in fields_name[data_type]:
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
            self.client[db_name][collec_name[data_type]].insert_many(df.to_dict('records'), ordered=False)
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


# example of using API
if __name__ == "__main__": 

    # create a client instance
    client = MongoDBClient()
    dataset_df_ = pd.read_csv('kaggle_dataset_df_page500.csv')
    print(dataset_df_.head())

    # insert_dataset_data
    success_num = client.insert_data(dataset_df_, "database", "kaggle", "dataset_slug")
    print(success_num)
