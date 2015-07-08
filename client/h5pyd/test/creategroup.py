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

f = h5pyd.File("creategroup.client_test.hdfgroup.org", "w", endpoint="http://127.0.0.1:5000")

print "filename,", f.filename
print "name:", f.name
print "uuid:", f.id.uuid
print "id:", f.id.id

g1 = f.create_group('g1')

print "g1 uuid:", g1.id.uuid
print "g1 name:", g1.name

g2 = f.create_group('g2')

print "g2 uuid:", g2.id.uuid
print "g2 name:", g2.name

g2['hlink'] = g1

g21 = g2.create_group('g2.1')
print "g2 count:", len(g2)
print "delete g2.1..."
del g2['g2.1']
print "g2 count:", len(g2)
