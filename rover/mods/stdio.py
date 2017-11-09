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
from basetypes import dispatchError, queue
running=True
dispatch=None

#----------Module-Specific Functionality----------
from threading import Thread
import sys, select

inq=queue()
outq=queue()
errq=queue()

def iothread():
    global running, dispatch
    p=select.poll()
    p.register(sys.stdin)
    while running:
        ev=p.poll()
        if len(ev)>0 and ev[0][1]&select.POLLIN==select.POLLIN:#data to read
            inq.push(sys.stdin.readline().strip())
        if outq.peek()!=None:#data to write
            sys.stdout.write('\r%s\n'%(outq.pop()))
            sys.stdout.flush()
        if errq.peek()!=None:#data to write
            sys.stderr.write('\r%s\n'%(errq.pop()))
            sys.stderr.flush()
        if inq.peek()!=None:#cmds to send
            data=inq.pop()
            dest=data.split(' ')[0]
            data=data[len(dest)+1:]
            try: reply=dispatch(dest,data)
            except dispatchError as e: errq.push('Error: %s'%e)
            else:
                if reply!=None: outq.push('Reply: %s'%reply)

    p.unregister(sys.stdin)
    dispatch('event','unregister')

#----------------API Functionality----------------
def init():
    global dispatch
    dispatch('event','register')
    ith=Thread(target=iothread)
    ith.daemon=True
    ith.start()

def start():
    global running

def stop():
    global running

def event(etype,msg):
    global errq
    errq.push('Event: %s "%s"'%(etype,msg))

def request(cmd):
    global outq
    outq.push(cmd)
    return None
