x = open("test.txt", "r+")
lines = x.read().lower()
lines = lines.split()
print lines
y=""
for i in lines:
	if 'okay' == i:
		print "Sucess"
	else:
		print "shit"