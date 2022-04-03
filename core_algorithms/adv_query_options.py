from distutils import extension
from spellchecker import SpellChecker
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.stem.snowball import SnowballStemmer

import re
import time
import itertools
import nltk

nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('omw-1.4')

def query_spell_check(query):
    s = re.sub(r'[^\w\s]','', query)
    wordlist = s.split()
    spell = SpellChecker()
    # find those words that may be misspelled
    misspelled_list = list(spell.unknown(wordlist))
    # To keep the query order
    misspelled = [word for word in wordlist if word in misspelled_list]
    new_query = []
    for word in wordlist:
        if word not in misspelled:
            new_query.append(word)
        else:
            curr = spell.correction(word)
            new_query.append(curr)
    return new_query

def get_query_expansion(query: str) -> list:
    """Returns a list of query expansion"""

    # TODO: integrate this with existing queries to remove redundancy
    stemmer = SnowballStemmer("english")
    tokens = nltk.word_tokenize(query)

    # remove stop words
    # TODO: Integrate this with our stopwords list
    filtered_words = [word for word in tokens if word not in stopwords.words('english')]
    pos = nltk.pos_tag(filtered_words)

    synonyms_all_words = []  # synonyms of all the tokens
    index = 0
    # iterating through the tokens
    for item in filtered_words:
        synsets = wordnet.synsets(item)

        if not synsets:
            # stemming the tokens in the query
            synsets = wordnet.synsets(stemmer.stem(item))

        # synonyms of the current token
        currentSynonyms = []
        currentPOS = _get_wordnet_pos(pos[index])

        for i in synsets:
            # check if token and synset have the same PoS
            if str(i.pos()) == str(currentPOS):

                for j in i.lemmas():
                    if j.name() not in currentSynonyms:  # if we have not
                        currentSynonyms.append(j.name().replace("_", " "))

            synonyms_all_words.append(currentSynonyms)
        index += 1
    
    # remove duplicates in the synonyms list
    tmp = []
    for elem in synonyms_all_words:
        if elem and elem not in tmp:
            tmp.append(elem)

    synonyms_all_words = tmp

    query_parts = query.split()
    extensions = []
    
    seen = set()
    seen.add(query)

    for curr in query_parts:
        seen.add(curr)

    if len(synonyms_all_words) < 2:
        max_cap = 2
    else: max_cap = 2

    for possible_word_suggestions in synonyms_all_words:
        num_extensions = max_cap
        for curr_suggestion in possible_word_suggestions:

            if num_extensions == 0:
                break
            for word_suggestion in curr_suggestion.split():
                if word_suggestion not in seen:
                    extensions.append(word_suggestion)
                    seen.add(word_suggestion)
                    num_extensions -= 1
            # if curr_suggestion not in seen: # remove duplicates
            #     extensions.append(curr_suggestion)
            #     seen.add(curr_suggestion)
            #     num_extensions -=1

    return extensions


def _get_wordnet_pos(tag:str) -> str:

    if tag[1].startswith('J'):
        return wordnet.ADJ
    elif tag[1].startswith('N'):
        return wordnet.NOUN
    elif tag[1].startswith('R'):
        return wordnet.ADV
    elif tag[1].startswith('V'):
        return wordnet.VERB
    else: return ''


if __name__ == '__main__':
    ## Tested & evaluated TextBlob, Spellchecker, and 
    # query = "mitocondria. Profiling tje imune Epigenome"
    query = 'schol algorihm chargerr baseball'
    start_time = time.time()
    new_query = query_spell_check(query)
    print(new_query)
    print(time.time()-start_time)

    '''
    b = TextBlob(query)
    # print(b.correct())

    # query

    print("Original Text: ", query)
    b = TextBlob(query)
    print("Corrected text: ", str(b.correct()))

    #remove all punctuations before finding possible misspelled words
    s = re.sub(r'[^\w\s]','', query)
    print("Text without punctuations: ",s)
    wordlist = s.split()
    spell = SpellChecker()
    # find those words that may be misspelled
    misspelled = list(spell.unknown(wordlist))
    print("Possible list of misspelled words in the original text: ", misspelled)
    new_query = []

    for word in misspelled:

        curr = spell.correction(word)
        new_query.append(word)
        print("Correct word:",spell.correction(word))
    '''
    
    queries = ["cat", "hello world", "poggers", "apple"]

    for curr_query in queries:
        print(get_query_expansion(curr_query))

