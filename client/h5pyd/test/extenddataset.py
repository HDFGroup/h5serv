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
import h5pyd as h5pyd

primes = [2, 3, 5, 7, 11, 13, 17, 19]

f = h5pyd.File("extenddataset.client_test.hdfgroup.org", "w", endpoint="http://127.0.0.1:5000")

print "filename,", f.filename
print "name:", f.name
print "uuid:", f.id.id
 
print "create dataset"
 
 
dset = f.create_dataset('ints', (1,len(primes)), maxshape=(None, len(primes)), dtype='i8')

print "name:", dset.name
print "uuid:", dset.id.id
print "shape:", dset.shape
print "dset.type:", dset.dtype
print "dset.maxshape:", dset.maxshape

print "writing data..."
dset[0:,:] = primes
print "values:", dset[...]

f.close()
 

 