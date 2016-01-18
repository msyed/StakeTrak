import nlp3

x = open("entity_stoplist.txt", 'r')
stopwords = x.read().lower().split()
print stopwords