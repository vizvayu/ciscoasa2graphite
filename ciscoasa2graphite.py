#!/usr/bin/env python

import pickle
import re
import struct
import time
import pprint
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
    parser.add_option("-o", "--single", dest="single",
        help="run a single time and exit",
        action="store_true", default=False)
    parser.add_option("-d", "--delay", dest="delay",
        help="wait <delay> seconds between each connection",
        action="store", default=30)
    parser.add_option("", "--debug", dest="debug",
        help="do not send any data to Graphite, print the data to the screen instead",
        action="store_true", default=False)

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("You must specify target_host and carbon_host")

    # assign some sane variable names to command line arguments
    carbon_host = args[1]  # carbon server hostname
    target_host = args[0]  # carbon server hostname

    oldOctetsIn = [0 for i in range(30)]
    oldOctetsOut = [0 for i in range(30)]
    
    while True:
        # try to establish connection with carbon server
        sock = socket()
        try:
            sock.connect((carbon_host, options.port))
        except:
            print("Couldn't connect to %s on port %d, is carbon-agent.py running?"
                  % (carbon_host, options.port))

        data = []
        timestamp = int(time.time())

        snmpDescInt = (
            '',								# 0 ifDescr
            'octets_in',					# 1 ifInOctets
            'octets_out',					# 2 ifOutOctets
            'discarded_in',					# 3 ifInDiscarded
            'discarded_out',				# 4 ifOutDiscarded
            'errors_in',					# 5 ifInError
            'errors_out',					# 6 ifOutError
        )
        
        snmpDescConn = (
            'conn_active',					# 0 connActive
            'conn_rate_1min',	            # 1 connRate1m
            'conn_rate_5min',           	# 2 connRate5m
        
        )

        snmpDesc = (
            '',								# 0 sysName
            'cpu_total_1min',	            # 1 cpmCPUTotal1min
            'ram_used', 				    # 2 ramUsed
            'ram_free',	    			    # 3 ramFree
            'snmp_traffic_in',			    # 4 snmpInOctets
            'snmp_traffic_out',			    # 5 snmpOutOctets
            'snmp_bad_version',			    # 6 snmpBadVersion
            'snmp_bad_community_name',	    # 7 snmpBadCommunityName
            'snmp_bad_community_use', 	    # 8 snmpBadCommunityUse
            'ike_active_tunnels',		    # 9 ikeActiveTunnels
            'ike_global_traffic_in',	    # 10 ikeGlobalInOctets
            'ike_global_drops_in',		    # 11 ikeGlobalInDrops
            'ike_global_traffic_out',	    # 12 ikeGlobalOutOctets
            'ike_global_drops_out',		    # 13 ikeGlobalOutDrops
            'ike_global_auth_fails',	    # 14 ikeGlobalAuthFails
            'ipsec_active_tunnels',		    # 15 ipsecActiveTunnels
            'ipsec_global_traffic_in',		# 16 ipsecGlobalInOctets
            'ipsec_global_drops_in',		# 17 ipsecGlobalInDrops
            'ipsec_global_auth_fails_in',	# 18 ipsecGlobalInAuthFails
            'ipsec_global_traffic_out',		# 19 ipsecGlobalOutOctets
            'ipsec_global_drops_out',	    # 20 ipsecGlobalOutDrops
            'ipsec_global_auth_fails_out',	# 21 ipsecGlobalOutAuthFails
        )

        errorIndication, errorStatus, errorIndex, snmpDataInt = cmdgen.CommandGenerator().nextCmd(
                cmdgen.CommunityData('agent', options.community, 0),
                cmdgen.UdpTransportTarget((target_host, options.snmpport), timeout=3),
                (1, 3, 6, 1, 2, 1, 31, 1, 1, 1, 1),             # 0 ifDescr
                (1, 3, 6, 1, 2, 1, 2, 2, 1, 10),                # 1 ifInOctets
                (1, 3, 6, 1, 2, 1, 2, 2, 1, 16),                # 2 ifOutOctets
                (1, 3, 6, 1, 2, 1, 2, 2, 1, 13),                # 3 ifInDiscarded
                (1, 3, 6, 1, 2, 1, 2, 2, 1, 19),                # 4 ifOutDiscarded
                (1, 3, 6, 1, 2, 1, 2, 2, 1, 14),                # 5 ifInError
                (1, 3, 6, 1, 2, 1, 2, 2, 1, 20),                # 6 ifOutError
            )

        if errorIndication:
            print(errorIndication)
            break
        elif errorStatus:
            print(errorStatus)
            break

        errorIndication, errorStatus, errorIndex, snmpDataConn = cmdgen.CommandGenerator().nextCmd(
                cmdgen.CommunityData('agent', options.community, 0),
                cmdgen.UdpTransportTarget((target_host, options.snmpport), timeout=3),
                (1, 3, 6, 1, 4, 1, 9, 9, 491, 1, 1, 1, 6),      # 0 connActive
                (1, 3, 6, 1, 4, 1, 9, 9, 491, 1, 1, 1, 10),     # 1 connRate1m
                (1, 3, 6, 1, 4, 1, 9, 9, 491, 1, 1, 1, 11),     # 2 connRate5m
            )

        if errorIndication:
            print(errorIndication)
            break
        elif errorStatus:
            print(errorStatus)
            break

        errorIndication, errorStatus, errorIndex, snmpData = cmdgen.CommandGenerator().nextCmd(
                cmdgen.CommunityData('agent', options.community, 0),
                cmdgen.UdpTransportTarget((target_host, options.snmpport), timeout=3),
                (1, 3, 6, 1, 2, 1, 1, 5),                       # 0 sysName
                (1, 3, 6, 1, 4, 1, 9, 9, 109, 1, 1, 1, 1, 4),   # 1 cpmCPUTotal1min
                (1, 3, 6, 1, 4, 1, 9, 9, 48, 1, 1, 1, 5),       # 2 ramUsed
                (1, 3, 6, 1, 4, 1, 9, 9, 48, 1, 1, 1, 6),       # 3 ramFree
                (1, 3, 6, 1, 2, 1, 11, 1),                      # 4 snmpInOctets
                (1, 3, 6, 1, 2, 1, 11, 2),                      # 5 snmpOutOctets
                (1, 3, 6, 1, 2, 1, 11, 3),                      # 6 snmpBadVersion
                (1, 3, 6, 1, 2, 1, 11, 4),                      # 7 snmpBadCommunityName
                (1, 3, 6, 1, 2, 1, 11, 5),                      # 8 snmpBadCommunityUse
                (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 2, 1, 1),      # 9 ikeActiveTunnels
                (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 2, 1, 3),      # 10 ikeGlobalInOctets
                (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 2, 1, 5),      # 11 ikeGlobalInDrops
                (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 2, 1, 11),     # 12 ikeGlobalOutOctets
                (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 2, 1, 13),     # 13 ikeGlobalOutDrops
                (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 2, 1, 23),     # 14 ikeGlobalAuthFails
                (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 3, 1, 1),      # 15 ipsecActiveTunnels
                (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 3, 1, 3),      # 16 ipsecGlobalInOctets
                (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 3, 1, 10),     # 17 ipsecGlobalInDrops
                (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 3, 1, 13),     # 18 ipsecGlobalInAuthFails
                (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 3, 1, 16),     # 19 ipsecGlobalOutOctets
                (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 3, 1, 23),     # 20 ipsecGlobalOutDrops
                (1, 3, 6, 1, 4, 1, 9, 9, 171, 1, 3, 1, 25),     # 21 ipsecGlobalOutAuthFails
            )

        if errorIndication:
            print(errorIndication)
            break
        elif errorStatus:
            print(errorStatus)
            break

        if options.custom_host_name:
          hostname = options.custom_host_name
        else:
          hostname = re.search(r'^([a-zA-Z0-9-]+).*', str(snmpData[0][0][1])).group(1)  # assigns and strips out the hostname

        for i in range(0, len(snmpDataInt)):    # Interfaces data loop
            for k in range(1, len(snmpDescInt)-1):
                data.append(("%s.%s.%s_%s" % (
                    options.custom_group_name,
                    hostname,
                    str(snmpDataInt[i][0][1]).replace('/', '_'),    # interface name; change / into _ to help grahite tree organisation
                    snmpDescInt[k]),
                    (
                        timestamp,
                        int(snmpDataInt[i][k][1])  # value
                    )))
            if (oldOctetsIn[i] > 0 and oldOctetsOut[i] > 0 and 
                int(snmpDataInt[i][1][1]) >= oldOctetsIn[i] and 
                int(snmpDataInt[i][2][1]) >= oldOctetsOut[i]):
                bwIn = ((int(snmpDataInt[i][1][1])-oldOctetsIn[i])*8)/options.delay   # Calculate input bandwith usage in bit/s
                bwOut = ((int(snmpDataInt[i][2][1])-oldOctetsOut[i])*8)/options.delay # Calculate output bandwith usage in bit/s
                data.append(("%s.%s.%s_%s" % (
                    options.custom_group_name,
                    hostname,
                    str(snmpDataInt[i][0][1]).replace('/', '_'),
                    'bandwidth_usage_in'),
                    (
                        timestamp,
                        int(bwIn)  # value
                    )))
                data.append(("%s.%s.%s_%s" % (
                    options.custom_group_name,
                    hostname,
                    str(snmpDataInt[i][0][1]).replace('/', '_'),
                    'bandwidth_usage_out'),
                    (
                        timestamp,
                        int(bwOut)  # value
                    )))
            oldOctetsIn[i] = int(snmpDataInt[i][1][1])
            oldOctetsOut[i] = int(snmpDataInt[i][2][1]) 
            
        for i in range(0, len(snmpDataConn[0])):    # Conn data loop
            data.append(("%s.%s.%s" % (
                options.custom_group_name,
                hostname,
                snmpDescConn[i]),
                (
                    timestamp,
                    int(snmpDataConn[0][i][1])  # value
                )))

        for i in range(1, len(snmpData[0])-1):    # Main data loop
            data.append(("%s.%s.%s" % (
                options.custom_group_name,
                hostname,
                snmpDesc[i]),
                (
                    timestamp,
                    int(snmpData[0][i][1])  # value
                )))

        if not (options.debug):
            # send gathered data to carbon server as a pickle packet
            payload = pickle.dumps(data)
            header = struct.pack("!L", len(payload))
            message = header + payload
            sock.sendall(message)
        else:
            pprint.pprint(data)

        sock.close()
        
        if (options.single):
            break
        
        time.sleep(options.delay)

if __name__ == '__main__':
    main()
