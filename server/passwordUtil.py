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
import hashlib
import logging
import h5py
import numpy as np
 

from tornado.web import HTTPError

 
import config

"""
 One way password encryptyion
"""
def encrypt_pwd(passwd):
    encrypted = hashlib.sha224(passwd).hexdigest()
    return encrypted 

"""
 Password util helper functions
""" 

def isPasswordValid(userid, password):
    log = logging.getLogger("h5serv")
    
    if not userid:
        log.info('isPasswordValid - null user')
        return False
    if not password:
        log.info('isPasswordValid - null password')
        return False
    log.info("validate password for user: [" + userid + "]")
    filename = config.get('password_file')
    if not filename:
        log.error("no config for password_file")
        raise HTTPError(500, message="bad configuration")
    # verify file exists and is writable
    if not op.isfile(filename):
        log.error("password file is missing")
        raise HTTPError(500, message="bad configuration")
                
    if not h5py.is_hdf5(filename):
        log.error("password file is invalid")
        raise HTTPError(500, message="bad configuration")
          
    f = h5py.File(filename, 'r')
    if 'user_type' not in f:
        log.error("password file is missing user_type")
        raise HTTPError(500, message="bad configuration")
         
    user_type = f['user_type']
    
    isValid = False
        
    if userid not in f.attrs:
        log.info("user: [" + userid + "] not found")
    else:
        data = f.attrs[userid]
        if data['pwd'] == encrypt_pwd(password):
            log.info("user: [" + userid + "] password validated")
            isValid = True
        else:
            log.info("user: [" + userid + "] password is not valid")
    f.close()
    return isValid
    
    
 