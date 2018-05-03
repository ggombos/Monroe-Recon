#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Jonas Karlsson
# Date: June 2016
# License: GNU General Public License v3
# Developed for use by the EU H2020 MONROE project

""" Dumps the three first metadata events both in files and on stdout. """
import zmq
import json
#import monroe_exporter
from datetime import datetime
import os
import subprocess
from threading import Thread
from time import sleep

from time import gmtime, strftime
act_time = strftime("%Y.%m.%d-%H.%M.%S", gmtime())

import sys

orig_stdout = sys.stdout
f = open('/monroe/results/script_out.txt', 'w')
sys.stdout = f
finish=False

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

print ("[{}] Hello: Default config {}").format(datetime.now(),
                                               json.dumps(CONFIG,
                                                          sort_keys=True,
                                                          indent=2))

scpCommand = "scp -o StrictHostKeyChecking=no -i /opt/monroe/server_login.key monroe_node@server:~/trace_target_ips.txt ."
output = subprocess.check_output(['bash','-c', scpCommand])

CONFIG['destinations'] = []
trace_ip_file = open('trace_target_ips.txt', 'r')
for line in trace_ip_file:
    CONFIG['destinations'].append(line.split('\n')[0])


def bg_save_gps():
    print "thread started"
    f = open(CONFIG['nodeid']+"_GPSDATA_"+act_time+".txt","w") 
    print "Filename: " + CONFIG['nodeid']+"_GPSDATA_"+act_time+".txt"
    f.write("GPS DATA COLLECTION STARTED!") 
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect ("tcp://172.17.0.1:5556")
    # An empty string subscribes to everything:
    topicfilter = 'MONROE.META.DEVICE.GPS'
    socket.setsockopt(zmq.SUBSCRIBE, topicfilter)
    while not finish:
        string = socket.recv()
        print "GPS_DATA_RECEIVED:" + string
        f.write(string)
    f.close()


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

try:
    try:
        with open(CONFIGFILE) as configfd:
            CONFIG.update(json.load(configfd))
    except Exception as e:
        print ("[{}] Cannot retrive config {} "
           "running outside a monre node?"
           ", skip trying to get metdata").format(datetime.now(), e)

    thread=Thread(target=bg_save_gps)
    thread.start()

    # Attach to the ZeroMQ socket as a subscriber and start listen to
    # MONROE messages
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(CONFIG['zmqport'])
    socket.setsockopt(zmq.SUBSCRIBE, CONFIG['metadata_topic'])
    # End Attach
    destinations=CONFIG['destinations']
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

    print "Measurements starting with " + str(CONFIG['iterations']) + " iterations"
    for i in range(CONFIG['iterations']):
        print "Traceroute iteration: " + str(i+1) + " started"
        bashCommand = ""
        for interface,provider in interfaces.iteritems():
            for dst in destinations:
                bashCommand = bashCommand + "traceroute -i "+interface+" -n -w 2 -q 1 -N 32 -m 16 "+dst+" > " +nodeId+"_"+provider+"_"+dst+"_"+act_time+".txt & \n"
            print bashCommand
            f = open('run_traces.sh','w')
            f.write(bashCommand)
            f.close()
            try:
                output = subprocess.check_output(['bash','-c', 'sh run_traces.sh'])
            except:
                pass

            scpCommand = "scp -o StrictHostKeyChecking=no -i /opt/monroe/server_login.key "+nodeId+"* monroe_node@server:~/trace_results/"
            output = subprocess.check_output(['bash','-c', scpCommand])

            moveCommand = "mv "+nodeId+"* "+CONFIG['resultdir']
            output = subprocess.check_output(['bash','-c', moveCommand])
        
        print "Traceroute iteration " + str(i+1) + "stopped"
        if i != CONFIG['iterations'] - 1:
            print "Sleeping" + str(CONFIG['sleep_between']) + "minutes"
            sleep(60*CONFIG['sleep_between'])
            act_time=strftime("%Y.%m.%d-%H.%M.%S", gmtime())
    finish=True
    print "Measurements finished with " + str(CONFIG['iterations']) + " iterations"


except Exception as e:
    print ("[{}] ERRRORRRRR {} "
           "running outside a monre node?"
           ", skip trying to get metdata").format(datetime.now(), e)

if CONFIG['verbosity'] > 1:
    print "[{}] Hello : Finished the experiment".format(datetime.now())

f.close()
