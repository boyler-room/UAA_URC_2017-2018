info=\
""""Rover Software API: Additional Types and Functions"

description:
    functions and types used by the API and additional useful types and functions

usage:
    lock: simplistic lock class for managing concurrent access
    stack: simplistic concurrency-safe stack class for shared stacks
    queue: simplistic concurrency-safe queue class for shared queues
    dispatchError: exception type used by the API, calls to dispatch should catch this error
    parsecmd(cmd): splits string cmd by spaces, except those in quotes, and parses ints; returns list

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
    def push(self,item):
        self.lock.acquire()
        if item!=None: q.append(item)
        self.lock.release()
    def pop(self):
        item=None
        self.lock.acquire()
        if len(q)>0:
            item=q[-1]
            del q[-1]
        self.lock.release()
        return item
    def peek(self):
        item=None
        self.lock.acquire()
        if len(q)>0:
            item=q[-1]
        self.lock.release()
        return item

class queue:
    def __init__(self):
        self.q=[]
        self.lock=lock()
    def push(self,item):
        self.lock.acquire()
        if item!=None: q.append(item)
        self.lock.release()
    def pop(self):
        item=None
        self.lock.acquire()
        if len(q)>0:
            item=q[0]
            del q[0]
        self.lock.release()
        return item
    def peek(self):
        item=None
        self.lock.acquire()
        if len(q)>0:
            item=q[0]
        self.lock.release()
        return item

class dispatchError(Exception):
    source=None
    code=None

def parsecmd(cmd):
    tlist=[]
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
    return tlist


