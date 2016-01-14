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

import os

unit_tests = ('timeUtilTest', 'fileUtilTest')
integ_tests = ('roottest', 'grouptest', 'dirtest', 'linktest', 'datasettest', 'valuetest',
    'attributetest', 'datatypetest', 'shapetest', 'datasettypetest', 'spidertest', 'acltest')
#
# Run all h5serv tests
# Run this script before running any integ tests
#
os.chdir('unit')
for file_name in unit_tests:
    print(file_name)
    os.system('python ' + file_name + '.py')
  
os.chdir('../integ')

os.system("python ./setupdata.py -f")  # initialize data files
for file_name in integ_tests:
    print(file_name)
    os.system('python ' + file_name + '.py')
os.chdir('..') 
print("Done!")
 





