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

f = h5pyd.File("tall.test.hdfgroup.org", "r", endpoint="http://127.0.0.1:5000")

print "filename,", f.filename
print "uuid:", f.id.uuid

dset112 = f['/g1/g1.1/dset1.1.2']
print "name:", dset112.name
print "type:", dset112.dtype
print "shape:", dset112.shape

nparr = dset112[...]

print "dset1.1.2:", nparr

print "dset1.1.2[3]:", dset112[3]

print "dset1.1.2[3:5]:", dset112[3:5]
rv = dset112[3:5]

dset111 =  f['/g1/g1.1/dset1.1.1']
print "name:", dset111.name
print "type:", dset111.dtype
print "shape:", dset111.shape
print "dset1.1.1:", dset111[...]
print "dset1.1.1[3]:", dset111[3]
print "dset1.1.1[3:4,3:4]:", dset111[3:4,3:4]
print "dset1.1.1[3,3]:", dset111[3,3]


