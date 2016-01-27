# with open('test.txt', 'r') as f:
# 	x = set(f.read().lower().split('\n'))

# #for i in xrange(len(x)):
# 	#x[i] = x[i].strip('\n')
# print type(x)
# print x


# def insert(table, fields=(), values=()):
# 	# g.db is the database connection
# 	conn = sqlite3.connect("ASG.db")
# 	cur = conn.cursor()
# 	query = ('INSERT INTO %s (%s) VALUES (%s)' % (table, ', '.join(fields), ', '.join(['?'] * len(values))))
# 	cur.execute(query, values)
# 	conn.commit()
# 	id = cur.lastrowid
# 	cur.close()
# 	return id