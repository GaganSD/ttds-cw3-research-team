from pymongo import MongoClient, errors
from pymongo.errors import ConnectionFailure
import pymongo
import pandas as pd
import logging
from tqdm import tqdm
import pickle

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
    def __init__(self, IP: str="10.154.0.4"):
        """
        The initialation function of MongoDB client.

        Parameters:
            IP - The ip of the mongodb instance. Could be "10.154.0.4"(internal on GCP, default) 
                    or "34.142.18.57"(external)

        Raises:
            ConnectionFailure - raises an exception
        """
        # CONNECTION_STRING_INTERNAL = "mongodb://127.0.0.1:27017" # for test
        # EXTERNAL_IP = "34.142.18.57"
        # INTERNAL_IP = "10.154.0.4"

        self.client = MongoClient(IP + ':27017',
                     username='team',
                     password='TTDS-CourseWork_3',
                     authSource='admin')

        self.logger = logging.getLogger('mongoDB-API')
        self.logger.setLevel(logging.DEBUG)
        self.success = True
        self.block_size = 200000

        try:
            self.client.admin.command('ping')
        except ConnectionFailure:
            logging.error("Can't connect to database server.")
            self.success = False
            raise
        pass

        self.hit_list = set()
        
    def insert_data(self, df: pd.DataFrame , data_type: str, source_identifier: str, 
                        identifier_field_name: str, overwrite: bool = False):
        """
        The method to insert data.

        Parameters:
            df - The data to be inserted.
            data_type - The type of data. Should either be "paper" or "dataset".
            source_identifier - name of the source, e.g. "Kaggle", "arvix".
            identifier_field_name - name of the field of identifier in the df, could be the "url", or "title"
            overwrite - whether to overwrite if doc id duplicated. default Flase.

        Return:
            number of documents successfully inserted / overwrited
        """

        if not self.check_data_type(data_type):
            return -1

        cur_table = self.client[db_name][collec_name[data_type]]

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

        total_num = df.shape[0]
        error_num = 0

        try:
            cur_table.insert_many(df.to_dict('records'), ordered=False)
        except errors.BulkWriteError as e:
            error_num = len(e.details['writeErrors'])
            panic_list = list(filter(lambda x: x['code'] != 11000, e.details['writeErrors']))
            if len(panic_list) > 0:
                logging.warning(f"these are not duplicate errors {panic_list}")
            logging.warning(f"Errors: {error_num - len(panic_list)} data duplicated, {len(panic_list)} data with other errors.")
            if overwrite:
                for error in e.details['writeErrors']:
                    if error['code'] != 11000:
                        continue
                    cur_table.find_one_and_update(filter = {"_id":error['keyValue']['_id']},
                        update = {'$set':error['op']}, upsert=True)
                    error_num -= 1

        return total_num-error_num


    def get_data(self, data_type: str, filter: dict, fields: list, skip: int = 0, 
                    limit:int = 0):
        """
        The method to get a pymongo data cursor. 
        Note: If you are only getting one piece of data, use method get_one, which should be 
        faster.

        Parameters:
            data_type - The type of data. Should either be "paper" or "dataset".
            filter - Filter for the data you want. e.g. { "source": "kaggle" }.
            fields -  Fields of information you want. e.g. [ "title", "text", "description" ].
            skip - start point, or docs to be skip at begining. default 0
            limit - max size of return result. default 0 (which means no limit)

        Returns:
            a mongodb cursor. Type: pymongo.cursor.Cursor
            the cursor can only be iterated in the following way:
                for doc in cursor:
            Don't use index or len() method.
        """
        if not self.check_data_type(data_type):
            return -1

        cur_table = self.client[db_name][collec_name[data_type]]

        cursor = cur_table.find(filter = filter, projection = fields, skip = skip, 
                                    limit = limit)
        # num = cur_table.count_documents(filter)

        try:
            cursor[0]
        except IndexError as e:
            logging.warning("can't find documents")
            
        return cursor
    
    def get_one(self, data_type: str, filter: dict, fields: list):
        """
        The method to get ONLY ONE data from db. should be more efficient than get_data. 

        Parameters:
            data_type - The type of data. Should either be "paper" or "dataset".
            filter - Filter for the data you want. e.g. { "source": "kaggle" }.
            fields -  Fields of information you want. e.g. [ "title", "text", "description" ].

        Returns:
            the doc in form of python dictionary.
            could be None if no data meets the filter.
        """
        if not self.check_data_type(data_type):
            return -1

        res = self.client[db_name][collec_name[data_type]].find_one(filter = filter, projection = fields)

        return res


    def update_data(self, data_type: str, source: str, identifier: str, update_content: dict):
        """
        The method to update a certain piece of data

        Parameters:
            data_type - The type of data. Should either be "paper" or "dataset". Type:string
            source - name of the source, e.g. "Kaggle", "arvix". Type:string
            identifier - identifier you used before. e.g. "0704.0001" (if from arxiv). Type:string  
            update_content - content you want to set. Type:python dictionary

        Returns:
            A boolean value suggesting whether the update successed. 
        """
        if not self.check_data_type(data_type):
            return False

        cur_table = self.client[db_name][collec_name[data_type]]

        res = cur_table.find_one({"_id":self.create_unique_identifier(source, identifier)})
        if res == None:
            logging.warning("No document found in database for " + self.create_unique_identifier(source, identifier))
            return False

        cur_table.find_one_and_update(filter = {"_id":self.create_unique_identifier(source, identifier)},
                                            update = {'$set':update_content}, upsert=False)

        if res.modified_count == 0:
            logging.warning("Update failed. " + self.create_unique_identifier(source, identifier))
            return False
        else:
            return True


    def update_index(self, term: str, update_list: list):
        """
        The method to update the index content of a term
        WARNING: DO OVERWRITE at [term][doc_id] level. (pos and len)

        Parameters:
            term - The term to be updated.
            update_list - The content to be updated. e.g. {doc_id: {"pos":[], "len":X}}
        """

        cur_table = self.client[db_name]["index"]
        hq = cur_table.find_one({"_id": term})
        cur_size = 0
        cur_chain = [term]
        if hq == None:
            cur_table.insert_one({"_id": term, "doc_count": 0, "docs": [], "chain": [term]})
        else:
            cur_size = hq["doc_count"] 
            cur_chain = hq["chain"]

        chain_id = 0

        new_chain = [cur_chain[-1]]
        s = 0
        e = min(len(update_list), self.block_size - cur_size % self.block_size)
        cnt = 0
        while 1:
            if chain_id >= len(new_chain):
                id = cur_table.insert_one({"term": term, "docs": []}).inserted_id
                new_chain.append(id)
            try:
                cur_table.find_one_and_update(
                    filter = {"_id":new_chain[chain_id]}, 
                    update = {'$push':{ "docs" : {'$each' : update_list[s:e]}} 
                            }, upsert=False)
                cnt = 0
            except pymongo.errors.OperationFailure:
                if cnt > 1:
                    raise pymongo.errors.OperationFailure
                chain_id += 1
                cnt += 1
                continue

            chain_id += 1
            s = e
            if s >= len(update_list):
                break
            e = min(len(update_list), s + self.block_size)

        cur_table.find_one_and_update(
                filter = {"_id": term}, 
                update = {'$inc':{"doc_count" : len(update_list)},
                        '$push':{ "chain" : {'$each' : new_chain[1:]}} 
                        }, upsert=False)

    def get_doc_from_index(self, term: str):
        """
        The method to get the docs with an index. 
        Warning: This method could be really slow (worst can take minutes)
        If you have a limit on the number of docs you are retrieving, 
        use get_topk_doc_from_index instead.

        Parameters:
            term - The index to be searched.

        Return:
            ans : the list of docs
        """
        cur_table = self.client[db_name]["index"]
        hq = cur_table.find_one({"_id": term}, {"chain": 1, "docs": 1})

        if hq == None:
            return []

        ans = []
        cursor = cur_table.find({"_id": {"$in": hq["chain"]}}, {'docs': 1})

        for doc in cursor:
            ans.extend(doc["docs"])

        return ans
    
    def get_topk_doc_from_index(self, term: str, k = 10):
        """
        The method to get the topk docs with an index. "Top" here means having most 
         appearances of the term.

        Parameters:
            term - The index to be searched.
            k - The number of documents tobe retrieved

        Return:
            ans : the list of docs
        """
        cur_table = self.client[db_name]["index"]
        hq = cur_table.find_one({"_id": term}, { "chain": 1 })

        if hq == None:
            return []

        ptr_list = []
        doc_lists =[]
        cursor = cur_table.find({"_id": {"$in": hq["chain"]}}, {'docs': {"$slice": k }})
        for doc in cursor:
            doc_lists.append(doc["docs"])
            ptr_list.append(0)

        ans = []
        pqueue = queue.PriorityQueue()

        for i in range(len(hq["chain"])):
            # print((doc_lists[i][0]["len"]))
            pqueue.put((-doc_lists[i][0]["len"], i))

        for i in range(k):
            _, list_id = pqueue.get()
            doc = doc_lists[list_id][ptr_list[list_id]]
            ans.append(doc)
            ptr_list[list_id] += 1
            pqueue.put((-doc_lists[list_id][ptr_list[list_id]]["len"], list_id))

        return ans


    def create_unique_identifier(self, source_name, ori_ui):
        return str(source_name) + '-' + str(ori_ui)

    def check_data_type(self, data_type):
        if data_type not in ["paper", "dataset"]:
            print("type must be \"paper\" or  \"dataset\"")
            return False
        else :
            return True

    def duplicate_removal(self):
        data_type = 'paper'
        cur_table = self.client[db_name][collec_name[data_type]]

        cursor = cur_table.find({})
        t = tqdm(total=23243349)
        remove_cnt = 0
        print("start!")
        for doc in cursor:
            cur_title = doc['title']
            res = cur_table.delete_many({'title':cur_title})
            cur_table.insert_one(doc)
            remove_cnt += res.deletedCount - 1

            t.update()
            
        t.close()
        print("removed ", remove_cnt)


# example of using API
if __name__ == "__main__": 
    # create a client instance
    client = MongoDBClient(IP = "34.142.18.57")
    # dataset_df_ = pd.read_csv('kaggle_dataset_df_page500.csv')
    # print(dataset_df_.head())

    # # # insert_dataset_data
    # insert_num = client.insert_data(dataset_df_, "dataset", "kaggle", "dataset_slug", overwrite=True)

    # # update data
    # client.update_data("dataset", "kaggle", "my-datase", {"subtitle": "new subtitle"})


    # # get cursor for documents
    # cursor, num = client.get_data("dataset", {'source':'kaggle'}, ['title', 'description', 'text'])
    # # print(num)
    # for doc in cursor:
    #     print(doc)


    # duplicate_removal
    # client.duplicate_removal()

    # cursor = client.get_data("paper", {}, [], 3, 100)
    # for doc in cursor:
    #     print(doc)

    # res = client.get_doc_from_index("data")
    # print(len(res), res[100])
