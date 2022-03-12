import nltk

from nltk.corpus import wordnet as wn

nltk.download('wordnet')


print(wn.synsets('dog'))

print(wn.synset('dog.n.01'))
print([str(lemma.name()) for lemma in wn.synset('dog.n.01').lemmas()])