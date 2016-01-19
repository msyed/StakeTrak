import sqlite3

from heapq import nlargest

import urllib

MAX_KEYS_PER_ENTITY = 20

# returns 0 if empty query, 1 if query returned stuff
def cursorlen(cursor):
	for item in cursor:
		return 1
	return 0

def get_entity_name_by_id(cursor, entity_id):
	cursor.execute("SELECT NAME FROM ENTITIES WHERE ENTITYID=? ", (entity_id,))
	name_result= c.fetchall()
	assert(len(name_result) == 1)
	return name_result[0][0]

def get_entity_id_by_name(cursor, entity_name):
	cursor.execute("SELECT ENTITYID FROM ENTITIES WHERE NAME=? ", (entity_name.replace("'", ""),))
	id_result = c.fetchall()
	assert(len(name_result) == 1)
	return id_result[0][0]

def dbcustomdata(entity_id, custom_data):
	print "CUSTOM_DATA:"
	print custom_data
	conn = sqlite3.connect("ASG.db")
	c = conn.cursor()
	c.execute("UPDATE ENTITIES SET CUSTOMDATA = (?) WHERE ENTITYID= (?)", (custom_data, entity_id))
	conn.commit()
	conn.close()
	return 0

def trymakeusertable():
	conn = sqlite3.connect("ASG.db")
	c = conn.cursor()
	val = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='USERS'")
	if cursorlen(val.fetchall()):
		return
	c.execute('''CREATE TABLE USERS
       (USERID INTEGER PRIMARY KEY autoincrement,
       USERNAME TEXT NOT NULL,
       HASHEDPASSWORD TEXT NOT NULL)''')
	return

def dbinsert(entity_dict):
	# hpdict
	# {'Name': [['summary'], [('key', 2.4), ('words', 1.3)], ['location'], [other1, other2]]}

	conn = sqlite3.connect("ASG.db")
	c = conn.cursor()

	val = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ENTITIES'")
	l = cursorlen(val.fetchall())
	if l == 0:
		#print "ABOUT TO CREATE A TABLE!"

		# create table entries (id integer primary key autoincrement, data)
		c.execute('''CREATE TABLE ENTITIES
		       (ENTITYID INTEGER  PRIMARY KEY autoincrement,
		       NAME TEXT NOT NULL,
		       CUSTOMDATA TEXT )''')

		# This table stores the tags. Each entityid may appear more than once,
		# and each tag may appear more than once, but no pair may appear
		# more than once!
		c.execute('''CREATE TABLE TAGS
		       (ENTITYID INTEGER  NOT NULL,
		       TAG TEXT NOT NULL,
		       SCORE REAL)''')

		c.execute('''CREATE TABLE SUMMARIES
		       (ENTITYID INTEGER NOT NULL,
		       SENTENCE TEXT NOT NULL)''')
		
		c.execute('''CREATE TABLE LOCATIONS
		       (ENTITYID INTEGER  NOT NULL,
		       LOCATION TEXT NOT NULL)''')

		c.execute('''CREATE TABLE MENTIONEDWITH
		       (ENTITYID1 INTEGER NOT NULL,
		       ENTITYID2 INTEGER NOT NULL,
		       COUNT INTEGER NOT NULL)''')



	ids = []
	for entity_name in entity_dict.keys():
		#0 index = summaries, 1st index = keys, 2nd index = links
		sum_key_loc = entity_dict[entity_name]
		#print "ENTITY NAME"
		#print entity_name
		name_no_apostrophes = entity_name.replace("'", "")
		summary_no_apostrophes = [i.replace("'", "") for i in sum_key_loc[0]]
		c.execute("SELECT * FROM ENTITIES WHERE NAME='" + name_no_apostrophes + "' ")
		get_entity_result = c.fetchall()
		# Ensure that entry with that name doesn't already exist
		if not get_entity_result:
			c.execute("INSERT INTO ENTITIES(NAME) VALUES (?)", (name_no_apostrophes,))

		c.execute("SELECT ENTITYID FROM ENTITIES WHERE NAME=?", (name_no_apostrophes,))
		# check if more than one element, which would be a problem.
		entity_id = c.fetchall()[0][0]
		ids.append(entity_id)
		for location in sum_key_loc[2]:
			c.execute("INSERT INTO LOCATIONS(ENTITYID, LOCATION) VALUES (?, ?)", (entity_id, location))
		for sentence in sum_key_loc[0]:
			c.execute("INSERT INTO SUMMARIES(ENTITYID, SENTENCE) VALUES (?, ?)", (entity_id, sentence))

		# Now deal with tags.
		c.execute("SELECT TAG, SCORE FROM TAGS WHERE ENTITYID=? ", (entity_id,))
		current_keywords = c.fetchall()
		c.execute("DELETE FROM TAGS WHERE ENTITYID=? ", (entity_id,))
		current_keywords_dict = {}
		# initialize dict to what is in db
		#print "current_keywords:"
		#print current_keywords
		for (keyword, score) in current_keywords:
			# convert from unicode.
			current_keywords_dict[keyword] = score

		minimum_score = 0
		if current_keywords:
			minimum_score = min([i[1] for i in current_keywords])
		# now check if any values need to be updated
		for (keyword, score) in sum_key_loc[1]:
			# If the keyword is already in the database for that name,
			# check if the score is bigger, in which case add it to 
			# the dictionary that will eventually be input into the db.
			if keyword in current_keywords_dict.keys():
				if score > current_keywords_dict[keyword]:
					current_keywords_dict[keyword] = score
					# update minimum
					minimum_score = min([current_keywords_dict[k] for k in current_keywords_dict.keys()])
			else:
				# could do a score check here
				current_keywords_dict[keyword] = score
		k_keys_sorted_by_scores = nlargest(MAX_KEYS_PER_ENTITY, current_keywords_dict, key=current_keywords_dict.get)
		for key in k_keys_sorted_by_scores:
			c.execute("INSERT INTO TAGS(ENTITYID, TAG, SCORE) VALUES (?, ?, ?)", (entity_id, key, current_keywords_dict[key]))


	entity_objects = []
	for entity_name in entity_dict.keys():
		c.execute("SELECT ENTITYID FROM ENTITIES WHERE NAME=?", (entity_name,))
		result = c.fetchall()
		assert(len(result) == 1)
		entity_objects.append(result[0])
	for mentioned in sum_key_loc[3]:
		assert(not (mentioned == entity_name))
		if mentioned < entity_name:
			c.execute("SELECT * FROM MENTIONEDWITH WHERE ENTITYID1=?", (entity_id,))
		else:
			c.execute("SELECT * FROM MENTIONEDWITH WHERE ENTITYID2=?", (entity_id,))

	conn.commit()
	conn.close()
	return ids


