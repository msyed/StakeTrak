import sqlite3

def cursorlen(cursor):
	c = 0
	for item in cursor:
		c = c + 1
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
		       LINKS         TEXT);''')

	for entity in hpdict.values():
		#0 index = name, 1st index = description, 2nd index = link
		name_no_apostrophes = entity[0][0].replace("'", "")
		desc_no_apostrophes = entity[0][1].replace("'", "")
		get_entity = c.execute("SELECT * FROM ENTITIES WHERE NAME='" + entity[0][0] + "' ")
		# Ensure that entry with that name doesn't already exist
		if cursorlen(get_entity) == 0:
			c.execute("INSERT INTO ENTITIES(NAME, TAGS, LINKS) VALUES ('" + name_no_apostrophes + "', '" + desc_no_apostrophes + "', '" + entity[0][2] + "')")

	conn.commit()
	conn.close()


def dbquery(query):
	conn = sqlite3.connect("ASG.db")
	wordlist = set(query.split(" "))
	rows = []
	with conn:
		c = conn.cursor()
		for word in wordlist:
			c.execute("SELECT * FROM ENTITIES WHERE NAME LIKE '%" + word + "%' OR TAGS LIKE '%" + word + "%' OR LINKS LIKE '%" + word + "%'")
			rows = rows + c.fetchall()
	return {0: rows}
