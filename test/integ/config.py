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
from h5serv.config import *

cfg = {
    'server': '127.0.0.1',
    'home_domain': 'home.hdfgroup.org',
    'port':   5000,
    'domain':   'test.hdfgroup.org',
    'hdf5_ext': '.h5',
    'home_dir': 'home'
}
update(cfg)
