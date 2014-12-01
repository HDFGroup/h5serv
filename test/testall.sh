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
echo 'timeUtilTest'
python timeUtilTest.py
echo 'fileUtilTest'
python fileUtilTest.py
echo 'hdf5dtypeTest'
python hdf5dtypeTest.py
echo 'hdf5dbTest'
python hdf5dbTest.py


cd ../integ
./setupdata.sh -f  # initialize data files
echo 'rootest'
python roottest.py
echo 'grouptest'
python grouptest.py
echo 'linktest'
python linktest.py
echo 'datasettest'
python datasettest.py
echo 'valuetest'
python valuetest.py
echo 'attributetest'
python attributetest.py
echo 'datatypetest'
python datatypetest.py
echo 'shapetest'
python shapetest.py
echo 'datasettypetest'
python datasettypetest.py
echo 'spidertest'
python spidertest.py
cd ..
echo "Done!"
 





