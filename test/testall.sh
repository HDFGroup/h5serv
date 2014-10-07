#!/bin/sh 
##############################################################################
# Copyright by The HDF Group.                                                #
# All rights reserved.                                                       #
#                                                                            #
# This file is part of H5Serv (HDF5 REST Server) Service, Libraries and      #
# Utilities.  The full HDF5 REST Server copyright notice, including       s   #
# terms governing use, modification, and redistribution, is contained in     #
# the file COPYING, which can be found at the root of the source code        #
# distribution tree.  If you do not have access to this file, you may        #
# request a copy from help@hdfgroup.org.                                     #
##############################################################################

#
# Run all h5serv tests
#
cd unit
python hdf5dbTest.py
cd ../integ
./setupdata.sh -f  # initialize data files
python roottest.py
python grouptest.py
python linktest.py
python datasettest.py
python valuetest.py
python attributetest.py
python datatypetest.py
# python searchtest.py
cd ..
echo "Done!"
 





