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
import os
import sys

cfg = {
    'port':   5000,
    'debug':  True,
    'datapath': '../data/',
    'domain':  'hdfgroup.org',
    'hdf5_ext': '.h5',
    'toc_name': '.toc.h5',
    'local_ip': '127.0.0.1',  # used by lcoal_dns.py
    'default_dns': '8.8.8.8',  # used by local_dns.py
    'ssl_port': 5050,
    'ssl_cert': '',  # add relative path to cert for SSL
    'ssl_key':  '',  # add relative path to cert key for SSL
    'ssl_cert_pwd': 'tampopo'
}
   
def get(x):     
    # see if there is a command-line override   
    option = '--'+x+'='
    for i in range(1, len(sys.argv)):
        #print i, sys.argv[i]
        if sys.argv[i].startswith(option):
            # found an override
            arg = sys.argv[i]
            return arg[len(option):]  # return text after option string
    # see if there are an environment variable override
    if x.upper() in os.environ:
        return os.environ[x.upper()]
    # no command line override, just return the cfg value        
    return cfg[x]

  
  
