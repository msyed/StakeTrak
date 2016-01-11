# You may have to download nltk (pip install nltk)
# You may have to download nltk (pip install python-magic)
import nltk, slate
import python-magic as magic

def get_text(filepath):
	extension = filepath.split(".")[-1]
	if extension.lower == "pdf":
		# get text from pdf!
	if extension.lower == "doc":
		# get text from doc!
	if extension.lower == "docx":
		# get text from docx (basically the same as doc)
	if extension.lower == "txt":
		# simply open and return file as string.
	#if pdf:
# 		>>> with open('example.pdf') as f:
# ...    doc = slate.PDF(f)

def get_entities(filepath):

	r = []
	for sent in nltk.sent_tokenize(text):
		for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
			if hasattr(chunk, 'node'):
				r.append(chunk.node, ' '.join(c[0] for c in chunk.leaves()))
	return r



print get_entities()