from json.tool import main
import urllib.request as _urllib
import pandas as pd
import numpy as np
import os




class Parser:

    def __init__(self):
        self.default_url = "https://www.research.ed.ac.uk/en/datasets/"
        self.url_prefix = "?format=&page="
        self.url_suffix = "&export=xls"
        self.max_limit = 100
        self.main_dataset = None


    def ed_research_get_repo(self, new_url=""):

        if new_url:
            url = new_url
        else: url = self.default_url

        curr_page = 0
            # to download to the folder
            # _urllib.urlretrieve(final_url, "datasets/ed_re_1.xls")
            # path = os.getcwd() + "\datasets\ed_re_1.xls"
        
        while curr_page <= self.max_limit:

        # work directly with pandas
            # try:
                curr_url = url + self.url_prefix + str(curr_page) + self.url_suffix
                dataset = pd.read_excel(curr_url, engine='xlrd')

                if not self.main_dataset:
                    self.main_dataset = dataset.copy()
                else:
                    self.main_dataset = pd.concat([self.main_dataset, dataset]) 
                print("---")
            # except: 
            #     print(f"Downloaded dataset info from page 0 to page {curr_page}.")
            #     # if curr_page == self.max_limit:
            #     #     self.max_limit += 50
            #     #     print(f"Updating max limit to download new data! New max_limit = {self.max_limit}")
            #     break
                curr_page += 1


        print("Dataset Downloaded.")
        print(self.main_dataset.columns)
        print("row size", self.main_dataset.size)
        # except:
        #     print("ERROR downloading dataset")
        #     return None
        

        # db = pd.read_csv(r"", encoding="utf-8")


        # try:
        #     dataset.drop(['Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5'], axis=1, inplace=True)
        # except:
        #     print("couldn't drop default irelevant columns")


    def ed_research_print_all(self):

        if not self.ed_research_repo_path:
            print("Update variable 'ed_research_repo_path' with path")
            return None
        
        dataset = pd.read_excel(self.ed_research_repo_path)

        # dataset.
        
curr_parser = Parser()
print(curr_parser.ed_research_get_repo())
    