import re
from spellchecker import SpellChecker
from textblob import TextBlob


## Tested & evaluated TextBlob, Spellchecker, and 
query = "mitocondria. Profiling tje imune Epigenome"

# b = TextBlob(query)

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
