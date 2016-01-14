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

from h5json import Hdf5db
    

#
# Print usage and exit
#
def printUsage():
    print("usage: python set_acl.py -file <filename> [-path h5path] [+-}[crudep] [userid1, userid2, ...]")
    print("  options -v: verbose, print request and response codes from server")
    print("  options -file: name of file")
    print("  options -path: path to object (default as /)")
    print("  options userids: userid of acl to return")
    print(" ------------------------------------------------------------------------------")
    print("  Example - set 'tall.h5' default access to read only")
    print("       python setacl.py -file ../../data/test/tall.h5 +r-udep")
    print("  Example - get acl for 'tall.h5' dataset /g1/g1.1/dset1.1.1 to full access for user 123")
    print("        python setacl.py -file ../../data/test/tall.h5 -path /g1/g1.1/dset1.1.1 +crudep 123")
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
    perm_abvr = {'c':'create', 'r': 'read', 'u': 'update', 'd': 'delete', 'e': 'readACL', 'p':'updateACL'} 
    h5path = None
    filename = None
    userids = []
    add_list = []
    remove_list = []
    if len(sys.argv) == 1 or sys.argv[1] == "-h":
        printUsage();
        sys.exit(1)
    argn = 1 
    while argn < len(sys.argv):
        arg = sys.argv[argn]
        if arg == '-file':  
            filename = getNextArg(argn)
            argn += 2
        elif arg == '-path':
            h5path = getNextArg(argn)
            argn += 2
        elif arg[0] in ('+', '-'):
            to_list = None
            for ch in arg:
                if ch == '+':
                    to_list = add_list
                elif ch == '-':
                    to_list = remove_list
                elif ch in perm_abvr.keys():
                    to_list.append(perm_abvr[ch])
                else:
                    printUsage()
                    sys.exit(1)
            argn += 1
        else:
            # process userids
            try:
                userid = int(arg)
                userids.append(userid)
            except ValueError:
                print("Invalid userid:", userid)
                sys.exit(1)
            argn += 1            
      
    
    conflicts = list(set(add_list) & set(remove_list))
    
    if len(conflicts) > 0:
        print("permission: ", conflicts[0], " set for both add and remove")
        sys.exit(1)
     
    if filename is None:
        print("no filename specified")
        sys.exit(1)    
  
    if not isfile(filename):
        print(filename, "not found")
        sys.exit(1)
    if not h5py.is_hdf5(filename):
        print(filename, "not an hdf5 file")
        sys.exit(1)
    if h5path is None:
        h5path = '/'
    if len(userids) == 0:
        userids.append(0)
    
    fields = ('userid', 'create', 'read', 'update', 'delete', 'readACL', 'updateACL')    
    with Hdf5db(filename) as db:
        try:
            obj_uuid = db.getUUIDByPath(h5path)
        except KeyError:
            print("no object found at path:", h5path)
            sys.exit(1)
        print("%8s   %8s  %8s  %8s  %8s  %8s  %8s " % fields)
        for userid in userids:
            
            acl = db.getAclByObjAndUser(obj_uuid, userid)
            if acl is None and userid != 0:
                acl = db.getAclByObjAndUser(obj_uuid, 0)
            if acl is None:
                acl = db.getDefaultAcl()
            
            acl['userid'] = userid
            for field in add_list:
                acl[field] = True 
            for field in remove_list:
                acl[field] = False
                
            format_args = [userid]
            for field in fields:
                if field == 'userid':
                    continue
                format_args.append('Y' if acl[field] else 'N')
            print("%8s %8s  %8s  %8s  %8s  %8s  %8s " % tuple(format_args))
            
            db.setAcl(obj_uuid, acl)
            
    

main()

    
	
