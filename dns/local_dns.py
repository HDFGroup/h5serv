##############################################################################
# Copyright by The HDF Group.                                                #
# All rights reserved.                                                       #
#                                                                            #
# This file is part of H5Serv (HDF5 REST Server) Service, Libraries and      #
# Utilities.  The full HDF5 REST Server copyright notice, including          #
# terms governing use, modification, and redistribution, is contained in     #
# the file COPYING, which can be found at the root of the source code        #
# distribution tree.  If you do not have access to this file, you may        #
# request a copy from help@hdfgroup.org.                                     #
##############################################################################

"""
This is a custom DNS server that can be used to view links to h5serv in a browser.

The server will will look at the request and if the domain matches the domain specified
by the service ('domain' key in ../server/config.py), will return 127.0.0.1 as the resolved
IP address.  Otherwise the request will be relayed to a different DNS server.  (8.8.8.8 by 
default).

Running: 
    Launch via: sudo python local_dns.py
    Admin privalages are needed since the server listens on port 53.
    Modify your Network settings to use 127.0.0.1 as a DNS server.
    E.g. on Mac OS X run: sudo networksetup -setdnsservers <network_name> 127.0.0.1
    
Note: Based on sample code from Twisted Matrix Laboratories
"""

from twisted.internet import reactor, defer
from twisted.names import client, dns, error, server
import config # symbolic link to "../server/config.py"


class DynamicResolver(object):
    """
    A resolver which calculates the answers to certain queries based on the
    query type and name.
    """
    _network = config.get('local_ip')
    _domain =  config.get('domain')

    def _dynamicResponseRequired(self, query):
        """
        Check the query to determine if a dynamic response is required.
        """
        if query.type == dns.A:
            if query.name.name.endswith(self._domain):
                return True

        return False


    def _doDynamicResponse(self, query):
        """
        Calculate the response to a query.
        """
        name = query.name.name
        answer = dns.RRHeader(
            name=name,
            payload=dns.Record_A(address=b'%s' % (self._network)))
        answers = [answer]
        authority = []
        additional = []
        return answers, authority, additional


    def query(self, query, timeout=None):
        """
        Check if the query should be answered dynamically, otherwise dispatch to
        the fallback resolver.
        """
        if self._dynamicResponseRequired(query):
            return defer.succeed(self._doDynamicResponse(query))
        else:
            return defer.fail(error.DomainError())

def main():
    """
    Run the server.
    """
    verbosity = 0
    _default_dns = config.get('default_dns')
    default_resolver = client.Resolver(servers=[(_default_dns, 53)])
    factory = server.DNSServerFactory(
        clients=[DynamicResolver(), default_resolver],
        verbose=verbosity
    )

    protocol = dns.DNSDatagramProtocol(controller=factory)
    factory.noisy = protocol.noisy = verbosity

    reactor.listenUDP(53, protocol)
    reactor.listenTCP(53, factory)

    reactor.run()

if __name__ == '__main__':
    raise SystemExit(main())
