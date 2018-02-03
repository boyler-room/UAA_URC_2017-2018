import sys

def ccat(l):
	if type(l)!=list: return None
	stl=''
	for i in l:
		stl+='%s '%i
	stl=stl.strip()
	return stl

if len(sys.argv)>1:
	print 'begin'
	print '\t%s'%ccat(sys.argv[1:])
	try:
		while True: pass
	except: print 'end'