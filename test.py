with open('entity_stoplist.txt', 'r') as f:
        stopwords = f.read().lower().splitlines()
print stopwords