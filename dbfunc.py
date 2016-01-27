import sqlite3

from heapq import nlargest

import urllib

# returns 0 if empty query, 1 if query returned stuff
def cursorlen(cursor):
	for item in cursor:
		return 1
	return 0

def create_tables(cursor):
	#print "ABOUT TO CREATE A TABLE!"
	# create table entries (id integer primary key autoincrement, data)
	cursor.execute('''CREATE TABLE ENTITIES
	       (ENTITYID INTEGER  PRIMARY KEY autoincrement,
	       NAME TEXT NOT NULL,
	       CUSTOMDATA TEXT,
	       UNIQUE(NAME))''')

	# This table stores the tags. Each entityid may appear more than once,
	# and each tag may appear more than once, but no pair may appear
	# more than once!
	cursor.execute('''CREATE TABLE TAGS
	       (ENTITYID INTEGER  NOT NULL,
	       TAG TEXT NOT NULL,
	       SCORE REAL)''')

	cursor.execute('''CREATE TABLE SUMMARIES
	       (ENTITYID INTEGER NOT NULL,
	       SENTENCE TEXT NOT NULL)''')

	cursor.execute('''CREATE TABLE MENTIONEDWITH
	       (ENTITYID1 INTEGER NOT NULL,
	       ENTITYID2 INTEGER NOT NULL,
	       COUNT INTEGER NOT NULL)''')
		   # eventually, change to this:
		   #COUNT INTEGER NOT NULL, UNIQUE(ENTITYID1, ENTITYID2))''')
	
	cursor.execute('''CREATE TABLE LOCATIONS
	       (ENTITYID INTEGER  NOT NULL,
	       LOCATION TEXT NOT NULL)''')

def get_entity_name_by_id(cursor, entity_id):
	cursor.execute("SELECT NAME FROM ENTITIES WHERE ENTITYID=? ", (entity_id,))
	name_result= cursor.fetchall()
	assert(len(name_result) == 1)
	return name_result[0][0]

def get_entity_id_by_name(cursor, entity_name):
	cursor.execute("SELECT ENTITYID FROM ENTITIES WHERE NAME=? ", (entity_name.replace("'", "").lower(),))
	id_result = cursor.fetchall()
	assert(len(id_result) == 1)
	return id_result[0][0]

def delete_entity_by_id(cursor, num):
	cursor.execute("DELETE FROM ENTITIES WHERE ENTITYID=?",(num,))
	cursor.execute("DELETE FROM LOCATIONS WHERE ENTITYID=?",(num,))
	cursor.execute("DELETE FROM MENTIONEDWITH WHERE ENTITYID1=?",(num,))
	cursor.execute("DELETE FROM MENTIONEDWITH WHERE ENTITYID2=?",(num,))
	cursor.execute("DELETE FROM SUMMARIES WHERE ENTITYID=?",(num,))
	cursor.execute("DELETE FROM TAGS WHERE ENTITYID=?",(num,))
	return

# returns entity id.
# if name exists, return id.
# if name doesnt exist, create new and return id.
def insert_entity_by_name(cursor, entity_name):
	cursor.execute("INSERT OR IGNORE INTO ENTITIES(NAME, CUSTOMDATA) VALUES (?, ?)", (entity_name.lower(), ""))
	entity_id = cursor.lastrowid
	# if user already exists:
	if entity_id == 0:
		cursor.execute("SELECT ENTITYID FROM ENTITIES WHERE NAME=?", (entity_name.lower(),))
		res = cursor.fetchall()
		return res[0][0]
	return entity_id

# returns old top tags and deletes them from the database
def get_delete_tags_by_id(cursor, entity_id):
	cursor.execute("SELECT TAG, SCORE FROM TAGS WHERE ENTITYID=? ", (entity_id,))
	current_keywords = cursor.fetchall()
	cursor.execute("DELETE FROM TAGS WHERE ENTITYID=? ", (entity_id,))
	return current_keywords