def dbquery(query):
	q = urllib.unquote(query).decode('utf8') 
	#print "QUERY:"
	#print query
	#print type(query)
	conn = sqlite3.connect("ASG.db")
	wordlist = set(q.split(" "))
	entity_result = []
	with conn:
		c = conn.cursor()
		# If we can get Fulltext extension: http://dev.mysql.com/doc/refman/5.0/en/fulltext-natural-language.html
		
		#c.execute(''' SELECT a.* from (SELECT *, 1 as rank FROM ENTITIES WHERE NAME LIKE '%:q%' UNION SELECT *, 2 as rank FROM ENTITIES WHERE TAGS LIKE '%:q%') a order by a.rank asc;''', {"q": query})
		try:
			c.execute("SELECT ENTITYID FROM TAGS WHERE TAG LIKE '%" + q + "%' LIMIT 100")
		except sqlite3.OperationalError:
			# there's no tables made yet.
			return 0
		tag_result = c.fetchall()
		tag_entities = []
		for tag_id in tag_result:
			c.execute("SELECT * FROM LOCATIONS WHERE ENTITYID=?", tag_id)
			tag_entities.append(c.fetchall())

		# Return search results by order: NAME, SUMMARY, TAG
		c.execute("SELECT ENTITYID FROM ENTITIES WHERE NAME LIKE '%" + q + "%' LIMIT 5")
		name_result = c.fetchall()
		print "NAME RESULT"
		print name_result
		c.execute("SELECT ENTITYID FROM TAGS WHERE TAG LIKE '%" + q + "%' LIMIT 5")
		tag_result = c.fetchall()
		c.execute("SELECT ENTITYID FROM SUMMARIES WHERE SENTENCE LIKE '%" + q + "%' LIMIT 5")
		summary_result = c.fetchall()
		c.execute("SELECT ENTITYID FROM LOCATIONS WHERE LOCATION LIKE '%" + q + "%' LIMIT 5")
		filename_result = c.fetchall()

		entity_result = []
		counter = 0
		unique_output_ids = []
		for item in name_result + tag_result + summary_result + filename_result:
			if item not in unique_output_ids:
				unique_output_ids.append(item)
		for final_id in unique_output_ids:
			print "FINAL ID"
			print final_id
			# Get name:
			c.execute("SELECT NAME FROM ENTITIES WHERE ENTITYID=?", final_id)
			name = c.fetchall()[0][0]
			#print "ID"
			#print final_id
			c.execute("SELECT SENTENCE FROM SUMMARIES WHERE ENTITYID=?", final_id)

			summary_chars = [i[0] for i in c.fetchall()]
			# for some reason this is a list of every character in a string....
			total = ""
			for char in summary_chars:
				total = total + char
			summary_list = [total]
			c.execute("SELECT TAG, SCORE FROM TAGS WHERE ENTITYID=?", final_id)
			tag_list = c.fetchall()
			c.execute("SELECT LOCATION FROM LOCATIONS WHERE ENTITYID=?", final_id)
			location_list = [i[0] for i in c.fetchall()]

			entity_result.append([final_id[0], name, summary_list, tag_list, location_list])
			counter = counter + 1

	#conn.commit()
	conn.close()
	# [[72, 'name', ['summary1', 'summary2'], [('key', 2.4), ('words', 1.3)], ['location', 'location2']], ...]
	print "ENTITY_RESULT"
	print entity_result
	return entity_result



