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
import math

f = h5pyd.File("createcompound.client_test.hdfgroup.org", "w")

count = 2

print "filename,", f.filename
print "name:", f.name
print "id:", f.id.id
 
print "create dataset"
print "create compound dataset"
dt = np.dtype([('real', np.float), ('img', np.float)])
 
dset = f.create_dataset('complex', (count,), dtype=dt)
  
print "name:", dset.name
print "id:", dset.id.id
print "shape:", dset.shape
print "dset.type:", dset.dtype
print "dset.maxshape:", dset.maxshape

print "writing data..."
elem = dset[0]
for i in range(count):
    theta = (4.0 * math.pi)*(float(i)/float(count))
    print theta
    elem['real'] = math.cos(theta)
    elem['img'] = math.sin(theta)
    dset[i] = elem
    
#print "values:", dset[...]
#body: {'start': [0], 'step': [1], 'stop': [1], 'value': (1.0, 0.0)}