# gets top keywords from a list of (tag, score) tuples.
def top_tags(all_tags, max_tags):
	return sorted(all_tags, key=(lambda s: -s[1]))[:max_tags]


def get_delete_mentions_by_id(cursor, entity_id):
	cursor.execute("SELECT * FROM MENTIONEDWITH WHERE ENTITYID1=? OR ENTITYID2=?", (entity_id, entity_id))
	current_mentions = cursor.fetchall()
	cursor.execute("DELETE FROM MENTIONEDWITH WHERE ENTITYID1=? OR ENTITYID2=?", (entity_id, entity_id))
	return current_mentions

def get_entities_mentioned_by_id(cursor, entity_id):
	cursor.execute("SELECT * FROM MENTIONEDWITH WHERE ENTITYID1=? OR ENTITYID2=? ORDER BY COUNT DESC", (str(entity_id[0]), str(entity_id[0])))
	current_mentions = cursor.fetchall()
	names = []
	for mention in current_mentions:
		if mention[0] == entity_id:
			names.append(get_entity_name_by_id(cursor, mention[1]))
		# if mention[1] == entity_id
		else:
			names.append(get_entity_name_by_id(cursor, mention[0]))
	return names

def top_mentions(all_mentions, max_mentions):
	return sorted(all_mentions , key=(lambda s: -s[2]))[:max_mentions]

# insert or update. Return count
def insert_mentions_by_ids(cursor, id1, id2):
	assert(id1 != id2)
	dbq = "INSERT OR IGNORE INTO MENTIONEDWITH(ENTITYID1, ENTITYID2, COUNT) VALUES (?, ?, 1)"
	if id1 < id2:
		cursor.execute(dbq, (id1, id2))
		some_id = cursor.lastrowid
		if some_id == 0:
			cursor.execute("UPDATE MENTIONEDWITH SET COUNT = COUNT + 1 WHERE ENTITYID1=? AND ENTITYID2=?", (id1, id2))
		cursor.execute("SELECT COUNT FROM MENTIONEDWITH WHERE ENTITYID1=? AND ENTITYID2=?", (id1, id2))
		return cursor.fetchall()[0][0]
	else:
		cursor.execute(dbq, (id2, id1))
		some_id = cursor.lastrowid
		if some_id == 0:
			cursor.execute("UPDATE MENTIONEDWITH SET COUNT = COUNT + 1 WHERE ENTITYID1=? AND ENTITYID2=?", (id2, id1))
		cursor.execute("SELECT COUNT FROM MENTIONEDWITH WHERE ENTITYID1=? AND ENTITYID2=?", (id2, id1))
		return cursor.fetchall()[0][0]

def write_new_mentions(cursor, mentions_list):
	cursor.executemany("INSERT INTO MENTIONEDWITH VALUES (?, ?, ?)", mentions_list)

def get_ids_from_query(cursor, q):
	try:
		cursor.execute("SELECT ENTITYID FROM TAGS WHERE TAG LIKE '%" + q + "%' LIMIT 100")
	except sqlite3.OperationalError:
		# there's no tables made yet.
		return 0
	tag_result = cursor.fetchall()
	tag_entities = []
	for tag_id in tag_result:
		cursor.execute("SELECT * FROM LOCATIONS WHERE ENTITYID=?", tag_id)
		tag_entities.append(cursor.fetchall())

	# Return search results by order: NAME, SUMMARY, TAG
	cursor.execute("SELECT ENTITYID FROM ENTITIES WHERE NAME LIKE '%" + q + "%' LIMIT 5")
	name_result = cursor.fetchall()
	cursor.execute("SELECT ENTITYID FROM TAGS WHERE TAG LIKE '%" + q + "%' LIMIT 5")
	tag_result = cursor.fetchall()
	cursor.execute("SELECT ENTITYID FROM SUMMARIES WHERE SENTENCE LIKE '%" + q + "%' LIMIT 5")
	summary_result = cursor.fetchall()
	cursor.execute("SELECT ENTITYID FROM LOCATIONS WHERE LOCATION LIKE '%" + q + "%' LIMIT 5")
	filename_result = cursor.fetchall()

	entity_result = []
	counter = 0
	unique_output_ids = []
	for item in name_result + tag_result + summary_result + filename_result:
		if item not in unique_output_ids:
			unique_output_ids.append(item)
	return unique_output_ids

