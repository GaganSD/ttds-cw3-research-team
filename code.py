########
# UUN: s1854008
########
## Takes 5-6 minutes to run
########


import re
import csv
import math
from decimal import Decimal

class EVAL:

    def __init__(self):

        self.count = 0
        self.system_ress = self.read_file('system_results.csv')
        self.qrels = self.read_file('qrels.csv')

    def read_file(self, filename):
        results = []
        with open(filename, 'r', encoding='utf-8') as f:

            for line in f.readlines():
                self.count += 1
                results.append(re.sub(',', ' ', line.strip()).split())
        return results


    def _get_relevant_documents_id(self):
        relevant_docs = []
        for i in range(11):
            if i == 0:
                continue
            else:
                curr_relevant_docs = [curr[1] for curr in self.qrels if curr[0] == str(i)]
                relevant_docs.append(curr_relevant_docs)
        return relevant_docs

    def evaluate(self, write_filename):

        table_data = []
        s_i, q_i, i = 1, 1, 1

        nDCG_10 = self.nDCG_at_N(self.system_ress, 10)
        nDCG_20 = self.nDCG_at_N(self.system_ress, 20)

        precision_10 = self._get_precision_n(self.system_ress, 10)
        avg_precisions = self._get_average_precision(self.system_ress)

        recall_50 = self._get_recall_n(self.system_ress, 50)

        r_precision = self._get_r_precesion_rank(self.system_ress)


        q_i = 1
        for i in range(0, 66):
            row = []
            s = s_i
            if (i + 1) % 11 == 0:
                s_i += 1
                q_i = 'mean'
            q1 = q_i
            if q_i == 'mean':
                q_i = 1
            else: q_i += 1

            row.extend([s, q1, precision_10[i],recall_50[i], r_precision[i],avg_precisions[i], nDCG_10[i], nDCG_20[i]])
            table_data.append(tuple(row))

        with open(write_filename, 'w', encoding='utf-8', newline='') as file:
            print(1)
            output_file = csv.writer(file)
            output_file.writerow(['system_number', 'query_number', 'P@10', 'R@50', 'r-precision', 'AP', 'nDCG@10', 'nDCG@20'])
            output_file.writerows(table_data)

        return True

    def _get_precision_n(self, results, nth):
        """Get precision at nth cutoff"""
        self._count = 1
        preciisinos = []
        relevant_docs = self._get_relevant_documents_id()
        for i in range(7):
            if i == 0:
                continue
            else:
                for j in range(1, 11):
                    self._count +=  1
                    real_docs_n = [curr[2] for curr in results if (curr[0] == str(i) and curr[1] == str(j))][:nth]
                    curr_relevant_doc = relevant_docs[j - 1]
                    curr_relevant_doc = set(curr_relevant_doc).intersection(set(real_docs_n))
                    preciisinos.append(len(curr_relevant_doc) / nth)

        print(self._count)

        return self._get_mean(preciisinos)

    def _get_recall_n(self, results, N):

        recalls = []
        relevant_docs = self._get_relevant_documents_id()
        for i in range(7):
            if i == 0:
                continue
            else:
                for j in range(1, 11):
                    real_docs_n = [curr[2] for curr in results if curr[0] == str(i) and curr[1] == str(j)][:N]
                    true_positives = set(relevant_docs[j - 1]).intersection(set(real_docs_n))
                    P = len(true_positives) / len(relevant_docs[j - 1])
                    recalls.append(P)

        return self._get_mean(recalls)


    def _get_r_precesion_rank(self, results):
        self.rank_count = 0
        r_precision = []
        relevant_docs = self._get_relevant_documents_id()

        for i in range(7):
            if i == 0:
                continue
            else:
                for j in range(1, 11):
                    self.rank_count += 1
                    curr_doc_query = relevant_docs[j - 1]
                    rank = len(curr_doc_query)
                    docs_at_n = [curr[2] for curr in results if curr[0] == str(i) and curr[1] == str(j)][:rank]
                    r_precision.append(len(set(curr_doc_query).intersection(set(docs_at_n))) / rank)

        return self._get_mean(r_precision)



    def nDCG_at_N(self, results, N):
        ndcg_n = []

        def DCG_at_N(results, N):
            DCGs = []
            relevant_docs = self._get_relevant_documents_id()
            relevances = self._get_relevances()

            for i in range(7):
                if i == 0:
                    continue
                else:
                    for j in range(1, 11):
                        dcg = 0
                        Relevance_for_query = relevances[j - 1]
                        realDocs_at_N = [curr[2] for curr in results if curr[0] == str(i) and curr[1] == str(j)][:N]
                        true_positive = set(relevant_docs[j - 1]).intersection(set(realDocs_at_N))

                        for index, curr in enumerate(realDocs_at_N):
                            if index == 0 and curr in true_positive:
                                other_index = relevant_docs[j - 1].index(curr)
                                dcg += int(Relevance_for_query[other_index])
                            elif index == 0: 
                                dcg += 0
                            elif curr in true_positive:
                                    other_index = relevant_docs[j - 1].index(curr)
                                    dcg += int(Relevance_for_query[other_index]) / math.log(index + 1, 2)
                            else: dcg += 0
                        DCGs.append(dcg)
            return DCGs


        def iDCG_at_N(N):

            idcgs = []
            idcg = None
            relevant_docs = self._get_relevant_documents_id()
            relevances = self._get_relevances()

            for _ in range(1, 7):
                for j in range(1, 11):
                    idcg = 0
                    doc_relevanc_n = relevances[j - 1][:N]

                    for index in range(len(relevant_docs[j - 1][:N])):
                        if index == 0: idcg += int(doc_relevanc_n[0])
                        else: idcg += int(doc_relevanc_n[index]) / math.log(index + 1, 2)
                    idcgs.append(idcg)

            return idcgs

        for i, curr in enumerate(DCG_at_N(results, N)):
            ndcg_n.append(curr / (iDCG_at_N(N)[i]))

        return self._get_mean(ndcg_n)

    def _get_average_precision(self, real_results_list):
        precisions = []
        relevant_docs = self._get_relevant_documents_id()
        for i in range(7):

            if i == 0: continue
            else:
                for j in range(11):
                    if j == 0: continue
                    else:
                        real_docs = [curr[2] for curr in real_results_list if curr[0] == str(i) and curr[1] == str(j)]
                        num_intersection = len(set(relevant_docs[j - 1]).intersection(set(real_docs)))
                        position, nums = 0, 0
                        cur_precision = []
                        for curr_doc in real_docs:
                            position += 1
                            if curr_doc in relevant_docs[j - 1]:
                                nums += 1
                                cur_precision.append(nums / float(position))
                        if num_intersection >= 1:
                            precisions.append(sum(cur_precision) / len(relevant_docs[j - 1]))
                        else: precisions.append(0.0)
        return self._get_mean(precisions)

    def _get_mean(self, arr):
        """ Add mean val to the arr"""

        for i in range(6):
            mean = sum(arr[(i * 10 + i): (10 + i * 10 + i)]) / 10
            arr.insert((10 + (i * 10) + i), mean)

        formatted = [str(Decimal(elem).quantize(Decimal('0.000'))) for elem in arr]
        return formatted


    def _get_relevances(self):

        relevances = []
        for i in range(11):
            if i == 0:
                continue
            else:
                relevances.append(list(curr[2] for curr in self.qrels if curr[0] == str(i)))

        return relevances

