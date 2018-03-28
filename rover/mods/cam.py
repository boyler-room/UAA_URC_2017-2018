info=\
""""Camera Control Module"

description: cameras streaming via gst-launch

usage:
	start [cam]
	stop [cam]
	poll [cam]

""""Chandra Boyle"

#-------------------API Header--------------------
from base.types import dispatchError
running=False
dispatch=None

#----------Module-Specific Functionality----------
import subprocess,signal,threading

cams={#name:[[launch args],popen instance,control param]
	'dummy':[['python','util/dummy.py','placeholder'],None,False],
	'cam0':[['gst-launch-1.0',
					'v4l2src','device=/dev/video0',
				'!','video/x-raw,height=480,framerate=15/1',
				'!','x264enc','tune=zerolatency','bitrate=512',
				'!','mpegtsmux',
				'!','udpsink','host=239.0.0.20','port=8080','sync=false','async=false'
			],None,False],
	'cam1':[['gst-launch-1.0',
					'v4l2src','device=/dev/video1',
				'!','video/x-raw,height=480,framerate=15/1',
				'!','x264enc','tune=zerolatency','bitrate=512',
				'!','mpegtsmux',
				'!','udpsink','host=239.0.0.20','port=8081','sync=false','async=false'
			],None,False],
	'cam2':[['gst-launch-1.0',
					'v4l2src','device=/dev/video2',
				'!','video/x-raw,height=480,framerate=15/1',
				'!','x264enc','tune=zerolatency','bitrate=512',
				'!','mpegtsmux',
				'!','udpsink','host=239.0.0.20','port=8082','sync=false','async=false'
			],None,False],
}

def camthread():
	global running
	while running:
		for c in cams:
			if cams[c][1]!=None and cams[c][1].poll()!=None: cams[c][1]=None
			if cams[c][2] and (cams[c][1]==None):
				clog=open('logs/cam_%s.log'%c,'w')
				cams[c][1]=subprocess.Popen(cams[c][0],stdout=clog,stderr=subprocess.STDOUT)
				cams[c][1].log=clog
				if cams[c][1].poll()!=None:
					#error msg
					cams[c][2]=False
			elif not cams[c][2] and (cams[c][1]!=None):
				cams[c][1].send_signal(signal.SIGINT)
				cams[c][1].wait()
				cams[c][1].log.close()
				cams[c][1]=None
	for c in cams:
		cams[c][2]=False
		if cams[c][1]!=None:
			cams[c][1].send_signal(signal.SIGINT)
			cams[c][1].wait()
			cams[c][1].log.close()
			cams[c][1]=None

#----------------API Functionality----------------
def init():
	global dispatch
	#dispatch('event',['register','autonomy'])

def start():
	global running
	running=True
	cthread=threading.Thread(target=camthread)
	cthread.start()

def stop():
	global running
	running=False

def event(type,msg):
	global dispatch
	#if type=='autonomy' and msg=='Enter Autonomous': disable stereo cam?

def request(cmd):
	global cams
	reply=None
	if len(cmd)==0: raise dispatchError('Empty command')
	elif cmd[0]=='start' and len(cmd)==2:
		if cmd[1] not in cams: raise dispatchError('No such device')
		cams[cmd[1]][2]=True
	elif cmd[0]=='stop' and len(cmd)==2:
		if cmd[1] not in cams: raise dispatchError('No such device')
		cams[cmd[1]][2]=False
	elif cmd[0]=='poll' and len(cmd)==2:
		if cmd[1] not in cams: raise dispatchError('No such device')
		reply=cams[cmd[1]][2]
	else: raise dispatchError('Invalid command')
	return reply