def dbcustomdata(entity_id, custom_data, dbpath):
	#print "CUSTOM_DATA:"
	#print custom_data
	conn = sqlite3.connect(dbpath)
	c = conn.cursor()
	c.execute("UPDATE ENTITIES SET CUSTOMDATA = (?) WHERE ENTITYID= (?)", (custom_data, entity_id))
	conn.commit()
	conn.close()
	return 0

def trymakeusertable(dbpath):
	conn = sqlite3.connect(dbpath)
	c = conn.cursor()
	val = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='USERS'")
	if cursorlen(val.fetchall()):
		return
	c.execute('''CREATE TABLE USERS
       (USERID INTEGER PRIMARY KEY autoincrement,
       USERNAME TEXT NOT NULL,
       HASHEDPASSWORD TEXT NOT NULL)''')
	return


def dbinsert(entity_dict, max_tags, max_mentions, dbpath):
	# hpdict
	# {'Name': [['summary'], [('key', 2.4), ('words', 1.3)], ['location'], [other1, other2]]}
	print "ENTITY_DICT TO INSERT:"
	print entity_dict
	conn = sqlite3.connect(dbpath)
	c = conn.cursor()

	val = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ENTITIES'")
	l = cursorlen(val.fetchall())
	if l == 0:
		create_tables(c)
		conn.commit()
	names_ids_tags_mentions = []
	ids = []
	for entity_name in entity_dict.keys():
		#0 index = summaries, 1st index = keys, 2nd index = links
		sum_key_loc = entity_dict[entity_name]
		name_no_apostrophes = entity_name.replace("'", "")
		summary_no_apostrophes = [i.replace("'", "") for i in sum_key_loc[0]]
		entity_id = insert_entity_by_name(c, entity_name)
		ids.append(entity_id)
		conn.commit()
	for entity_id in ids:
		entity_name = get_entity_name_by_id(c, entity_id)
		for location in sum_key_loc[2]:
			c.execute("SELECT EXISTS(SELECT LOCATION FROM LOCATIONS WHERE ENTITYID=(?))", (entity_id,))
			if not c.fetchone()[0]:
				c.execute("INSERT INTO LOCATIONS(ENTITYID, LOCATION) VALUES (?, ?)", (entity_id, location))

		for sentence in sum_key_loc[0]:
			c.execute("SELECT EXISTS(SELECT SENTENCE FROM SUMMARIES WHERE SENTENCE=(?))", (sentence,))
			if not c.fetchone()[0]:
				c.execute("INSERT INTO SUMMARIES(ENTITYID, SENTENCE) VALUES (?, ?)", (entity_id, sentence))

		# Tag stuff.
		old_tags = get_delete_tags_by_id(c, entity_id)
		conn.commit()
		tag_list = [(entity_id, tag_tup[0], tag_tup[1]) for tag_tup in top_tags(old_tags + sum_key_loc[1], max_tags)]
		c.executemany("INSERT INTO TAGS(ENTITYID, TAG, SCORE) VALUES (?, ?, ?)", tag_list)
		conn.commit()

		# MentionedWith stuff.

		# UPDATE MENTIONEDWITH SET COUNT = COUNT + 1 WHERE ENTITYID1 = 1
		# entity_objects.append(result[0])
		# list of mentioned names.
		old_mentions = get_delete_mentions_by_id(c, entity_id)
		new_mention_ids = []
		for mention in sum_key_loc[3]:
			mentioned_id = get_entity_id_by_name(c, mention)
			conn.commit()
			new_mention_ids.append(mentioned_id)
		new_mentions = []
		print "OLD MENTIONS"
		print old_mentions

		for old_mention in old_mentions:
			if old_mention[0] == entity_id:
				if old_mention[1] in new_mention_ids:
					new_mentions.append((old_mention[0], old_mention[1], old_mention[2] + 1))
					new_mention_ids.remove(old_mention[1])
			# old_mention[1] == entity_id
			else:
				if old_mention[0] in new_mention_ids:
					new_mentions.append((old_mention[0], old_mention[1], old_mention[2] + 1))
					new_mention_ids.remove(old_mention[0])
		mention_names = []
		for new_id in new_mention_ids:
			# In the future, this should not be commented out
			# assert(new_id != entity_id)
			mention_names.append(get_entity_name_by_id(c, new_id))
			if new_id < entity_id:
				new_mentions.append((new_id, entity_id, 1))
			else:
				new_mentions.append((entity_id, new_id, 1))
		print "NEW MENTIONS BEFORE"
		print new_mentions
		print max_mentions
		new_mentions = top_mentions(new_mentions, max_mentions)
		write_new_mentions(c, new_mentions)
		conn.commit()
		print "NEW MENTIONS"
		print new_mentions
		names_ids_tags_mentions.append((entity_name, entity_id, tag_list, mention_names))
	# entity_objects = []
	# for entity_name in entity_dict.keys():
	# 	c.execute("SELECT ENTITYID FROM ENTITIES WHERE NAME=?", (entity_name,))
	# 	result = c.fetchall()
	# 	assert(len(result) == 1)
	conn.commit()
	conn.close()
	return names_ids_tags_mentions


