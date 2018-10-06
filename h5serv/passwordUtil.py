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

import six

if six.PY3:
    unicode = str    
 
import hashlib
import logging
import h5serv.config as config
 

"""
 Password util helper functions
"""

    
def to_string(data):
    if six.PY3:           
        if type(data) is bytes:
            return data.decode('utf-8')
        else:
            return data
    else:
        return data
        
def to_bytes(data):
    if six.PY3:
        if type(data) is unicode:
            return data.encode('utf-8')
        else:
            return data
    else:
        return data
        
def encrypt_pwd(passwd):
    """
     One way password encryptyion
    """
    encrypted = hashlib.sha224(passwd).hexdigest()
    
    return to_bytes(encrypted)
    
def getAuthClient():
    log = logging.getLogger("h5serv")
    log.info("getAuthClient")
    password_uri = config.get("password_uri")
    log.info("password_uri:" + password_uri)
     
    auth = None
    if password_uri.startswith("mongo"):
        # use mongodb user db
        from h5serv.authMongo import AuthClient
        auth = AuthClient(password_uri)
    else:
        # use HDF5 file-based user db
        from h5serv.authFile import AuthClient
        auth = AuthClient(password_uri)
        
    return auth
