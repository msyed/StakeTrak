import sqlite3

# returns 0 if empty query, 1 if query returned stuff
def cursorlen(cursor):
	c = 0
	for item in cursor:
		return 1
	return c

def dbinsert(hpdict):
	print "hpdict:"
	print hpdict

	conn = sqlite3.connect("ASG.db")
	c = conn.cursor()

	print "Opened Successfully"

	val = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ENTITIES'")
	print "cursorlen:"
	l = cursorlen(val)
	print l
	print type(l)
	print (l == 0)
	if l == 0:
		print "ABOUT TO CREATE A TABLE!"
		c.execute('''CREATE TABLE ENTITIES
		       (NAME TEXT PRIMARY KEY     NOT NULL,
		        TAGS          TEXT,
		       LINKS         TEXT
		       )''')

	for entity in hpdict.values():
		#0 index = name, 1st index = description, 2nd index = link
		name_no_apostrophes = entity[0][0].replace("'", "")
		desc_no_apostrophes = entity[0][1].replace("'", "")
		get_entity = c.execute("SELECT * FROM ENTITIES WHERE NAME='" + entity[0][0] + "' ")
		# Ensure that entry with that name doesn't already exist
		if cursorlen(get_entity) == 0:
			c.execute("INSERT INTO ENTITIES(NAME, TAGS, LINKS) VALUES (?, ?, ?)", (name_no_apostrophes, desc_no_apostrophes, entity[0][2]))

	conn.commit()
	conn.close()


def dbquery(query):
	print "QUERY:"
	print query
	print type(query)
	conn = sqlite3.connect("ASG.db")
	wordlist = set(query.split(" "))
	d = {}
	with conn:
		c = conn.cursor()
		# If we can get Fulltext extension: http://dev.mysql.com/doc/refman/5.0/en/fulltext-natural-language.html
		
		#c.execute(''' SELECT a.* from (SELECT *, 1 as rank FROM ENTITIES WHERE NAME LIKE '%:q%' UNION SELECT *, 2 as rank FROM ENTITIES WHERE TAGS LIKE '%:q%') a order by a.rank asc;''', {"q": query})

		c.execute("SELECT * FROM ENTITIES WHERE NAME LIKE '%" + query + "%' OR TAGS LIKE '%" + query + "%' OR LINKS LIKE '%" + query + "%' LIMIT 100")
		result = c.fetchall()
		if not result:
			return 0
		print "RESULT"
		print result
		c = 0
		for entity in result:
			d[c] = [[i for i in entity]]
			c = c + 1

	#conn.commit()
	conn.close()
	return d
