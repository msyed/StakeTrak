# "Text Analysis by AlchemyAPI"
# This function will get the top five articles about a certain named entity
import requests
import json

test = True

def getArticles(entity):
	# make API call, 
	r = requests.get('https://gateway-a.watsonplatform.net/calls/data/GetNews?outputMode=json&start=now-1d&end=now&count=5&q.enriched.url.text=%s&return=enriched.url.url,enriched.url.title&apikey=55eb5cb57b84be0d71af05dc4cc485388474f424' % entity)
	# define variables

	# in case doesnt work: my API key: 251038a9c65c854b638a4d401509a398e9b9f1c9 is , Milton API key is 55eb5cb57b84be0d71af05dc4cc485388474f424
	myjson = r.json()
	articleset = []

	if 'result' not in myjson.keys():
		print 'For DEBUGGING PURPOSES: Error in API call'
		return 'Error in API call'

	if 'docs' not in myjson['result'].keys():
		return 'No new articles'

	else:
		# iterate through each article array, store title and link in an array for each article
		for i in range(len(myjson)):
			# DEBUGGING LIKE A G
			# print '%s' % myjson['result']['docs'] [0] ['source']['enriched']['url']
			# print '%s' % myjson['result']['docs'] [1] ['source']['enriched']['url']
			# print '%s' % myjson['result']['docs'] [2] ['source']['enriched']['url']
			# print '%s' % myjson['result']['docs'] [3] ['source']['enriched']['url']
			# print '%s' % myjson['result']['docs'] [4] ['source']['enriched']['url']
			# print '\n\n%s' % myjson['result']['docs'] [i] ['source']['enriched']['url']
			print articleset.append(myjson['result']['docs'] [i] ['source']['enriched']['url'])
			return articleset.append(myjson['result']['docs'] [i] ['source']['enriched']['url'])

		# DEBUGGING LIKE A G
		# print '\n\n\nARTICLE 0:'
		# print myjson['result']['docs'] [0] ['source']['enriched']['url']
		# print '\nARTICLE 1:'
		# print myjson['result']['docs'] [1] ['source']['enriched']['url']
		# print '\nARTICLE 2:'
		# print myjson['result']['docs'] [2] ['source']['enriched']['url']
		# print '\nARTICLE 3:'
		# print myjson['result']['docs'] [3] ['source']['enriched']['url']
		# print '\nARTICLE 4:'
		# print myjson['result']['docs'] [4] ['source']['enriched']['url']

	#print articleset
	#return aritcleset


if test:
	getArticles('Patriots')