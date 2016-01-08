import sqlite3



def dbinsert(hpdict):
	print "hpdict:"
	print hpdict

	conn = sqlite3.connect("ASG.db")
	c = conn.cursor()

	print "Opened Successfully"

	try:
		c.execute('''CREATE TABLE ENTITIES
		       (NAME TEXT PRIMARY KEY     NOT NULL,
		        TAGS          TEXT,
		       LINKS         TEXT);''')
	except sqlite3.OperationalError:
		pass

	for entity in hpdict.values():
		#0 index = name, 1st index = description, 2nd index = link
		name_no_apostrophes = entity[0][0].replace("'", "")
		desc_no_apostrophes = entity[0][1].replace("'", "")
		c.execute("INSERT INTO ENTITIES(NAME, TAGS, LINKS) VALUES ('" + name_no_apostrophes + "', '" + desc_no_apostrophes + "', '" + entity[0][2] + "')")

	conn.commit()
	conn.close()


def dbquery(q):
	conn = sqlite3.connect("ASG.db")
	c = conn.cursor()

	entity = [o for o in c.execute("SELECT * FROM ENTITIES WHERE NAME='Barack Obama'")][0]

	conn.close()
	return entity
