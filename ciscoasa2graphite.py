#!/usr/bin/env python

import pickle
import re
import struct
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
    parser.add_option("-n", "--custom-host-name", dest="custom_host_name",
        help="custom host name to show in Graphite",
        action="store", default="")
    parser.add_option("-g", "--custom-group-name", dest="custom_group_name",
        help="custom group name to show in Graphite",
        action="store", default="servers")

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("you must specify target_host and carbon_host as a command line option!")

    # assign some sane variable names to command line arguments
    carbon_host = args[1]  # carbon server hostname
    target_host = args[0]  # carbon server hostname

    # try to establish connection with carbon server
    sock = socket()
    try:
        sock.connect((carbon_host, options.port))
    except:
        print("Couldn't connect to %s on port %d, is carbon-agent.py running?"
              % (carbon_host, options.port))

    data = []
    timestamp = int(time.time())

    # TODO: fetch all the relevant data in one go and organise in a different way
    errorIndication, errorStatus, errorIndex, sysName = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 2, 1, 1, 5))

    errorIndication, errorStatus, errorIndex, ifIndex = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 2, 1, 2, 2, 1, 1))

    errorIndication, errorStatus, errorIndex, ifDescr = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 2, 1, 31, 1, 1, 1, 1))

    errorIndication, errorStatus, errorIndex, ifInOctets = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 2, 1, 2, 2, 1, 10))

    errorIndication, errorStatus, errorIndex, ifOutOctets = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 2, 1, 2, 2, 1, 16))

    errorIndication, errorStatus, errorIndex, ifInDiscarded = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 2, 1, 2, 2, 1, 13))

    errorIndication, errorStatus, errorIndex, ifOutDiscarded = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 2, 1, 2, 2, 1, 19))

    errorIndication, errorStatus, errorIndex, ifInError = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 2, 1, 2, 2, 1, 14))

    errorIndication, errorStatus, errorIndex, ifOutError = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 2, 1, 2, 2, 1, 20))

    errorIndication, errorStatus, errorIndex, cpmCPUTotal1min = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 109, 1, 1, 1, 1, 4))

    errorIndication, errorStatus, errorIndex, ramUsed = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 48, 1, 1, 1, 5))

    errorIndication, errorStatus, errorIndex, ramFree = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 48, 1, 1, 1, 6))

    errorIndication, errorStatus, errorIndex, snmpInOctets = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 2, 1, 11, 1))

    errorIndication, errorStatus, errorIndex, snmpOutOctets = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 2, 1, 11, 2))

    errorIndication, errorStatus, errorIndex, snmpBadVersion = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 2, 1, 11, 3))

    errorIndication, errorStatus, errorIndex, snmpBadCommunityName = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 2, 1, 11, 4))

    errorIndication, errorStatus, errorIndex, snmpBadCommunityUse = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 2, 1, 11, 5))

    errorIndication, errorStatus, errorIndex, ikeActiveTunnels = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 2, 1, 1))

    errorIndication, errorStatus, errorIndex, ikeGlobalInOctets = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 2, 1, 3))

    errorIndication, errorStatus, errorIndex, ikeGlobalInDrops = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 2, 1, 5))

    errorIndication, errorStatus, errorIndex, ikeGlobalOutOctets = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 2, 1, 11))

    errorIndication, errorStatus, errorIndex, ikeGlobalOutDrops = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 2, 1, 13))

    errorIndication, errorStatus, errorIndex, ikeGlobalAuthFails = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 2, 1, 23))

    errorIndication, errorStatus, errorIndex, ipsecActiveTunnels = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 3, 1, 1))

    errorIndication, errorStatus, errorIndex, ipsecGlobalInOctets = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 3, 1, 3))

    errorIndication, errorStatus, errorIndex, ipsecGlobalInDrops = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 3, 1, 10))

    errorIndication, errorStatus, errorIndex, ipsecGlobalInAuthFails = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 3, 1, 13))

    errorIndication, errorStatus, errorIndex, ipsecGlobalOutOctets = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 3, 1, 16))

    errorIndication, errorStatus, errorIndex, ipsecGlobalOutDrops = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 3, 1, 23))

    errorIndication, errorStatus, errorIndex, ipsecGlobalOutAuthFails = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 3, 1, 25))

    errorIndication, errorStatus, errorIndex, connActive = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 491, 1, 1, 1, 6))

    errorIndication, errorStatus, errorIndex, connRate1m = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 491, 1, 1, 1, 10))

    errorIndication, errorStatus, errorIndex, connRate5m = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', options.community, 0),
            cmdgen.UdpTransportTarget((target_host, options.snmpport)),
            (1, 3, 6, 1, 4, 1, 9, 9, 491, 1, 1, 1, 11))
            
    if options.custom_host_name:
      hostname = options.custom_host_name
    else:
      hostname = re.search(r'^([a-zA-Z0-9-]+).*', str(sysName[0][0][1])).group(1)  # assigns and strips out the hostname

    # assumes all the results from SNMP are in right (the same) order
    interfaces = zip(ifIndex, ifDescr, ifInOctets, ifOutOctets, ifInDiscarded, ifOutDiscarded, ifInError, ifOutError)

    for row in interfaces:
        data.append(("%s.%s.%s_traffic_in" % (
            options.custom_group_name,
            hostname,
            str(row[1][0][1]).replace('/', '_')),  # interface name; change / into _ to help grahite tree organisation
            (
                timestamp,
                int(row[2][0][1])  # traffic IN
            )))
        data.append(("%s.%s.%s_traffic_out" % (
            options.custom_group_name,
            hostname,
            str(row[1][0][1]).replace('/', '_')),
            (
                timestamp,
                int(row[3][0][1])  # traffic OUT
            )))
        data.append(("%s.%s.%s_discarded_in" % (
            options.custom_group_name,
            hostname,
            str(row[1][0][1]).replace('/', '_')),
            (
                timestamp,
                int(row[4][0][1])  # discarded IN
            )))
        data.append(("%s.%s.%s_discarded_out" % (
            options.custom_group_name,
            hostname,
            str(row[1][0][1]).replace('/', '_')),
            (
                timestamp,
                int(row[5][0][1])  # discarded OUT
            )))
        data.append(("%s.%s.%s_errors_in" % (
            options.custom_group_name,
            hostname,
            str(row[1][0][1]).replace('/', '_')),
            (
                timestamp,
                int(row[6][0][1])  # errors IN
            )))
        data.append(("%s.%s.%s_errors_out" % (
            options.custom_group_name,
            hostname,
            str(row[1][0][1]).replace('/', '_')),
            (
                timestamp,
                int(row[7][0][1])  # errors OUT
            )))

    # cpu usage
    data.append(("%s.%s.cpu_total_1min" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(cpmCPUTotal1min[0][0][1])  # cpmCPUTotal1min
        )))

    # ram used
    data.append(("%s.%s.ram_used" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(ramUsed[0][0][1])  # ramUsed
        )))

    # ram free
    data.append(("%s.%s.ram_free" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(ramFree[0][0][1])  # ramFree
        )))

    # snmp in
    data.append(("%s.%s.snmp_traffic_in" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(snmpInOctets[0][0][1])  # snmpInOctets
        )))

    # snmp out
    data.append(("%s.%s.snmp_traffic_out" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(snmpOutOctets[0][0][1])  # snmpOutOctets
        )))

    # snmp bad version
    data.append(("%s.%s.snmp_bad_version" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(snmpBadVersion[0][0][1])  # snmpBadVersion
        )))

    # snmp community name
    data.append(("%s.%s.snmp_bad_community_name" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(snmpBadCommunityName[0][0][1])  # snmpBadCommunityName
        )))

    # snmp community use
    data.append(("%s.%s.snmp_bad_community_use" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(snmpBadCommunityUse[0][0][1])  # snmpBadCommunityUse
        )))

    # ike active tunnels
    data.append(("%s.%s.ike_active_tunnels" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(ikeActiveTunnels[0][0][1])  # ikeActiveTunnels
        )))

    # ike global in octets
    data.append(("%s.%s.ike_global_traffic_in" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(ikeGlobalInOctets[0][0][1])  # ikeGlobalInOctets
        )))

    # ike global in drops
    data.append(("%s.%s.ike_global_drops_in" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(ikeGlobalInDrops[0][0][1])  # ikeGlobalInDrops
        )))

    # ike global out octets
    data.append(("%s.%s.ike_global_traffic_out" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(ikeGlobalOutOctets[0][0][1])  # ikeGlobalOutOctets
        )))

    # ike global out drops
    data.append(("%s.%s.ike_global_drops_out" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(ikeGlobalOutDrops[0][0][1])  # ikeGlobalOutDrops
        )))

    # ike global auth fails
    data.append(("%s.%s.ike_global_auth_fails" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(ikeGlobalAuthFails[0][0][1])  # ikeGlobalAuthFails
        )))

    # ipsec active tunnels
    data.append(("%s.%s.ipsec_active_tunnels" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(ipsecActiveTunnels[0][0][1])  # ipsecActiveTunnels
        )))

    # ipsec global in octets
    data.append(("%s.%s.ipsec_global_traffic_in" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(ipsecGlobalInOctets[0][0][1])  # ipsecGlobalInOctets
        )))

    # ipsec global in drops
    data.append(("%s.%s.ipsec_global_drops_in" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(ipsecGlobalInDrops[0][0][1])  # ipsecGlobalInDrops
        )))

    # ipsec global in auth fails
    data.append(("%s.%s.ipsec_global_auth_fails_in" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(ipsecGlobalInAuthFails[0][0][1])  # ipsecGlobalInAuthFails
        )))

    # ipsec global out octets
    data.append(("%s.%s.ipsec_global_traffic_out" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(ipsecGlobalOutOctets[0][0][1])  # ipsecGlobalOutOctets
        )))

    # ipsec global out drops
    data.append(("%s.%s.ipsec_global_drops_in" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(ipsecGlobalOutDrops[0][0][1])  # ipsecGlobalOutDrops
        )))

    # ipsec global out auth fails
    data.append(("%s.%s.ipsec_global_auth_fails_out" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(ipsecGlobalOutAuthFails[0][0][1])  # ipsecGlobalOutAuthFails
        )))

    # conn active
    data.append(("%s.%s.conn_active" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(connActive[0][0][1])  # connActive
        )))

    # conn rate 1min
    data.append(("%s.%s.conn_rate_1min" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(connRate1m[0][0][1])  # connRate1m
        )))

    # conn rate 5min
    data.append(("%s.%s.conn_rate_5min" % (
        options.custom_group_name,
        hostname),
        (
            timestamp,
            int(connRate5m[0][0][1])  # connRate5m
        )))

    # send gathered data to carbon server as a pickle packet
    payload = pickle.dumps(data)
    header = struct.pack("!L", len(payload))
    message = header + payload

    sock.sendall(message)
    sock.close()

if __name__ == '__main__':
    main()
