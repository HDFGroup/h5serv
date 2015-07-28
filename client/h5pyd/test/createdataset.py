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
import numpy as np
import h5pyd

f = h5pyd.File("createdataset.client_test.hdfgroup.org", "w", endpoint="http://127.0.0.1:5000")
"""
print "filename,", f.filename
print "name:", f.name
print "uuid:", f.id.uuid
 
print "create dataset"
 
dset = f.create_dataset('ints', (10,), dtype='i8')

print "name:", dset.name
print "uuid:", dset.id.uuid
print "shape:", dset.shape
print "dset.type:", dset.dtype
print "dset.maxshape:", dset.maxshape

print "writing data..."
dset[...] = range(10)
print "values:", dset[...]

print "write selection..."
dset[2:5] = [20,30,40]
print "values:", dset[...]

"""
data = np.arange(13).astype('f')
print "input data:", data[...]
dset = f.create_dataset('x', data=data)  
print "output data:", dset[...]
print "[1:7:3]:", dset[1:7:3]
dset[3:6] = (77.7, 88.8, 99.9)
print "output data:", dset[...]

 