## ciscoasa2graphite
=================

Yet another graphite feeder. It gets SNMP data from Cisco ASA and ships 
them over to a Graphite server.

### Requirements:
- Python >=2.6.6
- pysnmp

### Command line parameters:
Usage: ciscoasa2graphite.py [options] target_host carbon_host

Options:
  -h, --help            show this help message and exit
  -c COMMUNITY, --community=COMMUNITY
                        snmp community name
  -s SNMPPORT, --snmpport=SNMPPORT
                        snmp target port
  -p PORT, --port=PORT  carbon server port
  -n CUSTOM_HOST_NAME, --custom-host-name=CUSTOM_HOST_NAME
                        custom host name to show in Graphite
  -g CUSTOM_GROUP_NAME, --custom-group-name=CUSTOM_GROUP_NAME
                        custom group name to show in Graphite
  -o, --single          run a single time and exit
  -d DELAY, --delay=DELAY
                        wait <delay> seconds between each connection
  --debug               do not send any data to Graphite, print the data to
                        the screen instead


### It collects the following OIDs:
1.3.6.1.2.1.31.1.1.1.1				ifDescr
1.3.6.1.2.1.2.2.1.10				ifInOctets
1.3.6.1.2.1.2.2.1.16				ifOutOctets
1.3.6.1.2.1.2.2.1.13				ifInDiscarded
1.3.6.1.2.1.2.2.1.19				ifOutDiscarded
1.3.6.1.2.1.2.2.1.14				ifInError
1.3.6.1.2.1.2.2.1.20				ifOutError
1.3.6.1.4.1.9.9.491.1.1.1.6			connActive
1.3.6.1.4.1.9.9.491.1.1.1.10		connRate1m
1.3.6.1.4.1.9.9.491.1.1.1.11		connRate5m
1.3.6.1.2.1.1.5                     sysName
1.3.6.1.4.1.9.9.109.1.1.1.1.4		cpmCPUTotal1min
1.3.6.1.4.1.9.9.48.1.1.1.5			ramUsed
1.3.6.1.4.1.9.9.48.1.1.1.6			ramFree
1.3.6.1.2.1.11.1                    snmpInOctets
1.3.6.1.2.1.11.2                    snmpOutOctets
1.3.6.1.2.1.11.3                    snmpBadVersion
1.3.6.1.2.1.11.4                    snmpBadCommunityName
1.3.6.1.2.1.11.5                    snmpBadCommunityUse
1.3.6.1.4.1.9.9.171.1.2.1.1			ikeActiveTunnels
1.3.6.1.4.1.9.9.171.1.2.1.3			ikeGlobalInOctets
1.3.6.1.4.1.9.9.171.1.2.1.5			ikeGlobalInDrops
1.3.6.1.4.1.9.9.171.1.2.1.11		ikeGlobalOutOctets
1.3.6.1.4.1.9.9.171.1.2.1.13		ikeGlobalOutDrops
1.3.6.1.4.1.9.9.171.1.2.1.23		ikeGlobalAuthFails
1.3.6.1.4.1.9.9.171.1.3.1.1			ipsecActiveTunnels
1.3.6.1.4.1.9.9.171.1.3.1.3			ipsecGlobalInOctets
1.3.6.1.4.1.9.9.171.1.3.1.10		ipsecGlobalInDrops
1.3.6.1.4.1.9.9.171.1.3.1.13		ipsecGlobalInAuthFails
1.3.6.1.4.1.9.9.171.1.3.1.16		ipsecGlobalOutOctets
1.3.6.1.4.1.9.9.171.1.3.1.23		ipsecGlobalOutDrops
1.3.6.1.4.1.9.9.171.1.3.1.25		ipsecGlobalOutAuthFails

And also provides custom metrics for bandwidth usage of 
each interface, calculated from the input and output octets.

