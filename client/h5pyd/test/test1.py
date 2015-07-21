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
import h5pyd

print "version:", h5pyd.version.version
f = h5pyd.File("tall.test.hdfgroup.org", "r")

print "filename,", f.filename
print "name:", f.name
print "uuid:", f.id.uuid
print "id:", f.id.id

g2 = f['g2']

print "g2 uuid:", g2.id.uuid
print "g2 name:", g2.name
print "g2 num elements:", len(g2)
print "g2: iter.."
for x in g2:
    print x
   
print "xyz in g2", ('xyz' in g2)
print "dset2.1 in g2", ('dset2.1' in g2)

dset21 = g2['dset2.1']
print "dset21 uuid:", dset21.id.uuid
print "dset21 name:", dset21.name
print "dset21 dims:", dset21.shape
print "dset21 type:", dset21.dtype

dset111 = f['/g1/g1.1/dset1.1.1']
print "dset111 uuid:", dset111.id.uuid
print "dset111 name:", dset111.name
print "dset111 dims:", dset111.shape
print "dset111 type:", dset111.dtype

 
attr1 = dset111.attrs['attr1']
print "attr1:", attr1
print "num attrs of dset1.1.1:", len(dset111.attrs)
print "attr keys:", dset111.attrs.keys()

for attr in dset111.attrs:
    print 'name:', attr
    
