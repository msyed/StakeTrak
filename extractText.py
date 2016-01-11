# pip install nltk
# pip install pyinstaller
# pip install pdfminer

# If those dont work, try
# pip install python-docx
# pip install docx
# sudo pip install --upgrade --ignore-installed slate==0.3 pdfminer==20110515
# pip install Image
# brew install caskroom/cask/brew-cask
# brew cask install xquartz

import nltk, os

from docx.docx import *

import textract

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

def extractText(filepath):
	extension = filepath.split(".")[-1]
	if extension.lower() == "pdf":
		# http://stackoverflow.com/questions/26494211/extracting-text-from-a-pdf-file-using-pdfminer-in-python
		rsrcmgr = PDFResourceManager()
		retstr = StringIO()
		codec = 'utf-8'
		laparams = LAParams()
		device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
		fp = file(filepath, 'rb')
		interpreter = PDFPageInterpreter(rsrcmgr, device)
		password = ""
		maxpages = 0
		caching = True
		pagenos=set()
		for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
		    interpreter.process_page(page)
		text = retstr.getvalue()

		fp.close()
		device.close()
		retstr.close()
		return text

	if extension.lower() in  ["doc", "docx"]:
		# Might have to do some shit like this:
		# http://textract.readthedocs.org/en/latest/installation.html
		document = opendocx(filepath)
		# This location is where most document content lives 
		# https://github.com/mikemaccana/python-docx/blob/master/HACKING.markdown#user-content-a-note-about-namespaces-and-lxml
		docbody = document.xpath('/w:document/w:body', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})[0]
		# Extract all text
		lines = getdocumenttext(document)
		text_string = ""
		for line in lines:
			text_string = text_string + line + "\n"
		return text_string
	else:
		# simply open and return file as string.
		with open(filepath) as f:
			return f.read()


# print get_text('Welcome to the Python docx module.docx')
# print "_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-"
# print get_text('index.py')

