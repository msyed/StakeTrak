#import wikipedia libraries and API
import json
import wikipedia
from havenondemand.hodindex import HODClient
import os
import requests


#define function
def wikipediagrabber(filepath):  

	#make API call, as outlined in https://github.com/HPE-Haven-OnDemand/havenondemand-python
	#client = HODClient("5796fa6f-a9a7-4186-b53d-ab435c9c53ad")
	#r = client.post('extractentities', data={'entity_type': ['people_eng'], 'unique_entities': 'true'},files={'file':open(filepath,'rb')}   )

	#set variables
	#myjson = r.json()
	#identifiers = []
	dictionary={3:["Barack Obama","Barack obama is a real nigga", "wikipedia.com", "paris.txt"]}
	filename = filepath.replace("test_files/","")
	#iterate through each named entity
	# for i in range(0, len(myjson['entities'])):
		
	# 	#try statement that only stores named entries with wikipedia descriptions in dictionary
	# 	try:
	# 		#record duplicate named entities 
	# 		identifier = myjson['entities'][i]['additional_information']['wikidata_id']

	# 		#only add to dictionary if named entity has not already appeared 
	# 		if identifier not in identifiers:
	# 			identifiers.append(identifier)
	# 			entry = myjson['entities'][i]['original_text']
	# 			dictionary[myjson['entities'][i]['additional_information']['wikidata_id']] = [entry, wikipedia.summary(entry, sentences = 5), myjson['entities'][i]['additional_information']['wikipedia_eng'],filename]
 		
 # 		#do not add to dictionary if they do not have wikipedia pages		
		#except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError) as e:
		#	continue

	return dictionary

#function creates dictionary for each file and merges them
def gatherer():

	#create list that will include dictionaries from each file
	dicts = []

	#get file names from folder of files
	filenames = os.listdir('test_files/') 
	
	#remove hidden files
	for i in filenames:
		if i[0] == '.':
			filenames.remove(i)

	upload_size = 0
	#iterate through each file and run wikigrabber function	
	for info in filenames:
		upload_size = upload_size + os.path.getsize('test_files/' + info)
		dicts.append(wikipediagrabber('test_files/' + info))	

	# approximate hp backend time is 160,000 bytes/sec
	# upload_seconds = int(upload_size/160000)
	# upload_time = ""
	# if upload_seconds > 120:
	# 	upload_time = "upload time is approximately " + str(int(upload_seconds / 60)) + " minutes."
	# else:
	# 	upload_time = "upload time is approximately " + str(upload_seconds) + " seconds."
	#merge separate dictionaries, adapted from http://stackoverflow.com/questions/9415785/merging-several-python-dictionaries	
	super_dict = {}
	for entry in dicts:
		for k, v in entry.iteritems():
			super_dict.setdefault(k, []).append(v)
	return super_dict