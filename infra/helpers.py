import datetime


curr_day = datetime.today()
min_day = datetime.strptime("01-01-1000", '%d-%m-%Y')


def deserialize(query: str) -> dict:

    return_dict = {
        "query" :"",
        "start_date" :   datetime.min,
        "end_date" :   datetime.today(),
        "search_type" : "DEFAULT",
        "algorithm" : "APROX_NN",
        "datasets": False,
        "page_num" : 1
    }

    queries = query.split("/")[:-1]

    for i in range(len(queries)):
        if i == 0:
            return_dict["query"] = queries[i].replace("+", " ")
        if i == 1:
            from_date = queries[i][3:]
            if from_date != "inf":
                return_dict["start_date"] =   datetime.strptime(from_date, '%d-%m-%Y')
        if i == 2:
            to_date = queries[i][3:]
            if to_date != "inf":
                return_dict["end_date"] =   datetime.strptime(to_date, '%d-%m-%Y')
        if i ==3:
            st = queries[i][4:]
            return_dict["algorithm"] = st.replace("+","_")
        if i == 4:
            alg = queries[i][8:]
            return_dict["search_type"] = alg.replace("+","_")
        if i == 5:
            ds = queries[i][3:]
            if ds == "true":
                return_dict["datasets"] = True
        if i == 6:
            pn = queries[i][3:]
            return_dict["page_num"] = int(pn)

    return return_dict

def filter_dates(output: dict={'Results':[]}, start_date:datetime = min_day, end_date:datetime = curr_day):
    output_dict = {}
    output_dict['Results'] = [i for i in output['Results'] 
                            if i['date']>= start_date  and 
                            i['date'] <= end_date]
    return output_dict