from nltk import sent_tokenize, word_tokenize, ne_chunk_sents, pos_tag_sents #, pos_tag
#import nltk.data, nltk.tag
#tagger = nltk.data.load(nltk.tag._POS_TAGGER)
from extractText import extractText
import time
#with open('sample.txt', 'r') as f:
 #   sample = f.read().decode('utf-8')

def extract_entity_names(t):
    entity_names = []

    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))

    return entity_names


def get_entity_names(text, customstoplist):
    t1 = time.time()
    entity_names = []
    sentences = sent_tokenize(text)
    t2 = time.time()
    tokenized_sentences = [word_tokenize(sentence) for sentence in sentences]
    t3 = time.time()
    #tagged_sentences = [tagger.tag(sentence) for sentence in tokenized_sentences]
    tagged_sentences = pos_tag_sents(tokenized_sentences)
    #tagged_sentences = [pos_tag(sentence) for sentence in tokenized_sentences]
    t4 = time.time()
    chunked_sentences = ne_chunk_sents(tagged_sentences, binary=True)
    t5 = time.time()

    for tree in chunked_sentences:
        # Print results per sentence
        # print extract_entity_names(tree)
        
        entity_names.extend(extract_entity_names(tree))

    t6 = time.time()
    times = [(i - t1) for i in [t1, t2, t3, t4, t5, t6]]
    print "times:"
    print times
# Print all entity names
# print entity_names
# return unique entity names
    #return set(entity_names)

    # clean entity names
    stopwords = []
    with open("entity_stoplist.txt", 'r') as f:
        stopwords = f.read().lower().split('\n')
    with open(customstoplist, 'r') as f:
        stopwords = stopwords + f.read().lower().split('\n')
    newentitylist = [word for word in set(entity_names) if word.lower() not in set(stopwords)]
    #newentitylist = set(entity_names) - set(stopwords)
    return newentitylist


# get sentences in which the person appears
def sentextract(text, entity, max_value):
    entity = entity.lower()
    sentences = sent_tokenize(text)
    n_sent = []
    count = 0
    for sent in sentences:
        if count > (max_value - 1):
            break
        if entity in sent.lower():
            n_sent.append(sent)
            count += 1
    return n_sent








