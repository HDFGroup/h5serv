#!/usr/local/env python

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

from argparse import ArgumentParser
import os
import sys


unit_tests = ('timeUtilTest', 'fileUtilTest')
integ_tests = ('roottest', 'grouptest', 'dirtest', 'linktest', 'datasettest', 'valuetest',
    'attributetest', 'datatypetest', 'shapetest', 'datasettypetest', 'acltest')

#todo - add spidertest back
cwd = os.getcwd()
no_server = False

parser = ArgumentParser()
testKind = parser.add_mutually_exclusive_group()
testKind.add_argument('--unit', action='store_true', help='run only the unit tests')
testKind.add_argument('--integ', action='store_true', help='run only the integrity tests')
parser.add_argument('--failslow', action='store_true', help='keep running if a test fails, instead of terminating early')

args = vars(parser.parse_args())

if args['unit']:
    integ_tests = ()
elif args['integ']:
    unit_tests = ()

test_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(test_dir)

# Run all h5serv tests
# Run this script before running any integ tests

exit_code = None

os.chdir('unit')
for file_name in unit_tests:
    print(file_name)
    rc = os.system('python ' + file_name + '.py')
    if rc != 0:
        if args['failslow']:
            exit_code = 'Failed'
        else:
            os.chdir(cwd)
            sys.exit("Failed")
 
 
os.chdir('../integ')

if integ_tests:
    os.system("python ./setupdata.py -f")  # initialize data files
    
for file_name in integ_tests:
    print(file_name)
    rc = os.system('python ' + file_name + '.py')
    if rc != 0:
        if args['failslow']:
            exit_code = 'Failed'
        else:
            os.chdir(cwd)
            sys.exit("Failed")

log_file = "../../h5serv.log"
if exit_code:
    if os.name != 'nt' and os.path.isfile(log_file):
        # tail not available on windows
        print("server log...")
        os.system("tail -n 100 " + log_file)
    os.chdir(cwd)
    sys.exit(exit_code)
else:
    os.chdir(cwd)
    print("Done!")
