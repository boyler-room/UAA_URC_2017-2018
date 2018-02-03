info=\
""""Simple Client For Rover TCP Communication"

description:
    client end for rover comm module

usage:
    

""""Chandra Boyle"

import socket,sys,threading

def inthread():
	global inq,connected
	while connected:
		line=sys.stdin.readline()
		inq.append(line)

inq=[]
sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address=('127.0.0.1',9990)
ithread=threading.Thread(target=inthread)
ithread.daemon=True

sock.connect(address)
print 'connected'
connected=True
ithread.start()
sock.setblocking(0)
try:
	while connected:
		try:
			data=sock.recv(1024)
			if data=='': connected=False
			data=data.strip().split('\n')
			for s in data:
				if s[0]!='\a': print s
		except: pass
		for s in inq:
			sock.sendall(s)
			inq.remove(s)
			#except: connected=False
except: pass
sock.close()
print 'disconnected'
