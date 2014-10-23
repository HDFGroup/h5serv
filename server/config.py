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
cfg = {
    'port':   5000,
    'debug':  True,
    'datapath': '../data/',
    'domain': 'test.hdf.io',
    'hdf5_ext': '.h5',
    'local_ip': '127.0.0.1',
    'default_dns': '8.8.8.8'  # used by local_dns.py
}
   
def get(x):     
    return cfg[x]

  
  
