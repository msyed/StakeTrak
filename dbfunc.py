import sqlite3

from heapq import nlargest

import urllib

MAX_KEYS_PER_ENTITY = 20

# returns 0 if empty query, 1 if query returned stuff
def cursorlen(cursor):
	for item in cursor:
		return 1
	return 0

def dbinsert(hpdict):
	# hpdict
	# {0: ['Name', 'summary', [('key', 2.4), ('words', 1.3)], 'location']}

	conn = sqlite3.connect("ASG.db")
	c = conn.cursor()

	val = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ENTITIES'")
	l = cursorlen(val)
	if l == 0:
		print "ABOUT TO CREATE A TABLE!"
		# This table stores the entities.
		c.execute('''CREATE TABLE ENTITIES
		       (NAME TEXT PRIMARY KEY  NOT NULL,
		        SUMMARY         TEXT,
		       LOCATION 		 TEXT)''')

		# This table stores the tags. Each name may appear more than once,
		# and each tag may appear more than once, but no pair may appear
		# more than once!
		c.execute('''CREATE TABLE TAGS
		       (TAG TEXT   NOT NULL,
		        NAME  TEXT,
		        SCORE REAL)''')
		

	for entity in hpdict.values():
		#0 index = name, 1st index = description, 2nd index = link
		name_no_apostrophes = entity[0].replace("'", "")
		summary_no_apostrophes = entity[1].replace("'", "")
		c.execute("SELECT * FROM ENTITIES WHERE NAME='" + name_no_apostrophes + "' ")
		# Ensure that entry with that name doesn't already exist
		if not c.fetchall():
			c.execute("INSERT INTO ENTITIES(NAME, SUMMARY, LOCATION) VALUES (?, ?, ?)", (name_no_apostrophes, summary_no_apostrophes, entity[3]))
		
		print "ENTITY[0]:"
		print entity[0]
		c.execute("SELECT TAG, SCORE FROM TAGS WHERE NAME=? ", (entity[0],))
		current_keywords = c.fetchall()
		c.execute("DELETE FROM TAGS WHERE NAME=? ", (entity[0],))
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
		for (keyword, score) in entity[2]:
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
			c.execute("INSERT INTO TAGS(TAG, NAME, SCORE) VALUES (?, ?, ?)", (key, name_no_apostrophes, current_keywords_dict[key]))

	conn.commit()
	conn.close()


def dbquery(query):
	q = urllib.unquote(query).decode('utf8') 
	print "QUERY:"
	print query
	print type(query)
	conn = sqlite3.connect("ASG.db")
	wordlist = set(q.split(" "))
	d = {}
	with conn:
		c = conn.cursor()
		# If we can get Fulltext extension: http://dev.mysql.com/doc/refman/5.0/en/fulltext-natural-language.html
		
		#c.execute(''' SELECT a.* from (SELECT *, 1 as rank FROM ENTITIES WHERE NAME LIKE '%:q%' UNION SELECT *, 2 as rank FROM ENTITIES WHERE TAGS LIKE '%:q%') a order by a.rank asc;''', {"q": query})
		c.execute("SELECT NAME FROM TAGS WHERE TAG=? LIMIT 100", (q,))
		tag_result = c.fetchall()
		tag_entities = []
		for name in tag_result:
			c.execute("SELECT * FROM ENTITIES WHERE NAME=?", name)
			tag_entities.append(c.fetchall())
		c.execute("SELECT * FROM ENTITIES WHERE NAME LIKE '%" + q + "%' OR SUMMARY LIKE '%" + q + "%' OR LOCATION LIKE '%" + q + "%' LIMIT 100")
		name_result = c.fetchall()
		print "TAG_RESULT"
		print tag_result
		print "NAME_RESULT"
		print name_result
		print "TAG_ENTITIES"
		print tag_entities
		c = 0
		for entity_list in tag_entities:
			d[c] = [i for i in entity_list[0]]
			c = c + 1

		for entity in name_result:
			d[c] = [i for i in entity]
			c = c + 1

	#conn.commit()
	conn.close()
	return d