def dbquery(query, dbpath):
	q = urllib.unquote(query).encode('utf8')
	conn = sqlite3.connect(dbpath)
	wordlist = set(q.split(" "))
	entity_result = []
	with conn:
		c = conn.cursor()
		# If we can get Fulltext extension: http://dev.mysql.com/doc/refman/5.0/en/fulltext-natural-language.html
		
		#c.execute(''' SELECT a.* from (SELECT *, 1 as rank FROM ENTITIES WHERE NAME LIKE '%:q%' UNION SELECT *, 2 as rank FROM ENTITIES WHERE TAGS LIKE '%:q%') a order by a.rank asc;''', {"q": query})

		unique_output_ids = get_ids_from_query(c, query)
		if not unique_output_ids:
			return 0
		for final_id in unique_output_ids:
			# Get name:
			c.execute("SELECT NAME, CUSTOMDATA FROM ENTITIES WHERE ENTITYID=?", final_id)
			name, custom_data = c.fetchall()[0]
			c.execute("SELECT SENTENCE FROM SUMMARIES WHERE ENTITYID=?", final_id)

			summary_chars = [i[0] for i in c.fetchall()]
			# for some reason this is a list of every character in a string....
			total = ""
			for char in summary_chars:
				total = total + char
			summary_list = [total]
			c.execute("SELECT * FROM TAGS WHERE ENTITYID=?", final_id)
			tag_list = c.fetchall()
			c.execute("SELECT LOCATION FROM LOCATIONS WHERE ENTITYID=?", final_id)
			location_list = [i[0] for i in c.fetchall()]
			print "final_id:"
			print final_id
			names = get_entities_mentioned_by_id(c, final_id)
			print "names"
			print names
			entity_result.append([final_id[0], name, summary_list, tag_list, location_list, names, custom_data])

	#conn.commit()
	conn.close()
	# [[72, 'NAME', ['summary'], [('key', 6.9)], ['location.txt'], ['related_1', 'related_2'], "CustomDataString"], ...]
	print "ENTITY_RESULT"
	print entity_result
	return entity_result



