info=\
""""Rover Software API: Main Implementation"

description:
    API to initialize and manage rover modules

usage:
    in main app file:
       import base
       call addmod() to add modules
       [call event() to register event types]
       [call mod() to start modules]
       call loop()
    in module file
       declare running,dispatch
       define init(), start(), stop(), event(etype,msg), request(cmd)
       API functions must not block or delay
       communication with other modules thru dispatch()

""""Chandra Boyle"

import sys
from time import time, sleep

#--------------------API Base---------------------
from basetypes import lock, dispatchError, parsecmd

running=False
routing={}
logfile=open('logs/%f.log'%time(),'wb')

def log(msg):
    global logfile
    log.lock.acquire()
    logfile.write('@%f: %s\n'%(time(),msg))
    logfile.flush()
    log.lock.release()
log.lock=lock()

def event(cmd,src):
    global routing
    reply=None
    #log('event call %s from %s'%(cmd,src))
    if src not in routing: raise dispatchError('Invalid module')
    cmd=parsecmd(cmd)
    if len(cmd)==0: raise dispatchError('Empty command')

    elif cmd[0]=='fire' and len(cmd)==3:
        log('event %s:"%s" fired by %s'%(cmd[1],cmd[2],src))
        etype='!'+cmd[1]
        event.lock.acquire()
        for d in event.directory['all']:
            if routing[d].running==True: routing[d].event(cmd[1],cmd[2])
        if etype in event.directory:
            for d in event.directory[etype]:
                if routing[d].running==True: routing[d].event(cmd[1],cmd[2])
        event.lock.release()
    elif cmd[0]=='register' and len(cmd)==1:
        event('unregister',src)
        event.lock.acquire()
        if src not in event.directory['all']: event.directory['all'].append(src)
        event.lock.release()
    elif cmd[0]=='register' and len(cmd)==2:
        if cmd[1]=='all': event('register',src)
        elif src not in event.directory['all']:
            etype='!'+cmd[1]
            event.lock.acquire()
            if etype not in event.directory: event.directory[etype]=[]
            if src not in event.directory[etype]: event.directory[etype].append(src)
            event.lock.release()
    elif cmd[0]=='unregister' and len(cmd)==1:
        event.lock.acquire()
        if src not in event.directory['all']:
             for d in event.directory.keys():
                if src in event.directory[d]:
                    event.directory[d].remove(src)
                    if event.directory[d]==[]: del event.directory[d]
        else: event.directory['all'].remove(src)
        event.lock.release()
    elif cmd[0]=='unregister' and len(cmd)==2:
        if cmd[1]=='all': event('unregister',src)
        elif src not in event.directory['all']:
            event.lock.acquire()
            etype='!'+cmd[1]
            if etype in event.directory and src in event.directory[etype]:
                event.directory[etype].remove(src)
                if event.directory[etype]==[]: del event.directory[etype]
            event.lock.release()
    elif cmd[0]=='list' and len(cmd)==1:
        reply=[]
        event.lock.acquire()
        for d in event.directory:
            if src in event.directory[d]:
                if d=='all': reply=['all']
                else: reply.append(d[1:])
        event.lock.release()
    elif cmd[0]=='list' and len(cmd)==2:
        reply=[]
        event.lock.acquire()
        if cmd[1]=='all': etype='all'
        else: etype='!'+cmd[1]
        if etype in event.directory:
            for d in event.directory[etype]: reply.append(d)
        event.lock.release()

    else: raise dispatchError('Invalid command')
    return reply
event.directory={ 'all':[] }
event.lock=lock()

def mod(cmd):
    global routing, running
    reply=None
    #log('mod call %s'%(cmd))
    cmd=parsecmd(cmd)
    if len(cmd)==0: raise dispatchError('Empty command')

    elif cmd[0]=='stop' and len(cmd)==1:
        log('app is going down')
        mod('stop all')
        running=False
    elif cmd[0]=='stop' and len(cmd)==2:
        if cmd[1]=='app': mod('stop')
        elif cmd[1]=='all':
            for m in routing: mod('stop %s'%m)
        elif cmd[1] in routing:
            if routing[cmd[1]].running==True:
                log('stopping %s'%(cmd[1]))
                routing[cmd[1]].stop()
        else: raise dispatchError('Invalid module')
    elif cmd[0]=='start' and len(cmd)==2:
        if cmd[1]=='all':
            for m in routing: mod('start %s'%m)
        elif cmd[1] in routing:
            if routing[cmd[1]].running==False:
                log('starting %s'%(cmd[1]))
                routing[cmd[1]].start()
        else: raise dispatchError('Invalid module')
    elif cmd[0]=='poll' and len(cmd)==2:
        if cmd[1] in routing: reply={True:'running',False:'stopped'}[routing[cmd[1]].running]
        else: raise dispatchError('Invalid module')

    else: raise dispatchError('Invalid command')
    return reply

#--------------------Dispatch---------------------
def dispatch(src,dest,cmd):
    global routing, running
    reply=None
    #log('request "%s" from %s to %s'%(cmd,src,dest))
    try:
        #aliases
        if dest=='exit' or dest=='quit' or dest=='stop': reply=mod('stop')
        #base modules
        elif dest=='log': log('message "%s" from %s'%(cmd,src))
        elif dest=='mod': reply=mod(cmd)
        elif dest=='event': reply=event(cmd,src)
        #app modules
        elif dest in routing:
            if running==False: raise dispatchError('App not running')
            log('request "%s" from %s to %s'%(cmd,src,dest))
            if routing[dest].running==True:
                reply=routing[dest].request(cmd)
            else: raise dispatchError('Module not running')
        else: raise dispatchError('Invalid module')
    except dispatchError as e:
        log('dispatch failure "%s" from %s in request "%s" from %s'%(e,dest,cmd,src))
        raise dispatchError(e)
    except:
        log('unanticipated failure')
        print 'unanticipated failure!'
        mod('stop')
    if reply!=None: log('response "%s" from %s in request "%s" from %s'%(reply,dest,cmd,src))
    return reply

#-------------------Add Modules-------------------
def addmod(mod):
    global routing
    if mod in routing: return
    API=('running','dispatch','request','event','init','start','stop')
    mods=__import__('mods.'+mod)
    mx=getattr(mods,mod)
    for e in API:
        if not hasattr(mx,e): raise ImportError('Incompatible module %s'%mod)
    routing[mod]=mx
    log('added module %s'%(mod))
    mx.dispatch=lambda x,y: dispatch(mod,x,y)
    mx.init()

#--------------------App Loop---------------------
def loop():
    global running, logfile

    running=True
    print 'starting...'

    try:
        while running: pass
    except:
        mod('stop')

    print 'exiting...'
    logfile.close()
