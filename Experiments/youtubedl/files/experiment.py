#!/usr/bin/python
# -*- coding: utf-8 -*-

from time import gmtime, strftime
from datetime import datetime
import zmq
import json
import subprocess
import os

CONFIGFILE = '/monroe/config'

# Default values (overwritable from the CONFIGFILE)
CONFIG = {
		"zmqport": "tcp://172.17.0.1:5556",
		"nodeid": "fake.nodeid",  # Need to overriden
		"metadata_topic": "MONROE.META.DEVICE.MODEM",
		"verbosity": 2,  # 0 = "Mute", 1=error, 2=Information, 3=verbose
		"resultdir": "/monroe/results/",
		"nr_of_messages": 30,
		"destinations":[],
		"doNotUseIFs":['lo','docker0','metadata'],
		"iterations":1,
		"sleep_between":5,
		}

def changeInterface(interface,on):
	pass
	# if on:
		# output = subprocess.check_output(['bash','-c', "ifconfig "+interface+" down"])
	# else:
		# output = subprocess.check_output(['bash','-c', "ifconfig "+interface+" up"])

def enableInterfaces(interfaces):
	for interface,provider in interfaces.iteritems():
		print "Enable: "+interface+" ("+provider+")"
		changeInterface(interface,True)	

def disableInterfaces(interfaces):
	for interface,provider in interfaces.iteritems():
		print "Disable: "+interface+" ("+provider+")"
		changeInterface(interface,False)

def getInterfaceIp(interface):
	s = subprocess.check_output(['bash','-c', "ifconfig "+interface+" | grep \"inet \" | awk '{ print $2 }'"])
	return s.rstrip()
	
def runYoutube(interface,provider,nodeId):
	#print "Enable interface: "+interface+" ("+provider+")"
	#changeInterface(interface,True)
	act_time = strftime("%Y.%m.%d-%H.%M.%S", gmtime())
	ip = getInterfaceIp(interface)
	
	for video in ['video_pop_short','video_pop_long','video_nonpop_short','video_nonpop_long']:
		output = subprocess.check_output(['bash','-c', "./pytomo-master/start_crawl.py \""+ip+"\" -f /opt/monroe/"+video+".txt -r 1 -u 1 -b >> /monroe/results/res_"+nodeId+"_"+video+"_"+interface+"_"+provider+"_"+act_time+".txt"])
		output = subprocess.check_output(['bash','-c', "cp logs/* /monroe/results/"])		
		
		print "Youtube video ("+video+") downloaded on ",nodeId,"interface:",interface,provider,"ip:",ip
		saveResults()
	
	#print "Disable interface: "+interface+" ("+provider+")"
	#changeInterface(interface,False)


def getOperator(interface):
	print interface
	if interface[0:4]=='wlan' or interface[0:3]=='eth':
		return interface
	for i in range(1,10):
		data = socket.recv()
		print data
		ifinfo = json.loads(data.split(" ", 1)[1])
		if ('InternalInterface' in ifinfo and ifinfo['InternalInterface'] == interface):
			return ifinfo['Operator'].replace(' ','-')
	return 'UNKNOWN-OPERATOR'

def initYoutube():
	print "INIT pytomo"
	output = subprocess.check_output(['bash','-c', "scp -r -o StrictHostKeyChecking=no -i /opt/monroe/server_login.key monroe_node@server:~/pytomo-master.tar.gz ."])
	
	output = subprocess.check_output(['bash','-c', "tar -xvf pytomo-master.tar.gz"])
	
	
	print "pytomo downloaded"

	output = subprocess.check_output(['bash','-c', "scp -r -o StrictHostKeyChecking=no -i /opt/monroe/server_login.key monroe_node@server:~/youtube/video*.txt /opt/monroe/"])

	
	# output = subprocess.check_output(['bash','-c', "echo \"http://youtube.com/watch?v=JGwWNGJdvx8\" > /opt/monroe/video_pop_short.txt"])

	# output = subprocess.check_output(['bash','-c', "echo \"http://www.youtube.com/watch?v=Bs5Ml7_2wT0\" > /opt/monroe/video_pop_long.txt"])
	
	# output = subprocess.check_output(['bash','-c', "echo \"http://www.youtube.com/watch?v=rjf94G9HFkU\" > /opt/monroe/video_nonpop_short.txt"])

	# output = subprocess.check_output(['bash','-c', "echo \"http://www.youtube.com/watch?v=w5k7A7vuVic\" > /opt/monroe/video_nonpop_long.txt"])
	

def saveResults():
#	output = subprocess.check_output(['bash','-c', "scp -r -o StrictHostKeyChecking=no -i /opt/monroe/server_login.key /monroe/results/* monroe_node@server:~/youtube/results/"])
	
	print "Results saved "
	
def startTCPDumps(nodeId,ifs):
	act_time = strftime("%Y.%m.%d-%H.%M.%S", gmtime())

	for interface in ifs:
		print "START DUMP on ",interface + "---" +interfaces[interface]
		output = subprocess.call(['bash','-c', "tcpdump -i "+interface+" --snapshot-length=100 -w /monroe/results/dump_"+nodeId+"_"+interface+"_"+act_time+".pcap &"])

def killTCPDumps():
	pids = subprocess.check_output(['bash','-c', "ps aux | grep 'tcpdump' | awk '{ print $2 }'"]).splitlines()
	for pid in pids:
		subprocess.check_output(['bash','-c', "kill "+pid]).splitlines()
	
try:
	try:
		with open(CONFIGFILE) as configfd:
			CONFIG.update(json.load(configfd))
	except Exception as e:
		print ("[{}] Cannot retrive config {} "
		   "running outside a monre node?"
		   ", skip trying to get metdata").format(datetime.now(), e)
	
	initYoutube()
	
	
	# Attach to the ZeroMQ socket as a subscriber and start listen to
	# MONROE messages
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.connect(CONFIG['zmqport'])
	socket.setsockopt(zmq.SUBSCRIBE, CONFIG['metadata_topic'])
	
	nodeId=CONFIG['nodeid']
	
	interfaces={}
	ifs=os.listdir('/sys/class/net/')
	print "Interfaces:" + str(ifs)
	for noIF in CONFIG['doNotUseIFs']: 
		try:
			ifs.remove(noIF)
		except:
			pass

	print "Interfaces we will use:" + str(ifs)
	for interface in ifs:
		interfaces[interface]=getOperator(interface)

	print 'INTERFACE INFO COLLECTED'
	for interface in ifs:
		print interface + "---" +interfaces[interface]
	
	print "Disable all interfaces"
	#disableInterfaces(interfaces)
	
	startTCPDumps(nodeId,ifs)

	
	for interface,provider in interfaces.iteritems():
		runYoutube(interface,provider,nodeId)

	#enableInterfaces(interfaces)
	killTCPDumps()
	saveResults()

except Exception as e:
	print ("[{}] ERRRORRRRR {} "
			"running outside a monre node?"
			", skip trying to get metdata").format(datetime.now(), e)

if CONFIG['verbosity'] > 1:
	print "[{}] Hello : Finished the experiment".format(datetime.now())
