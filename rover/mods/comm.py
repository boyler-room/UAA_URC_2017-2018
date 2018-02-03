info=\
""""TCP Communication Module"

description:
	command system access over tcp

usage:
	

""""Chandra Boyle"

#-------------------API Header--------------------
from base.types import dispatchError, queue, parsecmd
running=False
dispatch=None

#----------Module-Specific Functionality----------
from threading import Thread
import socket

address=('127.0.0.1',9990)
connected=False
inq=queue()
ouq=queue()

def iothread():
	global running,dispatch
	global inq,ouq,address,connected
	ssock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ssock.bind(address)
	ssock.setblocking(0)
	ssock.listen(1)
	while running:
		try: client=ssock.accept()
		except: continue
		connected=True
		dispatch('event',['fire','comm','client connected at %s'%(client[1][0])])
		client[0].setblocking(0)
		while connected:
			try: 
				data=client[0].recv(1024)
				data=data.strip().split('\n')
				for s in data: inq.push(s)
			except: pass

			try:
				while ouq.peek()!=None:
					client[0].sendall('%s\n'%ouq.pop())
			except: break

			cmd=inq.pop()
			if cmd==None: continue
			else: dest,cmd=parsecmd(cmd)
			try: reply=dispatch(dest,cmd)
			except dispatchError as e: ouq.push('Error: %s'%e)
			else:
				if reply!=None: ouq.push('%s'%reply)
		client[0].close()
		connected=False
		try: dispatch('event',['fire','comm','client disconnected'])
		except: pass
	ssock.close()

#----------------API Functionality----------------
def init():
	global dispatch

def start():
	global running
	running=True
	dispatch('event',['register'])
	iot=Thread(target=iothread)
	#iot.daemon=True
	iot.start()

def stop():
	global running,connected
	dispatch('event',['unregister'])
	running=False
	connected=False
	inq.clear()
	ouq.clear()

def event(etype,msg):
	global ouq
	ouq.push('\a%s: %s'%(etype,msg))

def request(cmd):
	global ouq
	return None
