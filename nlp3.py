import nltk
from extractText import extractText
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


def get_entity_names_sentences(text):
    entity_names = []
    sentences = nltk.sent_tokenize(text)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)

    for tree in chunked_sentences:
        # Print results per sentence
        # print extract_entity_names(tree)
        
        entity_names.extend(extract_entity_names(tree))

# Print all entity names
#print entity_names
# return unique entity names
    return set(entity_names)

# get sentences in which the person appears
def sentextract(text, entity):
    entity = entity.lower()
    sentences = nltk.sent_tokenize(text)
    tensent = [None] * 10
    count = 0
    for sent in sentences:
        if entity in sent.lower() and count < 10:
            tensent[count] = sent
            count += 1
    return tensent





