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

CONFIGFILE = '/monroe/config'

orig_stdout = sys.stdout
f = open('/monroe/results/script_out.txt', 'w')
sys.stdout = f

# Default values (overwritable from the CONFIGFILE)
CONFIG = {
        "zmqport": "tcp://172.17.0.1:5556",
        "nodeid": "fake.nodeid",  # Need to overriden
        "metadata_topic": "MONROE.META.DEVICE.MODEM",
        "verbosity": 2,  # 0 = "Mute", 1=error, 2=Information, 3=verbose
        "resultdir": "/monroe/results/",
        "nr_of_messages": 30,
        "destinations":[
                        '195.37.16.121',
                        '170.140.119.70',
                        '219.243.208.60',
                        '142.150.238.12',
                        '153.90.1.34',
                        '130.194.252.8',
                        '219.243.208.62',
                        '128.36.233.154',
                        '156.56.250.227',
                        '130.216.1.22',
                        '116.89.165.133',
                        '165.242.90.128',
                        '194.79.147.164',
                        '156.56.250.226',
                        '139.30.240.191',
                        '194.79.147.165',
                        '203.178.133.11',
                        '198.108.101.61',
                        '134.197.113.4',
                        '193.226.19.31',
                        '137.165.1.114'
                       ],
        "doNotUseIFs":['lo','docker0','metadata'],
        }

print ("[{}] Hello: Default config {}").format(datetime.now(),
                                               json.dumps(CONFIG,
                                                          sort_keys=True,
                                                          indent=2))

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

    for interface,provider in interfaces.iteritems():
        for dst in destinations:
            bashCommand = "traceroute -i "+interface+" -n "+dst+" > "+nodeId+"_"+provider+"_"+dst+".txt"
            print bashCommand
            output = subprocess.check_output(['bash','-c', bashCommand])

    copyCommand = "cp "+nodeId+"* "+CONFIG['resultdir']
    output = subprocess.check_output(['bash','-c', copyCommand])
    
    scpCommand = "scp -o StrictHostKeyChecking=no -i /opt/monroe/server_login.key "+nodeId+"* monroe_node@server:~/trace_results/"
    output = subprocess.check_output(['bash','-c', scpCommand])


except Exception as e:
    print ("[{}] ERRRORRRRR {} "
           "running outside a monre node?"
           ", skip trying to get metdata").format(datetime.now(), e)

if CONFIG['verbosity'] > 1:
    print "[{}] Hello : Finished the experiment".format(datetime.now())

f.close()
