from datetime import datetime
from io import StringIO
import re

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
        "page_num" : 1,
        "start_date_str": "01-01-1100",
        "end_date_str": "01-10-2500" #TODO:change this in 500 years
    }

    queries = query.split("/")[:-1]

    for i in range(len(queries)):
        if i == 0:
            return_dict["query"] = queries[i].replace("+", " ")
        if i == 1:
            from_date = queries[i][3:]
            if from_date != "inf":
                return_dict["start_date"] =   datetime.strptime(from_date, '%d-%m-%Y')
                retrun_dict["start_date_str"] = from_date
        if i == 2:
            to_date = queries[i][3:]
            if to_date != "inf":
                return_dict["end_date"] =   datetime.strptime(to_date, '%d-%m-%Y')
                return_dict["end_date_str"] = to_date
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

class Formatting:

    def __init__(self):
        """
        This class has methods that helps format markdown and latex (#TODO: Leo)
        """
        from markdown import Markdown

        Markdown.output_formats["plain"] = self._unmark_element

        self._md = Markdown(output_format="plain")
        self._md.stripTopLevelTags = False

        # For latex
        self.latex_regex = r"(\$+)(?:(?!\1)[\s\S])*\1"

    def remove_markdown(self, corpus: str) -> str:
        """
        Removes all markdown formatting from the string.
        """
        # Part of this method is derived from: 
        # https://stackoverflow.com/questions/761824/python-how-to-convert-markdown-formatted-text-to-text
        return self._md.convert(corpus)

    def remove_latex(self, corpus: str) -> str:

        return re.sub(self.latex_regex, "", corpus, 0, re.MULTILINE)

    def _unmark_element(self, element, stream=None):
        """
        Private helper method to unmark element.
        """
        if stream is None:
            stream = StringIO()
        if element.text:
            stream.write(element.text)
        for sub in element:
            self._unmark_element(sub, stream)
        if element.tail:
            stream.write(element.tail)
        return stream.getvalue()

format_ = Formatting()
test_str = "This is an example $$a \\text{$a$}$$. How to remove it? Another random math expression $\\mathbb{R}$..."
t2 = "\\begin{eqarray}...\\begin{eqarry}"

print(format_.remove_latex(test_str))
