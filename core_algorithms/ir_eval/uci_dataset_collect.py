# ================================================================================================
# Function to build a local database (CSV file) with name and URL (of raw data page) information
# ================================================================================================
def build_local_database(filename=None, msg_flag=True):
    """
    Reads through the UCI ML portal and builds a local table with information such as: \
    name, size, ML task, data type
    filename: Optional filename that can be chosen by the user
    """
    df_local = build_full_dataframe(msg_flag=msg_flag)
    try:
        if filename != None:
            df_local.to_csv(filename)
        else:
            df_local.to_csv("UCI database.csv")
    except:
        print(
            "Sorry, could not create the CSV table. Please make sure to close an already opened file, \
        or to have sufficient permission to write files in the current directory"
        )

# ======================================================================================
# Function to create dictionary of datasets' name, description, and identifier string
# ======================================================================================
def build_dataset_dictionary(
    url="https://archive.ics.uci.edu/ml/datasets.php?format=&task=&att=&area=&numAtt=&numIns=&type=&sort=nameUp&view=list",
    msg_flag=True,
):
    """
    Scrapes through the UCI ML datasets page and builds a dictionary of all datasets with names and description.
    Also stores the unique identifier corresponding to the dataset.
    This identifier string is needed by the downloader function to download the data file. Generic name won't work.
    """
    import urllib.request, urllib.parse, urllib.error
    from bs4 import BeautifulSoup
    import ssl
    import time
    import re

    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = url
    if msg_flag:
        print("Opening the file connection...")
    try:
        uh = urllib.request.urlopen(url, context=ctx)
        html = uh.read()
    except:
        print("Could not open the UCI ML portal successfully. Sorry!")
        return -1

    soup = BeautifulSoup(html, "html5lib")

    lst = []
    for tag in soup.find_all("p"):
        lst.append(tag.contents)

    i = 0
    description_dict = {}

    for l in lst:
        if len(l) > 2:
            if str(l[1]).find("datasets/") != -1:
                string = str(l[1])
                s = re.search('">.*</a>', string)
                x, y = s.span()
                name = string[x + 2 : y - 4]
                desc = l[2][2:]
                tmp_list = []
                description_dict[name] = tmp_list
                description_dict[name].append(desc)
                s = re.search('".*"', string)
                x, y = s.span()
                identifier = string[x + 10 : y - 1]
                description_dict[name].append(identifier)
                i += 1
        if msg_flag:
            if i % 10 == 0 and i != 0:
                print(f"Record {i} processed!")

    return description_dict

# ===============================================================
# Function to create a DataFrame with all information together
# ===============================================================
def build_full_dataframe(msg_flag=False):
    """
    Builds a DataFrame with all information together including the url link for downloading the data.
    """
    import pandas as pd
    import urllib.request, urllib.parse, urllib.error
    from bs4 import BeautifulSoup
    import ssl
    import time

    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    i = 0
    d = build_dataset_dictionary(msg_flag=False)
    new_d = {}
    dataset_list = build_dataset_list(msg_flag=False)

    for k, v in d.items():
        a = extract_url_dataset(v[1], msg_flag=msg_flag)
        if a != None:
            desc = v[0]
            identifier = v[1]
            v[0] = k
            v[1] = desc
            v.append(identifier)
            v.append(a)
            new_d[k] = v
            i += 1
            if msg_flag:
                print(f"Dataset processed:{k}")
        else:
            desc = v[0]
            identifier = v[1]
            v[0] = k
            v[1] = desc
            v.append(identifier)
            v.append("URL not available")
            new_d[k] = v
            if msg_flag:
                print(f"Dataset processed:{k}")
    if msg_flag:
        print("\nTotal datasets analyzed: ", i)

    df_dataset = pd.DataFrame(data=new_d)
    df_dataset = df_dataset.T
    df_dataset.columns = ["Name", "Abstract", "Identifier string", "Datapage URL"]
    df_dataset.index.set_names(["Dataset"], inplace=True)

    return df_dataset


# ==================================================================
# Function to read the main page text and create list of datasets
# ==================================================================
def build_dataset_list(url="https://archive.ics.uci.edu/ml/datasets", msg_flag=True):
    """
    Scrapes through the UCI ML datasets page and builds a list of all datasets.
    """

    import urllib.request, urllib.parse, urllib.error
    from bs4 import BeautifulSoup
    import ssl
    import time

    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Read the HTML from the URL and pass on to BeautifulSoup
    url = url
    if msg_flag:
        print("Opening the file connection...")
    try:
        uh = urllib.request.urlopen(url, context=ctx)
        # print("HTTP status",uh.getcode())
        html = uh.read()
        # print(f"Reading done. Total {len(html)} characters read.")
    except:
        print("Could not open the UCI ML portal successfully. Sorry!")
        return -1

    soup = BeautifulSoup(html, "html5lib")

    dataset_list = []
    lst = []

    for link in soup.find_all("a"):
        lst.append(link.attrs)

    if msg_flag:
        print()
        print("Adding datasets to the list", end="")

        for i in range(11):
            time.sleep(0.3)
            print(".", end="")
        print(" ", end="")

    for l in lst:
        a = l["href"]
        if a.find("/") != -1:
            x = a.split("/")
            if len(x) == 2:
                dataset_list.append(x[1])

    dataset_list = list(set(dataset_list))
    dataset_list = sorted(dataset_list)

    if msg_flag:
        print("\nFinished adding datasets to the list!")

    return dataset_list


# ==========================================
# Function for extracting dataset page url
# ==========================================
def extract_url_dataset(dataset, msg_flag=False):
    """
    Given a dataset identifier this function extracts the URL for the page where the actual raw data resides.
    """
    import urllib.request, urllib.parse, urllib.error
    from bs4 import BeautifulSoup
    import ssl
    import time

    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    dataset_dict = {}
    baseurl = "https://archive.ics.uci.edu/ml/datasets/"
    url = baseurl + dataset

    try:
        uh = urllib.request.urlopen(url, context=ctx)
        html = uh.read().decode()
        soup = BeautifulSoup(html, "html5lib")
        if soup.text.find("does not appear to exist") != -1:
            if msg_flag:
                print(f"{dataset} not found")
            return None
        else:
            for link in soup.find_all("a"):
                if link.attrs["href"].find("machine-learning-databases") != -1:
                    a = link.attrs["href"]
                    a = a[2:]
                    dataurl = "https://archive.ics.uci.edu/ml/" + str(a)
                    # print(dataurl)
                    return str(dataurl)
                    # dataurls.append(dataurl)

            # After finishing the for-loop with a-tags, the first dataurl is added to the dictionary
            # dataset_dict['dataurl']=dataurls[0]
    except:
        # print("Could not retrieve")
        return None

print("building")
build_local_database("uci_dataset_test.csv",msg_flag=True)
print("done")