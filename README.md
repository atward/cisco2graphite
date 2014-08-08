# cisco2graphite

Graphite feeder. Reads SNMP data from a Cisco and
ships them to Graphite's carbon pickle receiver

## Requirements
* python (>=2.7)
* pysnmp

## Usage

```
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
```
