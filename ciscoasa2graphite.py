#!/usr/bin/env python

import os
import pickle
import platform
import re
import struct
import subprocess
import sys
import time
from optparse import OptionParser
from socket import socket
from pysnmp.entity.rfc3413.oneliner import cmdgen

"""
Cisco ASA to Graphite

Reads all the interesting numbers from Cisco ASA over SNMP and ships them
over to the target Graphite installation.

Well, for now reads only interfaces counters.
"""

def main():
    # process options and arguments
    usage = "usage: %prog [options] target_host carbon_host"
    parser = OptionParser(usage)

    parser.add_option("-c", "--community", dest="community",
        help="snmp community name",
        action="store", default="public")
    parser.add_option("-s", "--snmpport", dest="snmpport",
        help="snmp target port",
        action="store", default=161)
    parser.add_option("-p", "--port", dest="port",
        help="carbon server port",
        action="store", default=2004)

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("you must specify target_host and carbon_host as a command line option!")

    # assign some sane variable names to command line arguments
    carbon_host = args[1] # carbon server hostname
    target_host = args[0] # carbon server hostname

    # try to establish connection with carbon server
    sock = socket()
    try:
        sock.connect((carbon_host,options.port))
    except:
        print("Couldn't connect to %s on port %d, is carbon-agent.py running?"
              % (carbon_host, options.port))

    data = []
    timestamp = int(time.time())

    # TODO: fetch all the relevant data in one go and organise in a different way
    errorIndication, errorStatus, errorIndex, sysName = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1,3,6,1,2,1,1,5))

    errorIndication, errorStatus, errorIndex, ifIndex = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1,3,6,1,2,1,2,2,1,1))

    errorIndication, errorStatus, errorIndex, ifDescr = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1,3,6,1,2,1,31,1,1,1,1))

    errorIndication, errorStatus, errorIndex, ifInOctets = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1,3,6,1,2,1,2,2,1,10))

    errorIndication, errorStatus, errorIndex, ifOutOctets = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1,3,6,1,2,1,2,2,1,16))

    hostname = re.search(r'^([a-zA-Z0-9-]+).*', str(sysName[0][0][1])).group(1) # assigns and strips out the hostname

    # assumes all the results from SNMP are in right (the same) order
    interfaces = zip(ifIndex, ifDescr, ifInOctets, ifOutOctets)

    for row in interfaces:
        data.append(("servers.%s.%s_traffic_in" % (
            hostname,
            str(row[1][0][1]).replace('/', '_')), # interface name; change / into _ to help grahite tree organisation
            (
                timestamp,
                int(row[2][0][1]) # traffic IN
            )))
        data.append(("servers.%s.%s_traffic_out" % (
            hostname,
            str(row[1][0][1]).replace('/', '_')),
            (
                timestamp,
                int(row[3][0][1]) # traffic OUT
            )))

    # send gathered data to carbon server as a pickle packet
    payload = pickle.dumps(data)
    header = struct.pack("!L", len(payload))
    message = header + payload

    sock.sendall(message)
    sock.close()

if __name__ == '__main__':
    main()