print("start part 1...")
evaluation = EVAL()
evaluation.evaluate('ir_eval.csv')
print("end start part 1....")


########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
########################################################################################################################################################################################################################

## Part 2


import os
import numpy as np
from decimal import Decimal
import re
import csv
import string
from stemming.porter2 import stem
import itertools
from gensim.models import LdaModel
from gensim.corpora.dictionary import Dictionary
import math
import heapq



class TextAnalysis:

    def __init__(self, train_and_dev, stopwords):
        """Main Class for EVERYTHIN related to part 2 of the coursework"""

        self.documents = self._pre_process(train_and_dev, stopwords)
        self.quran_documents, self.quran_terms = self._get_docs_terms('quran')
        self.ot_documents, self.ot_terms = self._get_docs_terms('ot')
        self.nt_documents, self.nt_terms = self._get_docs_terms('nt')
        self.count, self.count2 = 0, 0
        self.test = np.random.rand(3,2)


    def generate_mi_chi_square(self, write_file):
        """Generate Mutual Information & chi square results to the txt file"""
        quran_mi, quran_chi_square = self._calc_main('quran')
        ot_mi, ot_chi_square = self._calc_main('ot')
        nt_mi, nt_chi_square = self._calc_main('nt')
        self.count = 0

        with open(write_file, 'w', encoding='utf-8') as file:
            
            file.write("token,score\n")
            file.write("----- Part 2 Results: Mutual Information & Chi Square Results -------\n")

            file.write("-- QURAN - Top Mutual Information --\n")
            for i in quran_mi: 
                self.count += 1
                file.write(str(i[0]) + "," + str(i[1]) + "\n")
            file.write("-- QURAN - TOP 10 CHI SQUARE --\n")
            for i in quran_chi_square: 
                self.count += 1
                file.write(str(i[0]) + "," + str(i[1]) + "\n")
            file.write("-- OT - TOP 10 MUTUAL INFORMATION --\n")
            for i in ot_mi: 
                self.count += 1
                file.write(str(i[0]) + "," + str(i[1]) + "\n")
            file.write("-- OT - TOP 10 CHI SQUARE--\n")
            for i in ot_chi_square: 
                self.count += 1
                file.write(str(i[0]) + "," + str(i[1]) + "\n")
            file.write("-- NT - TOP 10 MUTUAL INFORMATION--\n")
            for i in nt_mi:
                self.count += 1
                file.write(str(i[0]) + "," + str(i[1]) + "\n")
            file.write("-- NT - TOP 10 CHI SQUARE --\n")
            for i in nt_chi_square: 
                self.count += 1
                file.write(str(i[0]) + "," + str(i[1]) + "\n")
            file.write("------- DONE -----------")
            file.write(f"Count = {self.count2}")

        return quran_mi, quran_chi_square, ot_mi, ot_chi_square, nt_mi, nt_chi_square

    def get_LDA_stats(self, output_filename, num_topics):
        """Saves LDA stats in the output file"""
        texts = self.quran_documents + self.ot_documents + self.nt_documents
        common_dict = Dictionary(texts)

        self.lda = LdaModel([common_dict.doc2bow(text) for text in texts], num_topics=num_topics, random_state=1000, id2word= common_dict)

        q_t3, q_t10_tokens = self._get_avg_scores_token(self.quran_documents, common_dict)
        ot_t3, ot_t10_tokens = self._get_avg_scores_token(self.ot_documents, common_dict)
        nt_topic_top3, nt_t10_tokens = self._get_avg_scores_token(self.nt_documents, common_dict)
        self.count2 = 0
        with open(output_filename, 'w', encoding='utf-8') as file:
            file.write("---------- Quran - TOP 3 AVERAGE SCORES && TOP 10 TOKENS----------\n")
            for i, curr in enumerate(q_t3): 
                self.count += 1
                x = [ (i[0], round(i[1], 3)) for i in q_t10_tokens[i]]
                file.write(str(curr[0]) + ", " + str(curr[1]) + "\n" + str(x) + "\n")
            file.write("---------- OT - TOP 3 AVERAGE SCORES && TOP 10 TOKENS----------\n")
            for i, curr in enumerate(ot_t3): 
                self.count2 += 1
                x = [ (i[0], round(i[1], 3)) for i in ot_t10_tokens[i]]
                file.write(str(curr[0]) + ", " + str(curr[1]) + "\n" + str(x) + "\n")
            file.write("---------- NT - TOP 3 AVERAGE SCORES && TOP 10 TOKENS----------\n")
            for i, curr in enumerate(nt_topic_top3): 
                self.count2 += 1
                x = [ (i[0], round(i[1], 3)) for i in nt_t10_tokens[i]]
                file.write(str(curr[0]) + ", " + str(curr[1]) + "\n" + str(x) + "\n")
            file.write("------- DONE -----------\n")
            file.write(f"Count = {self.count2}")

        return True

    def _pre_process(self, read_file, stop_word_file_name):

        stop_words = []

        with open(stop_word_file_name, encoding='utf-8') as stopwords:
            stop_words = [ word.strip('\n') for word in stopwords]

        processed = []
        with open(read_file, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                curr = re.sub(r'[{}]+'.format(string.punctuation), ' ', line.strip().lower()).split()
                curr = [stem(i) for i in curr if i not in stop_words]
                processed.append(curr)            
            
        return processed

    def _get_docs_terms(self, corpora_name):

        docs = []
        for document in self.documents:
            if document[0] == corpora_name:
                docs.append(document[1:])

        words = list(itertools.chain.from_iterable(docs.copy()))
        unique_terms = list(set(words))

        return docs, unique_terms

    def _get_all_top_10_tokens(self, top_topics):
        top_10_tokens = []
        for topic in top_topics:
            top_10_tokens.append(self.lda.show_topic(topic[0]))
        return top_10_tokens


    def calc_mutual_inference(self, N11, N, P1, N01, P2, N10, P3, N00, P4):
        mi = (N11 / N) * P1 + (N01 / N) * P2 + (N10 / N) * P3 + (N00 / N) * P4
        return round(mi, 3)

    def calc_chi_square(self, N, N11, N00, N10, N01):
        numer = N * (( N11*N00 - N10*N01 ) ** 2)
        denom = (N11 + N01) * (N11 + N10) * (N10 + N00) * (N01 + N00)
        chi_square = numer / denom
        return round(chi_square, 3)

    def _calc_main(self, term):
        """
        Calculate Mutual Information & chi square for the input corpora.
        """

        try:
            if term == 'quran': target, terms, not_t_1, not_t_2 = self.quran_documents, self.quran_terms, self.ot_documents, self.nt_documents
            elif term == 'ot': target, terms, not_t_1, not_t_2 = self.ot_documents, self.ot_terms, self.quran_documents, self.nt_documents
            elif term == 'nt': target, terms, not_t_1, not_t_2 = self.nt_documents, self.nt_terms, self.quran_documents, self.ot_documents
            else: print("error: wrong term given for _calc_main")
        except:
            print("ERROR: PART 2 ERROR")

        not_t = not_t_1 + not_t_2

        N = len(target) + len(not_t_1) + len(not_t_2)
        mutual_inferences, chi_squares  = [], []


        for curr_term in terms:
            N10, N11 = 0,0
            for doc in target:
                if curr_term in doc:
                    N11 += 1

            N01 = len(target) - N11
            for dc in not_t:
                if curr_term in dc:
                    N10 += 1
            N00 = len(not_t) - N10

            P1 = N * N11 / ((N11 + N10) * (N11 + N01))
            P1 = math.log(P1, 2) if P1 != 0 else 0

            P2 = N * N01 / ((N01 + N00) * (N11 + N01))
            P2 = math.log(P2, 2) if P2 != 0 else 0

            P3 = N * N10 / ((N11 + N10) * (N10 + N00))
            P3 = math.log(P3, 2) if P3 != 0 else 0

            P4 = N * N00 / ((N01 + N00) * (N10 + N00)) 
            P4 = math.log(P4, 2) if P4 != 0 else 0

            curr_chi_square = self.calc_chi_square(N, N11, N00, N10, N01)
            curr_mutual_inference = self.calc_mutual_inference(N11, N, P1, N01, P2, N10, P3, N00, P4)

            mutual_inferences.append((curr_term, curr_mutual_inference))
            chi_squares.append((curr_term, round(curr_chi_square, 3)))

        top_10_mi =  heapq.nlargest(10, mutual_inferences, key=lambda x: x[1])  
        top_10_chi = heapq.nlargest(10, chi_squares, key=lambda x: x[1]) 

        return top_10_mi, top_10_chi

    def _get_top_3_topics(self, documents, common_dict):
        scores = []
        for q in documents:
            topic = self.lda.get_document_topics(bow=common_dict.doc2bow(q), minimum_probability=0.00)
            scores.append(topic)
        scores = list(itertools.chain.from_iterable(scores))
        averages = []
        for i in range(0, 20):
            average = sum(item[1] for item in scores if item[0] == i) / len(documents)
            averages.append((i, round(average, 3)))
        return heapq.nlargest(3, averages, key=lambda x: x[1]) 

    def _get_avg_scores_token(self, documents, common_dict):
        """Get top 3 avg scores & their respective tokens"""
        top_3_topics = self._get_top_3_topics(documents, common_dict)
        top_tokens = self._get_all_top_10_tokens(top_3_topics)
        return top_3_topics, top_tokens

part2 = TextAnalysis('train_and_dev.tsv', 'englishST.txt')
print("starting part 2....")
part2.generate_mi_chi_square('text_analysis_results_mi_chi.txt')
print("done part2")
print(part2.get_LDA_stats('text_analysis_results_lda.txt', 2))
print(part2.count)
print("part 2 done completely")


########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
########################################################################################################################################################################################################################

# Part 3

import os
import csv
from stemming.porter2 import stem
import itertools
import random
import numpy as np
from sklearn.model_selection import train_test_split
import sklearn
import scipy
from sklearn import svm
import sklearn
import collections
import string
import re
import math


class Classification:


    def __init__(self, train_and_dev_filename, test_filename, stop_word_filename):

        self.train_dev_data = self._pre_process(train_and_dev_filename, stop_word_filename)
        self.New_test_list = self._pre_process(test_filename, stop_word_filename)
        self.New_doc, self.New_class, self.New_vocab = self._get_docs_classes_vocabularies(self.New_test_list)
        self.count, self.count = 0,0
        self.cls2id = {}
        self.main_row = [['train', 'baseline'], ['dev', 'baseline'], ['test', 'baseline'], ['train', 'improved'], ['dev', 'improved'], ['test', 'improved']]


    def _pre_process(self, read_file, stop_word_file_name):

        stop_words = []
        with open(stop_word_file_name, encoding='utf-8') as stopwords:
            stop_words = [ word.strip('\n') for word in stopwords]

        processed = []
        with open(read_file, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                curr = re.sub(r'[{}]+'.format(string.punctuation), ' ', line.strip().lower()).split()
                curr = [stem(i) for i in curr if i not in stop_words]
                processed.append(curr)            
            
        return processed


    def get_bow_matrix(self, document_dt, word2id, model_type):
        """Convert to BOW format"""
        def weight(tf, df, document_dt):
            return (1 + math.log(tf, 10)) * math.log(len(document_dt)/df, 10)

        if model_type == 'improved':
            inv_posi_index_Dic = self.InvPosDic(document_dt)
        else:
            inv_posi_index_Dic = None

        matrix_size = (len(document_dt), len(word2id) + 1)
        out_of_words_idx = len(word2id)
        X = scipy.sparse.dok_matrix(matrix_size) #[doc_id, token_id]

        for i, documents in enumerate(document_dt):
            for word in documents:

                if model_type == "improved":
                    df=len(inv_posi_index_Dic[word])
                    tf=len(inv_posi_index_Dic[word][i])
                    X[i,word2id.get(word, out_of_words_idx)] += weight(tf,df,document_dt)
                else:
                    X[i, word2id.get(word, out_of_words_idx)] += 1
        return X

    def _get_docs_classes_vocabularies(self, data):
        docs, classes = [], []
        for curr in data:
            docs.append(curr[1:])
            classes.append(curr[0])

        return docs, classes, set(itertools.chain.from_iterable(docs)) # unique words/vocabulories


    def InvPosDic(self, documents):

        index = []
        inverted_p_idx = {}

        for i, document in enumerate(documents):
            for j,t in enumerate(document): index.append((t,i,j)) 

        index = sorted(index)
        for i in index:
            word, document_number, pos  = i[0], i[1], i[2] # alais
            if word not in inverted_p_idx: # check if exists  else create
                inverted_p_idx.update({word: {document_number: [pos]}})
            else:
                if document_number not in inverted_p_idx[word]:
                    inverted_p_idx[word][document_number] = [pos]
                else: inverted_p_idx[word][document_number].append(pos)

        return inverted_p_idx

    def print_stats(self, train_doc, train_class, train_vocab, test_doc, test_class, test_vocab):
        print("Number of training documents :", len(train_doc), "\n", train_doc[0:5])
        print("Number of Training classes :", len(train_class), "\n", train_class[0:5])
        print("Number of training vocabulaires :", (len(train_vocab)), "\n", train_vocab[0:5])
        print("Number of test  documents : ", len(test_doc), "\n", test_doc[0:5])
        print("Number of test classes : ", len(test_class), "\n", test_class[0:5])
        print("Number of test vocabulaires : ", len(test_vocab), "\n", test_vocab[0:5]) 
        print("Most occured category in the training set : ")
        print(collections.Counter(train_class).most_common())

        return True

    def get_stats(self, predicted_vals, true_vals):


        true_positive, false_positive, false_negative , count, results = 0, 0, 0, 0, []
        cls_ids = [self.cls2id['quran'], self.cls2id['ot'], self.cls2id['nt']]
        # print(type(cls_ids))

        for curr in cls_ids:
            for predicted_val, t in zip(predicted_vals, true_vals):
                count += 1
                if t == curr:
                    if predicted_val == curr:
                        true_positive += 1
                    else:
                        false_negative += 1
                elif predicted_val == curr:
                    false_positive += 1

            denom = true_positive + false_positive
            curr_p = round(true_positive / denom, 3)
            curr_r = round(true_positive / denom, 3)
            denom_2 = curr_p + curr_r
            curr_f1 = round((2 * curr_p * curr_r) / denom_2, 3)

            curr_result = [curr_p, curr_r, curr_f1]
            results.extend(curr_result)

        Pmacro = round(sum(results[:3]) / 3, 3)
        Rmacro = round(sum(results[3:6]) / 3, 3)
        Fmacro = round(sum(results[6:9]) / 3, 3)

        macros = [Pmacro, Rmacro, Fmacro]
        results.extend(macros)

        return results

    def train_predict(self, model_type, train_size, test_size, random_state, C):
        """select training set and testing set"""
        word2id, cls2id_  = {}, {}
        model = sklearn.svm.SVC(C=C)
        random.shuffle(self.train_dev_data)
        self.count += 1

        training_dataset, test_dataset = train_test_split(self.train_dev_data, train_size=train_size, test_size=test_size, random_state=random_state)
        docs_tr, classes_train, vocabularies_tr = self._get_docs_classes_vocabularies(training_dataset)
        docs_test, class_test, vocabularies_test = self._get_docs_classes_vocabularies(test_dataset)

        if model_type == 'baseline':
            self.print_stats(docs_tr, classes_train, vocabularies_tr, docs_test, class_test, vocabularies_test)

        for word_id, word in enumerate(vocabularies_tr): word2id[word] = word_id
        for cls_id, curr_class in enumerate(set(classes_train)): cls2id_[curr_class] = cls_id

        Y_trn = [cls2id_[i] for i in classes_train]

        if model_type == 'baseline':
            self.cls2id = cls2id_

        X_trn = self.get_bow_matrix(docs_tr, word2id, model_type)
        model.fit(X_trn, Y_trn)
        X_test = self.get_bow_matrix(docs_test, word2id, model_type)
        test_Y = [cls2id_[cat] for cat in class_test]
        pred_test_Y = model.predict(X_test)
        new_X = self.get_bow_matrix(self.New_doc, word2id, model_type)
        new_Y = [cls2id_[cat] for cat in self.New_class]
        pred_new_Y = model.predict(new_X)

        train_pred_Y = model.predict(X_trn)
        return train_pred_Y, pred_test_Y, pred_new_Y, Y_trn, test_Y, new_Y

    def get_curr_row(self, count):
        
        return self.main_row[count]

    def generate_output(self, data_path):

        train_pred_Y, pred_test_Y, pred_new_Y, Y_trn, test_Y, new_Y = self.train_predict('baseline', 0.8, 0.2, 0, 1000)
        print("generated baseline model")
        train_pred_Y_, pred_test_Y_, new_pred_Y_, train_Y_, test_Y_, new_Y_ = self.train_predict('improved', 0.9, 0.1, 0, 1000)
        print("generated improved model")
        with open(data_path, 'w', encoding='utf-8', newline='') as f:
            file = csv.writer(f)
            file.writerow(['system', 'split', 'p-quran', 'r-quran', 'f-quran', 'p-ot', 'r-ot', 'f-ot','p-nt',
                            'r-nt', 'f-nt','p-macro','r-macro','f-macro'])

            row = self.get_curr_row(0)
            row.extend(self.get_stats(train_pred_Y, Y_trn))
            file.writerow(row)
            row = self.get_curr_row(1)
            row.extend(self.get_stats(pred_test_Y, test_Y))
            file.writerow(row)
            row = self.get_curr_row(2)
            row.extend(self.get_stats(pred_new_Y, new_Y))
            file.writerow(row)
            row = self.get_curr_row(3)
            row.extend(self.get_stats(train_pred_Y_, train_Y_))
            file.writerow(row)
            row = self.get_curr_row(4)
            row.extend(self.get_stats(pred_test_Y_, test_Y_))
            file.writerow(row)
            row = self.get_curr_row(5)
            row.extend(self.get_stats(new_pred_Y_, new_Y_))
            file.writerow(row)

        return self.count


print("starting part 3...")
part3 = Classification( 'train_and_dev.tsv', 'test.tsv', 'englishST.txt')
print("built part3 base")
part3.generate_output('classification.csv')
print("generated classification.csv file for part 3")
print("ALL PARTS COMPLETED")
print("ending now...")
