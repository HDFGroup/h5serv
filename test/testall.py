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
import sys


unit_tests = ('timeUtilTest', 'fileUtilTest')
integ_tests = ('roottest', 'grouptest', 'dirtest', 'linktest', 'datasettest', 'valuetest',
    'attributetest', 'datatypetest', 'shapetest', 'datasettypetest', 'spidertest', 'acltest')

cwd = os.getcwd()
no_server = False
print(len(sys.argv))
if len(sys.argv) > 1:
    if sys.argv[1] == '--unit':
        integ_tests = () # skip integ tests
    elif sys.argv[1] == '--integ':
        unit_tests = () # skip unit tests
    
        

test_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

os.chdir(test_dir)

# Run all h5serv tests
# Run this script before running any integ tests
#
os.chdir('unit')
for file_name in unit_tests:
    print(file_name)
    rc = os.system('python ' + file_name + '.py')
    if rc != 0:
        os.chdir(cwd)
        sys.exit("Failed")
 
 
os.chdir('../integ')

if integ_tests:
    os.system("python ./setupdata.py -f")  # initialize data files
    
for file_name in integ_tests:
    print(file_name)
    rc = os.system('python ' + file_name + '.py')
    if rc != 0:
        print("server log...")
        os.system("tail -n 100 ../../log/h5serv.log")
        os.chdir(cwd)
        sys.exit("Failed")
    
os.chdir(cwd)
print("Done!")
 





