import nltk
def extract_entities(text):
     for sent in nltk.sent_tokenize(text):
         for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
             if hasattr(chunk, 'node'):
                 print chunk.node, ' '.join(c[0] for c in chunk.leaves())


x = "Barack Obama is the president of the United States"

extract_entities(x)