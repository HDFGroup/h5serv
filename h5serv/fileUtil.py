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
"""File util helper functions (primarily from mapping files to domains
and vice-versa).

"""

import os
import os.path as op
import logging

from tornado.web import HTTPError

from h5py import is_hdf5
import h5serv.config as config
from h5serv.passwordUtil import getAuthClient

def getFileModCreateTimes(filePath):
    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filePath)
    return (mtime, ctime)


def isIPAddress(s):
    """Return True if the string looks like an IP address:
        n.n.n.n where n is between 0 and 255 """
    
    parts = s.split('.')
    
    if len(parts) == 1:
        # treat as IP address for names like "localhost" or other one-word names
        # that may get mapped to IP address via /etc/hosts entries
        return True
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
    
# Convert windows style path names to posxipaths
#
# todo: any edge cases this doesn't handle?
def posixpath(filepath):
     
     if os.name == 'nt':
        pp = filepath.replace('\\', '/')
     else:
        pp = filepath
     return pp
     
# Join to pathnames and convert to posix style
#
# todo: any edge cases this doesn't handle?
def join(path, paths):
     pp = op.join(path, paths)
     if os.name == 'nt':
        pp = posixpath(pp)
      
     return pp

def getFilePath(host_value, auth=None):
    # logging.info('getFilePath[' + host_value + ']')
    # strip off port specifier (if present)
    npos = host_value.rfind(':')
    if npos > 0:
        host = host_value[:npos]
    else:
        host = host_value

    topdomain = config.get('domain')
    
    # check to see if this is an ip address
    if isIPAddress(host):
        host = topdomain  # use topdomain

    if host.lower() == topdomain:
        # if host is the same as topdomain, return toc path
        # filePath = getTocFilePath()
        filePath = config.get('datapath')
        filePath = join(filePath, config.get('toc_name') )
        return filePath
    print("host:", host, "topdomain:", topdomain)
    if len(host) <= len(topdomain) or host[-len(topdomain):].lower() != topdomain:
        msg = "top-level domain is not valid"
        print(msg)
        raise HTTPError(403, message=msg)

    if host[-(len(topdomain) + 1)] != '.':
        # there needs to be a dot separator
        raise HTTPError(400, message='domain name is not valid')

    host = host[:-(len(topdomain)+1)]   # strip off top domain part

    if len(host) == 0 or host[0] == '.' or host[-1] == '.':
        # needs a least one character (which can't be '.', or have '.' as first or last char)
        raise HTTPError(400, message='domain name is not valid')

    dns_path = host.split('.')
    dns_path.reverse()  # flip to filesystem ordering
    filePath = config.get('datapath')
    num_parts = 0
    for field in dns_path:      
        if len(field) == 0:   
            raise HTTPError(400)  # Bad syntax
        
        filePath = join(filePath, field)
        num_parts += 1

    # check to see if this is the user's home domain
    if num_parts == 2 and dns_path[0] == config.get('home_dir'):
        if auth is None:
            auth = getAuthClient
        user_info = auth.getUserInfo(dns_path[1])
        if user_info is None:
            raise HTTPError(404)  # not found
        makeDirs(filePath)  # add user directory if it doesn't exist
        filePath = join(filePath, config.get('toc_name') )
    else:    
        filePath += config.get('hdf5_ext')   # add extension
     
    #print('getFilePath[' + host + '] -> "' + filePath + '"')

    return filePath

