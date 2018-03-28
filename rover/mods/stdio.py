info=\
""""Simple User Input Module"

description: simple text-based interface to command system

usage:
	commands entered into stdin
	responses printed to stdout
	events and errors written to stderr when errv True
	accepts commands
		print: print a string to stdout
		noprinterr: disable printing to stderr
		printerr: enable printing to stderr
	enter commands as module command

""""Chandra Boyle"

#-------------------API Header--------------------
from base.types import dispatchError, parsecmd
running=False
dispatch=None

#----------Module-Specific Functionality----------
import sys,threading

errv=True
thread=None
def inthread():
	global running,dispatch
	global thread,errv
	while running:
		data=sys.stdin.readline().strip()
		dest,cmd=parsecmd(data)
		try: resp=dispatch(dest,cmd)
		except dispatchError as e:
			resp='Error: %s'%e
			if errv: sys.stderr.write('%s\n'%e)
		if resp!=None: sys.stdout.write('%s\n'%resp)
	thread=None

#----------------API Functionality----------------
def init():
	global dispatch
	dispatch('event',['register'])

def start():
	global running
	global thread
	running=True
	if thread==None:
		thread=threading.Thread(target=inthread)
		thread.daemon=True
		thread.start()

def stop():
	global running
	running=False

def event(etype, msg):
	global errv
	if errv: sys.stderr.write('Event %s: %s\n'%(etype,msg))

def request(cmd):
	global dispatch
	global errv
	reply=None
	if len(cmd)==0: raise dispatchError('Empty command')

	elif cmd[0]=='print' and len(cmd)==2:
		sys.stdout.write('%s\n'%cmd[1])
	elif cmd[0]=='printerr' and len(cmd)==1:
		errv=True
	elif cmd[0]=='noprinterr' and len(cmd)==1:
		errv=False

	else: raise dispatchError('Invalid command')
	return reply
