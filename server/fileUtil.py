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
import os
import os.path as op
from tornado.web import HTTPError

from h5py import is_hdf5
import config

"""
 File util helper functions
 (primarily from mapping files to domains and vice-versa)
""" 

def getFileModCreateTimes(filePath):
    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filePath)
    return (mtime, ctime)
    
def isIPAddress(s):
    """Return True if the string looks like an IP address:
        n.n.n.n where n is between 0 and 255 """
    parts = s.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        try:
            n = int(part)
            if n < 0 or n > 255:
                return False
        except ValueError:
            return False
    return True
        

def getFilePath(host_value):
    # logging.info('getFilePath[' + host_value + ']')
    #strip off port specifier (if present)
    npos = host_value.rfind(':')
    if npos > 0:
        host = host_value[:npos]
    else:
        host = host_value
    
    topdomain = config.get('domain')
    
    #check to see if this is an ip address 
    if isIPAddress(host):
        host = topdomain  # use topdomain
    
    if host.lower() == topdomain:
        return None  # not an exception, return .toc 
     
    if len(host) <= len(topdomain) or host[-len(topdomain):].lower() != topdomain:
        raise HTTPError(403, message='top-level domain is not valid')
        
      
    if host[-(len(topdomain) + 1)] != '.':
        # there needs to be a dot separator
        raise HTTPError(400, message='domain name is not valid')
    
    host = host[:-(len(topdomain)+1)]   # strip off top domain part
    
    if len(host) == 0 or host[0] == '.':
        print "invalid domain"
        # needs a least one character (which can't be '.')
        raise HTTPError(400, message='domain name is not valid')
        
    filePath = config.get('datapath')
    while len(host) > 0:
        if len(filePath) > 0 and filePath[len(filePath) - 1] != '/':
            filePath += '/'  # add a directory separator
        npos = host.rfind('.')
        if npos < 0:
            filePath += host
            host = ''
        elif npos == 0 or npos == len(host) - 1:
            raise HTTPError(400) # Bad syntax
        else:     
            filePath += host[(npos+1):]
            host = host[:npos]

    filePath += ".h5"   # add extension
    
    # logging.info('getFilePath[' + host + '] -> "' + filePath + '"')
    
    return filePath
        
    
def getDomain(filePath):
    # Get domain given a file path
    if filePath.endswith(".h5"):
        domain = op.basename(filePath)[:-3]
    elif filePath.endswith(".hdf5"):
        domain = op.basename(filePath)[:-5]
    else:
        domain = op.basename(filePath)
    dirname = op.dirname(filePath)
    while len(dirname) > 0 and not op.samefile(dirname, config.get('datapath')):
        domain += '.'
        domain += op.basename(dirname)
        dirname = op.dirname(dirname)
    domain += '.'
    domain += config.get('domain')
      
    return domain 
  

def verifyFile(filePath, writable=False):
    # logging.info("filePath: " + filePath)
    if not op.isfile(filePath):
        raise HTTPError(404)  # not found
    if not is_hdf5(filePath):
        # logging.warning('this is not a hdf5 file!')
        raise HTTPError(404)
    if writable and not os.access(filePath, os.W_OK):
        # logging.warning('attempting update of read-only file')
        raise HTTPError(403)

def makeDirs(filePath):
    # Make any directories along path as needed
    if len(filePath) == 0 or op.isdir(filePath):
        return
    # logging.info('makeDirs filePath: [' + filePath + ']')
    dirname = op.dirname(filePath)
    
    if len(dirname) >= len(filePath):
        #logging.warning('makeDirs - unexpected dirname')
        return
    makeDirs(dirname)  # recursive call
    #logging.info('mkdir("' + filePath + '")')
    os.mkdir(filePath)  # should succeed since parent directory is created  
