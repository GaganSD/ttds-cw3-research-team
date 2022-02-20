from pymongo import MongoClient, errors
from pymongo.errors import ConnectionFailure
import pymongo
import pandas as pd
import logging

db_name = "TTDS"
collec_name = dict()
fields_name = dict()

collec_name["paper"] = "papers_info"
collec_name["dataset"] = "datasets_info"

collec_name_paper = "papers_info"
collec_name_dataset = "datasets_info"


# official field names
# fields_name["paper"] = ['title', '#citations', 'date', 'abstract',
#                 'text', 'authors', 'keywords']
# fields_name["dataset"] = ['title', 'subtitle', 'keywords', 'description', '#downloads', 
#                 '#views', '#votes', 'owner', 'dataset_slug']

# important fields that can't be missed.
fields_name["paper"] = ['title', 'abstract', 'text']
fields_name["dataset"] = ['title', 'description']

class MongoDBClient():
    def __init__(self):
        CONNECTION_STRING_INTERNAL = "mongodb://127.0.0.1:27017"
        # GCP_CONNECTION_STRING_INTERNAL = "mongodb://10.154.0.4:27017"
        self.client = MongoClient(CONNECTION_STRING_INTERNAL)
        try:
            self.client.admin.command('ping')
        except ConnectionFailure:
            print("Server not available")
            raise
        pass
        

    # TODO Avoid repeat data from different source (can be removed later)

    # insert_data
    ## Input
    # df: The data to be inserted. Type: pandas.Dataframe
    # data_type: The type of data. Should either be "paper" or "dataset". Type:string
    # source_identifier: name of the source, e.g. "Kaggle", "arvix". Type:string
    # identifier_field_name: name of the field of identifier in the df, could be the "url", or "title"
    #                   should be unique for each datapoint, better be breif. Type:string
    #
    ## Output(Return)
    # number of documents successfully inserted
    def insert_data(self, df, data_type, source_identifier, identifier_field_name):
        if not self.check_data_type(data_type):
            return -1

        # check fields
        missing_field = list()
        for field_name in fields_name[data_type]:
            if field_name not in set(df.columns):
                missing_field.append(field_name)

        if len(missing_field) > 0:
            logging.error("Important fields missing in dataframe! missing list: ", missing_field)
            return -1

        # rename unique identifier field
        df["_id"] = df[identifier_field_name].map(
            lambda x: self.create_unique_identifier(source_identifier, x) )
        df["source"] = source_identifier
        # print(df)

        total_num = df.shape[0]
        error_num = 0
        try:
            self.client[db_name][collec_name[data_type]].insert_many(df.to_dict('records'), ordered=False)
        except errors.BulkWriteError as e:
            error_num = len(e.details['writeErrors'])
            panic_list = list(filter(lambda x: x['code'] != 11000, e.details['writeErrors']))
            if len(panic_list) > 0:
                logging.warning(f"these are not duplicate errors {panic_list}")
            logging.info(f"Errors: {error_num - len(panic_list)} data duplicated, {len(panic_list)} data with other errors.")
        
        return total_num-error_num


    def get_data(self, data_type, source, identifier, fields):
        if not self.check_data_type(data_type):
            return -1

        cur_table = self.client[db_name][collec_name[data_type]]
        update = dict()

        res = cur_table.find(filter = {"_id":self.create_unique_identifier(source, identifier)},
                            projection = fields)
        
        if len(res) == 0:
            logging.warning("No document found in database for " + self.create_unique_identifier(source, identifier))
        else:
            logging.info(f"Found {len(res)} documents.")

        return res


    def update_data(self, data_type, source, identifier, update_content):
        if not self.check_data_type(data_type):
            return -1

        cur_table = self.client[db_name][collec_name[data_type]]
        update = dict()

        res = cur_table.find_one_and_update(filter = {"_id":self.create_unique_identifier(source, identifier)},
                                            update = {'$set':update_content}, upsert=False)

        if res == None:
            logging.warning("No document found in database for " + self.create_unique_identifier(source, identifier))
            return -1
        else:
            return 1


    def create_unique_identifier(self, source_name, ori_ui):
        return str(source_name) + '-' + str(ori_ui)

    def check_data_type(self, data_type):
        if data_type not in ["paper", "dataset"]:
            print("type must be \"paper\" or  \"dataset\"")
            return False
        else :
            return True

# example of using API
if __name__ == "__main__": 

    # create a client instance
    client = MongoDBClient()
    dataset_df_ = pd.read_csv('test.csv')
    print(dataset_df_.head())

    # insert_dataset_data
    # success_num = client.insert_data(dataset_df_, "dataset", "kaggle", "dataset_slug")
    # print("# data inserted ", success_num)

    client.update_data("dataset", "kaggle", "my-datase", {"subtitle": "new new subtitle"})
