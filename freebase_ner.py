# coding=UTF-8
from __future__ import division
import nltk
import re
import requests
from extractText import extractText

# This code comes from: https://gist.github.com/shlomibabluki/6333170

# Add your freebase key here
# If you don't have one, register at https://code.google.com/apis/console
FREEBASE_KEY = "AIzaSyC9ta4LJXt7rZ5UrGMYiJ05MqacQgNz47M"

pattern = "(?P<name>(([A-Z]+)([a-z]*)(\s)?)*)"


class NER(object):

    def __init__(self, text, key=None):
        self.text = text
        self.sentences = self.split_text(text)
        self.results = []
        self.key = key

    def split_text(self, text):
        sentences = nltk.sent_tokenize(text)
        stripped_sentences = []
        for sentence in sentences:
            stripped_sentences.append(sentence.strip())
        return stripped_sentences

    def get_options(self):
        options = set()
        for s in self.sentences:
            f = re.finditer(pattern, s)
            for a in f:
                o = a.group("name").strip()
                parts = o.split(" ")
                if len(parts) > 1:
                    options.add(o)
                    if len(parts) > 2:
                        extra_options = nltk.ngrams(parts, 2)
                        for e in extra_options:
                            options.add(" ".join(e))

        return options

    def is_person(self, possible_name):
        # Run first with filter
        freebase_server = "https://www.googleapis.com/freebase/v1/search"
        params = {
            "query": possible_name,
            "filter": "(any type:/people/person)"
        }
        if self.key:
            params["key"] = self.key
        options = requests.get(freebase_server, params=params).json()
        #print options
        #print dir(options)
        options = options.get("result", "")
        if options:
            for option in options:
                print option
                if possible_name == option["name"]:
                    # Run without filter and validate
                    mid = option["mid"]
                    params = {"query": possible_name}
                    if self.key:
                        params["key"] = self.key
                    compare = requests.get(freebase_server, params=params).json().get("result", "")
                    for result in compare:
                        if result["mid"] == mid:
                            return True
        return False

# Main method, just run "python freebase_ner.py"
def main():

    # I took this article from:
    # http://keepingscore.blogs.time.com/2013/08/21/with-beanball-justice-baseball-makes-a-rod-sympathetic/?iid=sp-main-lead

    text = extractText("police.txt")

    text = text.decode("utf-8")
    ner = NER(text, FREEBASE_KEY)
    options = ner.get_options()
    people = []
    count = 0
    for option in options:
        print "%s%% Completed" % (count / len(options) * 100)
        count += 1
        if ner.is_person(option):
            people.append(option)
    print "100% Done!\n"
    print ", ".join(people)


if __name__ == '__main__':
    main()