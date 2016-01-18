import sqlite3

from heapq import nlargest

import urllib

MAX_KEYS_PER_ENTITY = 20

# returns 0 if empty query, 1 if query returned stuff
def cursorlen(cursor):
	for item in cursor:
		return 1
	return 0

def dbinsert(entity_dict):
	# hpdict
	# {'Name': [['summary'], [('key', 2.4), ('words', 1.3)], ['location']]}

	conn = sqlite3.connect("ASG.db")
	c = conn.cursor()

	val = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='LOCATIONS'")
	l = cursorlen(val.fetchall())
	if l == 0:
		print "ABOUT TO CREATE A TABLE!"
		# This table stores the tags. Each name may appear more than once,
		# and each tag may appear more than once, but no pair may appear
		# more than once!
		c.execute('''CREATE TABLE TAGS
		       (NAME TEXT  NOT NULL,
		       TAG TEXT NOT NULL,
		       SCORE REAL)''')


		c.execute('''CREATE TABLE SUMMARIES
		       (NAME TEXT  NOT NULL,
		       SENTENCE TEXT NOT NULL)''')
		

		c.execute('''CREATE TABLE LOCATIONS
		       (NAME TEXT  NOT NULL,
		       LOCATION TEXT NOT NULL)''')

	for entity_name in entity_dict.keys():
		#0 index = name, 1st index = description, 2nd index = link
		sum_key_loc = entity_dict[entity_name]
		name_no_apostrophes = entity_name.replace("'", "")
		summary_no_apostrophes = [i.replace("'", "") for i in sum_key_loc[0]]
		c.execute("SELECT * FROM LOCATIONS WHERE NAME='" + name_no_apostrophes + "' ")
		# Ensure that entry with that name doesn't already exist
		if not c.fetchall():
			for location in sum_key_loc[2]:
				c.execute("INSERT INTO LOCATIONS(NAME, LOCATION) VALUES (?, ?)", (name_no_apostrophes, location))
		for sentence in sum_ley_loc[0]:
			c.execute("INSERT INTO SUMMARIES(NAME, SENTENCE) VALUES (?, ?)", (name_no_apostrophes, sentence))

		# Now deal with tags.
		c.execute("SELECT TAG, SCORE FROM TAGS WHERE NAME=? ", (name_no_apostrophes,))
		current_keywords = c.fetchall()
		c.execute("DELETE FROM TAGS WHERE NAME=? ", (name_no_apostrophes,))
		current_keywords_dict = {}
		# initialize dict to what is in db
		print "current_keywords:"
		print current_keywords
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
			c.execute("INSERT INTO TAGS(NAME, TAG, SCORE) VALUES (?, ?, ?)", (name_no_apostrophes, key, current_keywords_dict[key]))

	conn.commit()
	conn.close()


def dbquery(query):
	q = urllib.unquote(query).decode('utf8') 
	print "QUERY:"
	print query
	print type(query)
	conn = sqlite3.connect("ASG.db")
	wordlist = set(q.split(" "))
	entity_result = {}
	with conn:
		c = conn.cursor()
		# If we can get Fulltext extension: http://dev.mysql.com/doc/refman/5.0/en/fulltext-natural-language.html
		
		#c.execute(''' SELECT a.* from (SELECT *, 1 as rank FROM ENTITIES WHERE NAME LIKE '%:q%' UNION SELECT *, 2 as rank FROM ENTITIES WHERE TAGS LIKE '%:q%') a order by a.rank asc;''', {"q": query})
		try:
			c.execute("SELECT NAME FROM TAGS WHERE TAG LIKE '%" + q + "%' LIMIT 100")
		except sqlite3.OperationalError:
			return 0
		tag_result = c.fetchall()
		tag_entities = []
		for name in tag_result:
			c.execute("SELECT * FROM LOCATIONS WHERE NAME=?", name)
			tag_entities.append(c.fetchall())
		# Return search results by order: NAME, SUMMARY, TAG
		c.execute("SELECT NAME FROM LOCATIONS WHERE NAME LIKE '%" + q + "%' LIMIT 5")
		name_result = c.fetchall()
		c.execute("SELECT NAME FROM TAGS WHERE TAG LIKE '%" + q + "%' LIMIT 5")
		tag_result = c.fetchall()
		c.execute("SELECT NAME FROM SUMMARIES WHERE SENTENCE LIKE '%" + q + "%' LIMIT 5")
		summary_result = c.fetchall()
		c.execute("SELECT NAME FROM LOCATIONS WHERE LOCATION LIKE '%" + q + "%' LIMIT 5")
		filename_result = c.fetchall()

		entity_result = {}
		counter = 0
		unique_output_names = []
		for item in name_result + tag_result + summary_result + filename_result:
			if item not in unique_output_names:
				unique_output_names.append(item)
		for name in unique_output_names:
			print "NAME"
			print name
			c.execute("SELECT SENTENCE FROM SUMMARIES WHERE NAME=?", name)

			summary_chars = [i[0] for i in c.fetchall()]
			# for some reason this is a list of every character in a string....
			total = ""
			for char in summary_chars:
				total = total + char
			summary_list = [total]
			c.execute("SELECT TAG, SCORE FROM TAGS WHERE NAME=?", name)
			tag_list = c.fetchall()
			c.execute("SELECT LOCATION FROM LOCATIONS WHERE NAME=?", name)
			location_list = [i[0] for i in c.fetchall()]

			entity_result[name[0]] = [summary_list, tag_list, location_list]
			counter = counter + 1

	#conn.commit()
	conn.close()
	# {'Name': [['summary1', 'summary2'], [('key', 2.4), ('words', 1.3)], ['location', 'location2']]}
	return entity_result
