from summarizer import FrequencySummarizer
from extractText import extractText

x = FrequencySummarizer()

n = extractText("church.txt")

n = n.decode('utf-8')

print(x.summarize(n,1))
