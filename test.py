with open('test.txt', 'r') as f:
	x = set(f.read().lower().split('\n'))

#for i in xrange(len(x)):
	#x[i] = x[i].strip('\n')
print type(x)
print x