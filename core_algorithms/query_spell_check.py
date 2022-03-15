import re
from spellchecker import SpellChecker
from textblob import TextBlob
import time


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
