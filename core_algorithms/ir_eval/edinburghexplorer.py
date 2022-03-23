import pandas as pd


class Parser:

    def __init__(self):
        self.default_url = "https://www.research.ed.ac.uk/en/datasets/"
        self.url_prefix = "?format=&page="
        self.url_suffix = "&export=xls"
        self.max_limit = 50
        self.main_dataset = None


    def ed_research_get_repo(self, new_url=""):

        if new_url:
            url = new_url
        else: url = self.default_url

        curr_page = 0

        fst = True
        dataset = None
        while curr_page <= self.max_limit:
            # to download to the folder
            # _urllib.urlretrieve(final_url, "datasets/ed_re_1.xls")
            # path = os.getcwd() + "\datasets\ed_re_1.xls"
        # work directly with pandas
            try:
                curr_url = url + self.url_prefix + str(curr_page) + self.url_suffix
                dataset = pd.read_excel(curr_url, engine='xlrd')

                if fst:
                    self.main_dataset = dataset.copy()
                    fst = False
                else:
                    self.main_dataset = pd.concat([self.main_dataset, dataset]) 

                if curr_page == self.max_limit:
                    self.max_limit += 50
                    print(f"Max limit reached. max_limit updated to {self.max_limit}")
            except: 
                    print(f"Downloaded dataset info from page 0 to page {curr_page}.")
                    break

            if dataset.empty:
                print(f"Downloaded dataset info from page 0 to page {curr_page}.")
                break
            else:
                curr_page += 1

        try:
            self.main_dataset.drop(['Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5'], axis=1, inplace=True)
        except:
            print("couldn't drop all default irelevant columns")

        print(self.main_dataset.columns)
        print("Number of rows:", self.main_dataset.size)

        self._save_to_csv() ## PART OF CODE THAT SHOULD BE CHANGED TO MONGODB

        return None

    def _save_to_csv(self):
        self.main_dataset.to_csv('core_algorithms/ir_eval/edinburgh_research_datasets_info.csv')

        
curr_parser = Parser()
print(curr_parser.ed_research_get_repo())
    