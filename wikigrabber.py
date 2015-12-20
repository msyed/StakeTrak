#import wikipedia libraries and API
import json
import wikipedia
from havenondemand.hodindex import HODClient
import os

#define function
def wikipediagrabber(filepath):  

	#make API call, as outlined in https://github.com/HPE-Haven-OnDemand/havenondemand-python
	client = HODClient("http://api.havenondemand.com/", "5e8a3841-5bec-43cc-9dac-5e5d0a90bbc9")
	r = client.post('extractentities', data={'entity_type': ['people_eng'], 'unique_entities': 'true'},files={'file':open(filepath,'rb')}   )

	#set variables
	myjson = r.json()
	identifiers = []
	dictionary={}
	
	#iterate through each named entity
	for i in range(0, len(myjson['entities'])):
		
		#try statement that only stores named entries with wikipedia descriptions in dictionary
		try:
			#record duplicate named entities 
			identifier = myjson['entities'][i]['additional_information']['wikidata_id']

			#only add to dictionary if named entity has not already appeared 
			if identifier not in identifiers:
				identifiers.append(identifier)
				entry = myjson['entities'][i]['original_text']
				dictionary[myjson['entities'][i]['additional_information']['wikidata_id']] = [myjson['entities'][i]['original_text'], wikipedia.summary(entry, sentences = 5), myjson['entities'][i]['additional_information']['wikipedia_eng']]
 		
 		#do not add to dictionary if they do not have wikipedia pages		
		except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError) as e:
			continue

	return dictionary

#function creates dictionary for each file and merges them
def gatherer():

	#create list that will include dictionaries from each file
	dicts = []

	#get file names from folder of files
	filenames = os.listdir('files/') 
	
	#remove hidden files
	for i in filenames:
		if i[0] == '.':
			filenames.remove(i)

	#iterate through each file and run wikigrabber function	
	for info in filenames:
		dicts.append(wikipediagrabber('files/' + info))	

	#merge separate dictionaries, adapted from http://stackoverflow.com/questions/9415785/merging-several-python-dictionaries	
	super_dict = {}
	for entry in dicts:
		for k, v in entry.iteritems():
			super_dict.setdefault(k, []).append(v)
	return super_dict