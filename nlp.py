# pip install numpy
import nltk
from extractText import extractText

def extract_entities(text):
	for sent in nltk.sent_tokenize(text):
		for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
			if hasattr(chunk, 'node'):
				print chunk.node, ' '.join(c[0] for c in chunk.leaves())



def extract_entities2(text):
    pos = nltk.pos_tag(text.split())
    keywords = [noun for noun in pos if (noun[1] == 'NNP' or noun[1] == 'NN' or noun[1] == 'NNS')]
    return keywords


x = extractText('police.txt')

#print extract_entities(x)
print extract_entities2(x)