# 
# Return filepath to TOC file - either the public toc file or the per
# user TOC file (if the dns path includes the "home" directory).
# For the later, method will throw 404 if the user is not registered.
#    
def getTocFilePathForDomain(host_value, auth=None):
    """ Return toc file path for given domain value.
        Will return path "../data/.toc.h5" for public domains or
        "../data/home/<user>/.toc.h5" for user domains.
    """
    # logging.info('getFilePath[' + host_value + ']')
    # strip off port specifier (if present)
    npos = host_value.rfind(':')
    if npos > 0:
        host = host_value[:npos]
    else:
        host = host_value

    topdomain = config.get('domain')

    # check to see if this is an ip address
    if isIPAddress(host):
        host = topdomain  # use topdomain

    if host.lower() == topdomain:
        # if host is the same as topdomain, return toc path
        # filePath = getTocFilePath()
        filePath = config.get('datapath')
        filePath = join(filePath, config.get('toc_name') )
        return filePath

    if len(host) <= len(topdomain) or host[-len(topdomain):].lower() != topdomain:
        host = topdomain  # use topdomain
    else:
        if host[-(len(topdomain) + 1)] != '.':
            # there needs to be a dot separator
            raise HTTPError(400, message='domain name is not valid')

        host = host[:-(len(topdomain)+1)]   # strip off top domain part

        if len(host) == 0 or host[0] == '.' or host[-1] == '.':
            # needs a least one character (which can't be '.', or have '.' as first or last char)
            raise HTTPError(400, message='domain name is not valid')

    dns_path = host.split('.')
    dns_path.reverse()  # flip to filesystem ordering
    filePath = config.get('datapath')
    
    if dns_path[0] == config.get('home_dir'):
        filePath = join(filePath, config.get('home_dir'))
        filePath = join(filePath, dns_path[1])
        if auth is None:
            auth = getAuthClient()
        user_info = auth.getUserInfo(dns_path[1])
        if user_info is None:
            raise HTTPError(404)  # not found
        makeDirs(filePath)  # add user directory if it doesn't exist
        filePath = join(filePath, config.get('toc_name'))
        #print("return user toc filepath")
    else:
        # not home dir, just return top-level toc
        filePath = join(filePath, config.get('toc_name'))
        #print("return default toc filepath")

    return filePath

#
# If the filePath passed references the user's home directory, return a path relative 
# to the base location of the user's toc file.  Otherwise returns the path relative to
# the base data directory
#
def getUserFilePath(file_path):
    data_path = config.get('datapath')
    file_path = file_path[len(data_path):]  # strip off base data path
    if len(file_path) > 1 and file_path[0] == '/':
        file_path = file_path[1:]  # don't include first slash if preseent- messes up the split
    path_names = file_path.split('/')
     
    if path_names[0] == config.get('home_dir') and len(path_names) > 1:
        # return a path relative to user's base dir
        file_path = '/'  
        path_names = path_names[2:]  # skip home, userid
        for path_name in path_names:
            file_path = op.join(file_path, path_name)
        
    return file_path
 
def getDomain(file_path, base_domain=None):
    # Get domain given a file path
    
    data_path = op.normpath(config.get('datapath'))  # base path for data directory
    data_path = posixpath(data_path)
    file_path = posixpath(file_path)
    hdf5_ext = config.get("hdf5_ext")
    if op.isabs(file_path):
        # compare with absolute path if we're given an absolute path
        data_path = posixpath(op.abspath(data_path))
    
    if file_path == data_path:
        return config.get('domain')
            
    if file_path.endswith(hdf5_ext):
        domain = op.basename(file_path)[:-(len(hdf5_ext))]
    else:
        domain = op.basename(file_path)

    # replace dots with %2E in basename
    domain = domain.replace('.', '%2E')

    dirname = op.dirname(file_path)
    
    while len(dirname) > 1 and dirname != data_path:
        domain += '.'
        domain += op.basename(dirname)
        if len(op.dirname(dirname)) >= len(dirname):
            break
        dirname = op.dirname(dirname)
     
    domain += '.'
    if base_domain:
        domain += base_domain
    else:
        domain += config.get('domain')

    return domain

def verifyFile(filePath, writable=False):
    """ verify given file exists and is an HDF5 file
    """
    log = logging.getLogger("h5serv")
    log.info("verifyFile('" + filePath + "', " + str(writable) + ")")
    if not op.isfile(filePath):
        log.info("not a file")
        raise HTTPError(404)  # not found
    if not is_hdf5(filePath):
        log.info('this is not a hdf5 file!')
        raise HTTPError(404)
    if writable and not os.access(filePath, os.W_OK):
        log.warning('attempting update of read-only file')
        raise HTTPError(403)
        
def isFile(filePath):
    """ verify given file exists and is an HDF5 file
    """
    if not op.isfile(filePath):
        return False
    if not is_hdf5(filePath):
        # logging.warning('this is not a hdf5 file!')
        return False
    return True
     


def makeDirs(filePath):
    # Make any directories along path as needed
    if len(filePath) == 0 or op.isdir(filePath):
        return
    dirname = op.dirname(filePath)

    if len(dirname) >= len(filePath):
        return
    makeDirs(dirname)  # recursive call
    os.mkdir(filePath)  # should succeed since parent directory is created
