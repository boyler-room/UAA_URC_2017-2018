info=\
""""Additional API Types and Functions"

description:
	functions and types used by the API and additional useful types and functions

usage:
	lock: simplistic lock class for managing concurrent access
	stack: simplistic concurrency-safe stack class for shared stacks
	queue: simplistic concurrency-safe queue class for shared queues
	dispatchError: exception type used by the API, calls to dispatch should catch this error
	parsecmd(cmd): splits and tokenizes dest-cmd strings, returns (dest,cmd) tuple
	unparsecmd(cmd): concatenate command tokens into string

""""Chandra Boyle"

class lock:
	def __init__(self,block=True):
		self.blocking=block
		self.locked=False
	def acquire(self):
		if self.blocking:
			while self.locked: pass
			self.locked=True
		elif self.locked: return False
		else: self.locked=True
	def release(self):
		self.locked=False

class stack:
	def __init__(self):
		self.q=[]
		self.lock=lock()
	def clear(self):
		self.q=[]
	def push(self,item):
		self.lock.acquire()
		if item!=None: self.q.append(item)
		self.lock.release()
	def pop(self):
		item=None
		self.lock.acquire()
		if len(self.q)>0:
			item=self.q[-1]
			del self.q[-1]
		self.lock.release()
		return item
	def peek(self):
		item=None
		self.lock.acquire()
		if len(self.q)>0:
			item=self.q[-1]
		self.lock.release()
		return item

class queue:
	def __init__(self):
		self.q=[]
		self.lock=lock()
	def clear(self):
		self.q=[]
	def push(self,item):
		self.lock.acquire()
		if item!=None: self.q.append(item)
		self.lock.release()
	def pop(self):
		item=None
		self.lock.acquire()
		if len(self.q)>0:
			item=self.q[0]
			del self.q[0]
		self.lock.release()
		return item
	def peek(self):
		item=None
		self.lock.acquire()
		if len(self.q)>0:
			item=self.q[0]
		self.lock.release()
		return item

class dispatchError:#dispatch error codes
	def __init__(self, msg, code=0xFF):
		if type(msg)==str: self.msg=msg
		elif isinstance(msg,dispatchError):
			self.msg=msg.msg
			self.code=msg.code
		else: self.msg=None
		if type(code)==int: self.code=code
	def __repr__(self):
		return 'Error %s: "%s"'%(hex(self.code),self.msg)
	def __str__(self):
		return self.msg

def unparsecmd(dest,cmd):
	scmd=dest
	for c in cmd:
		if type(c)==str and ' ' in c: scmd+=' "%s"'%c
		else: scmd+=' %s'%c
	return scmd

def parsecmd(cmd):
	tlist=[]
	dest=''
	token=''
	inq=False
	isq=False
	for c in cmd:
		if c=='"':
			inq=not inq
			if not inq: isq=True
		elif c==' ' and token!='' and not inq:
			if not isq:
				for i in token:
					if i not in '0123456789': break
				else: token=int(token)
			isq=False
			tlist.append(token)
			token=''
		else: token+=c
	if token!='': tlist.append(token)
	if len(tlist)>0:
		dest=tlist[0]
		del tlist[0]
	return (dest,tlist)
