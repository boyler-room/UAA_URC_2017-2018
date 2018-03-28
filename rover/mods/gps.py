info=\
""""GPS Module"
description:
	Reads data from gps (sparkfun venus)
usage:
	get [param] - get gps value
		status - gps fix status
		lattitude - lattitude, degrees N
		longitude - longitude, degrees E
		altitude - altitude, m above sea level
		course - direction, degrees from N
		speed - speed, km/h
		speedmph - speed, mph
""""Chandra Boyle"

#-------------------API Header--------------------
from base.types import dispatchError
running=False
dispatch=None

#----------Module-Specific Functionality----------
import serial,threading

gpsdev='/dev/ttyUSB0'
params={
	'status':False,
	'lattitude':None,
	'longitude':None,
	'altitude':None,
	'course':None,
	'speed':None,
	'speedmph':None,
}

def gpsread():
	global gpsbus,gpsdev
	global params,running
	try: gpsbus=serial.Serial(gpsdev)
	except:
		running=False
		dispatch('event',['fire','gps','error opening device'])
		return
	while running:
		s=gpsbus.readline()[:-3].strip().split(',')
		if len(s)>1:
			if s[0]=='$GPGSA':
				try:
					d=int(s[2])
					if d>1: params['status']=True
					else: params['status']=False
				except: pass
			elif s[0]=='$GPGSV': pass
			elif s[0]=='$GPRMC': pass
			elif s[0]=='$GPVTG':
				try:
					d=float(s[1])
					params['course']=d
					d=float(s[7])
					params['speed']=d
					params['speedmph']=d*0.621
				except: pass
			elif s[0]=='$GPGGA':
				try:
					d=int(s[2][:2])+float(s[2][2:])/60
					if s[3]=='S': d=-d
					params['lattitude']=d
					d=int(s[4][:3])+float(s[4][3:])/60
					if s[5]=='W': d=-d
					params['longitude']=d
					d=float(s[9])
					params['altitude']=d
				except: pass
	gpsbus.close()

#----------------API Functionality----------------
def init():
	global dispatch

def start():
	global running
	running=True
	threading.Thread(target=gpsread).start()

def stop():
	global running
	running=False

def event(etype,msg):
	global dispatch

def request(cmd):
	global running,dispatch
	reply=None
	if len(cmd)==0: raise dispatchError('Empty command')
	elif cmd[0]=='get' and len(cmd)==2:
		if cmd[1] not in params: raise dispatchError('Invalid parameter')
		reply=params[cmd[1]]
	else: raise dispatchError('Invalid command')
	return reply
