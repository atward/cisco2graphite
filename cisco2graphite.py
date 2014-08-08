#!/usr/bin/env python
"""
Cisco to Graphite

Reads values from a Cisco over SNMP and ships them to carbon pickle receiver

Need more metrics? add more oids to metrics dict
"""

import pickle
import re
import struct
import time
from optparse import OptionParser
from socket import socket
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pprint import pprint


def getall_oid(target_host, community, snmpport, oid, index=True):
    errorIndication, errorStatus, errorIndex, values = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('agent', community, 0),
            cmdgen.UdpTransportTarget((target_host, snmpport)),
            oid)
    if index:
        # return {idx1: v1, idx2: v2}
        result = dict([(o[-1],v) for pair in values for o,v in pair])
    else:
        result = values
    #print(result)
    return result
def getone_oid(target_host, community, snmpport, oid):
    return getall_oid(target_host, community, snmpport, oid, index=False)[0][0][1]


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
    parser.add_option("-P", "--prefix", dest="prefix",
        help="carbon metric prefix",
        action="store", default="servers")
    parser.add_option("-d", "--debug", dest="debug",
        help="do not send to carbon",
        action="store_true", default=False)

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("you must specify target_host and carbon_host as a command line option!")

    # assign some sane variable names to command line arguments
    carbon_host = args[1]  # carbon server hostname
    target_host = args[0]  # carbon server hostname

    # try to establish connection with carbon server
    sock = socket()
    try:
        if not options.debug:
            sock.connect((carbon_host, options.port))
    except:
        print("Couldn't connect to %s on port %d, is carbon-agent.py running?"
              % (carbon_host, options.port))

    data = []
    timestamp = int(time.time())

    # helper
    _get = lambda oid: getall_oid(target_host, options.community, options.snmpport, oid)

    ifIndex = _get((1, 3, 6, 1, 2, 1, 2, 2, 1, 1))
    ifDescr = _get((1, 3, 6, 1, 2, 1, 31, 1, 1, 1, 1))
    metrics = {
        'ifSpeed'        : _get((1, 3, 6, 1, 2, 1, 2, 2, 1, 5)),
        'ifAdminStatus'  : { i: v==1  # 1: UP 2: DOWN
                                for i,v in _get((1, 3, 6, 1, 2, 1, 2, 2, 1, 7)).iteritems() },

        'ifInOctets'     : _get((1, 3, 6, 1, 2, 1, 2, 2, 1, 10)),
        'ifInDiscards'   : _get((1, 3, 6, 1, 2, 1, 2, 2, 1, 13)),
        'ifInErrors'     : _get((1, 3, 6, 1, 2, 1, 2, 2, 1, 14)),

        'ifOutOctets'    : _get((1, 3, 6, 1, 2, 1, 2, 2, 1, 16)),
        'ifOutDiscards'  : _get((1, 3, 6, 1, 2, 1, 2, 2, 1, 19)),
        'ifOutErrors'    : _get((1, 3, 6, 1, 2, 1, 2, 2, 1, 20)),
    }

    sysName = getone_oid(target_host, options.community, options.snmpport, (1, 3, 6, 1, 2, 1, 1, 5))
    hostname = re.search(r'^([a-zA-Z0-9-]+).*', str(sysName)).group(1)  # assigns and strips out the hostname

    for idx in ifIndex:
        desc = re.sub('[/.]','_',str(ifDescr[idx]))  # interface name; change / or . into _ to help grahite tree organisation
        for metric_name in metrics:
            try:
                # append value: ('prefix.hostname.ifDesc.ifMetric', (timestamp, value))
                data.append(("%s.%s.%s.%s" % (
                        options.prefix,
                        hostname,
                        desc,
                        metric_name
                    ),(
                        timestamp,
                        int(metrics[metric_name][idx])
                    )))
            except KeyError:
                pass

    # send gathered data to carbon server as a pickle packet
    payload = pickle.dumps(data)
    header = struct.pack("!L", len(payload))
    message = header + payload

    if options.debug:
        pprint(data)
    else:
        sock.sendall(message)
        sock.close()

if __name__ == '__main__':
    main()
