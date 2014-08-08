cisco2graphite
==============

Yet another graphite feed, this time it gets (interesting, for now just
interface stats and CPU usage) SNMP data from a Cisco and ships them over to
target Graphite installation.

Requires pysnmp.  Best to be run from cron.

$ ./cisco2graphite.py --help
Usage: cisco2graphite.py [options] target_host carbon_host

Options:
  -h, --help            show this help message and exit
  -c COMMUNITY, --community=COMMUNITY
                        snmp community name
  -s SNMPPORT, --snmpport=SNMPPORT
                        snmp target port
  -p PORT, --port=PORT  carbon server port
  -P PREFIX, --prefix=PREFIX
                        carbon metric prefix
  -d, --debug           do not send to carbon
