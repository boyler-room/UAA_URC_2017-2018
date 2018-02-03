info=\
""""Title"

description:

usage:

""""Author"

#-------------------API Header--------------------
from base.types import dispatchError
running=False
dispatch=None

#----------Module-Specific Functionality----------

#----------------API Functionality----------------
def init():
	global dispatch

def start():
	global running
	running=True

def stop():
	global running
	running=False

def event(etype,msg):
	global dispatch

def request(cmd):
	global running,dispatch
	reply=None
	return reply
