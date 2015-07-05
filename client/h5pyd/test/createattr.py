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
import sys
sys.path.append('..')
import h5pyd

f = h5pyd.File("createattr.client_test.hdfgroup.org", "w", endpoint="http://127.0.0.1:5000")

print "filename,", f.filename
print "name:", f.name
print "uuid:", f.id.uuid
 
print "create attribute"

#f.attrs['a1'] = 42  # fix

g1 = f.create_group('g1')
 
g1.attrs['a1'] = 42 
g1.attrs['a2'] = ['hello', 'goodbye']
 