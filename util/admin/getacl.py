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
from os.path import isfile 
import json
import numpy as np
import h5py

sys.path.append('../../hdf5-json/lib')
from hdf5db import Hdf5db
import hdf5dtype 
   

#
# Print usage and exit
#
def printUsage():
    print "usage: python get_acl.py [-h] -file <filename> [-path h5path] [userid1, userid2, ...]"
    print "  options -v: verbose, print request and response codes from server"
    print "  options -filename: name of file"
    print "  options -path: path to object (default as /)"
    print "  options -userid: userid of acl to return"
    print " ------------------------------------------------------------------------------"
    print "  Example - get 'tall.h5' root acl:"
    print "       python get_acl.py ../../data/test/tall.h5"
    print "  Example - get acl for 'tall.h5', /g1/g1.1/dset1.1.1, user 123"
    print "        python get_acl.py ../../data/test/tall.h5 -path /g1/g1.1/dset1.1.1 -userid 123"
    sys.exit(); 
    
"""
  Get command line argument.
  Exit with usage message if not available
"""    
def getNextArg(argn):
    if (argn+1) == len(sys.argv):
        printUsage();
        sys.exit(-1)
    return sys.argv[argn+1]
               
def main():
    h5path = None
    filename = None
    req_userids = []
    if len(sys.argv) == 1 or sys.argv[1] == "-h":
        printUsage();
        sys.exit(0)
    argn = 1 
    while argn < len(sys.argv):
        arg = sys.argv[argn]
        if arg == '-file':  
            filename = getNextArg(argn)
            argn += 2
        elif arg == '-path':
            h5path = getNextArg(argn)
            argn += 2
        else:
            # process userids
            try:
                userid = int(arg)
                req_userids.append(userid)
            except ValueError:
                print "Invalid userid:", userid
                sys.exit(1)
            argn += 1 
            
            
    if not isfile(filename):
        print filename, "not found"
        sys.exit(1) 
    if not h5py.is_hdf5(filename):
        print filename, "not an hdf5 file"
        sys.exit(1)
        
    if h5path is None:
        h5path = '/'
            
    fields = ('userid', 'create', 'read', 'update', 'delete', 'readACL', 'updateACL')
    with Hdf5db(filename) as db:
        obj_uuid = db.getUUIDByPath(h5path)
        acl_dset = db.getAclDataset(obj_uuid)
        if acl_dset and acl_dset.shape[0] > 0:
            acls = {}
            items = acl_dset[...]
            for item in items:
                acls[item[0]] = item
                
            userids = acls.keys()
            userids.sort()  # sort to print by userid
         
            print "%8s   %8s  %8s  %8s  %8s  %8s  %8s " % fields
            for userid in userids:
                if len(req_userids) > 0 and userid not in req_userids:
                    continue
                acl = acls[userid]
                format_args = [userid]
                for field in ('create', 'read', 'update', 'delete', 'readACL', 'updateACL'):
                    format_args.append('Y' if acl[field] else 'N')
                print "%8s %8s  %8s  %8s  %8s  %8s  %8s " % tuple(format_args)
        else:
            print "no ACLs"
              
    

main()

    
	
