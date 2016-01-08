import sqlite3

def dbinsert(dict):

	conn = sqlite3.connect("ASG.db")

	print "Opened Successfully"

	try:
		conn.execute('''CREATE TABLE ENTITIES
		       (NAME TEXT PRIMARY KEY     NOT NULL,
		        TAGS          TEXT,
		       LINKS         TEXT);''')
	except sqlite3.OperationalError:
		pass

	for entities in dict.values():
		#0 index = name, 1st index = description, 2nd index = link
		conn.execute("INSERT INTO ENTITIES(NAME) \
	      VALUES ("+entities[0][0]+")");

	conn.close()


def dbquery(q):
	conn = sqlite3.connect("ASG.db")


	result = '''  '''
	conn.close()
	return result