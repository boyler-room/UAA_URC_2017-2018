info=\
""""Rover Software API: Terminal Input/Output Module"

description:
    provides access to API interface via stdio for typing commands and printing output via the terminal

usage:
    enter commands as 'module command' to initiate a dispatch call
    replies are printed to stdout and errors and events are printed to stderr
    events can be (un)registered via dispatch to event, all is registered by default
    cmds sent to request() are printed as is; this module has no controllable funtionallity
    this module runs 1 (one) thread

""""Chandra Boyle"

#-------------------API Header--------------------
from basetypes import dispatchError
running=True
dispatch=None

#----------Module-Specific Functionality----------
from threading import Thread
import sys, select

outq=[]
errq=[]

def infunc():
    global running, dispatch
    p=select.poll()
    p.register(sys.stdin)
    while running:
        for ev in p.poll():
            if ev[0]==sys.stdin.fileno() and ev[1]&select.POLLIN==select.POLLIN:
                reply=None
                data=sys.stdin.readline().strip()
                dest=data.split(' ')[0]
                try: reply=dispatch(dest,data[len(dest)+1:])
                except dispatchError as e: sys.stderr.write('Error: %s\n'%e)
                else:
                    if reply!=None: sys.stdout.write('Reply: %s\n'%reply)
                sys.stdout.flush()
                sys.stderr.flush()
    dispatch('event','unregister')

#----------------API Functionality----------------
def init():
    global dispatch
    dispatch('event','register')
    inthread=Thread(target=infunc)
    inthread.daemon=True
    inthread.start()

def start():
    global running

def stop():
    global running

def event(etype,msg):
    global running
    sys.stderr.write('Event: %s "%s"\n'%(etype,msg))
    sys.stderr.flush()

def request(cmd):
    global running
    reply=None
    sys.stdout.write('%s\n'%cmd)
    sys.stdout.flush()
    return reply
