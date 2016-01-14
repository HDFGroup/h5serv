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
    
import os.path as op
import hashlib
import logging
import h5py

from tornado.web import HTTPError

import config

def to_bytes(a_string):
    if type(a_string) is unicode:
        return a_string.encode('utf-8')
    else:
        return a_string
    

def encrypt_pwd(passwd):
    """
     One way password encryptyion
    """
    encrypted = hashlib.sha224(passwd).hexdigest()
    
    return to_bytes(encrypted)

"""
 Password util helper functions
"""


def getUserInfo(user_name):
    """
      getUserInfo: return user data
    """
     
    log = logging.getLogger("h5serv")
    userid = None

    if not user_name:
        return None

    log.info("get info for user")
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

    with h5py.File(filename, 'r') as f:
        if user_name not in f.attrs:
            return None

        data = f.attrs[user_name]
        return data


def getUserId(user_name):
    """
      getUserId: get id for given user name
    """
    data = getUserInfo(user_name)
    userid = None
    if data is not None:
        userid = data['userid']
    return userid


def getUserName(userid):
    """
      getUserName: return user name for given user id
      #todo: may need to be optimized to support large number of users

    """
    log = logging.getLogger("h5serv")

    log.info("get user name for userid: [" + str(userid) + "]")
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

    with h5py.File(filename, 'r') as f:
        for attr_name in f.attrs:
            attr = f.attrs[attr_name]
            if attr['userid'] == userid:
                return attr_name

    return None


def validateUserPassword(user_name, password):
    """
      validateUserPassword: verify user and password.
        throws exception if not valid
    """
    log = logging.getLogger("h5serv")

    if not user_name:
        log.info('validateUserPassword - null user')
        raise HTTPError(401, message="provide user name and password")
    if not password:
        log.info('isPasswordValid - null password')
        raise HTTPError(401, message="provide  password")
    data = getUserInfo(user_name)

    if data is None:
        log.info("user not found")
        raise HTTPError(401, message="provide user and password")

    if data['pwd'] == encrypt_pwd(password):
        log.info("user  password validated")
    else:
        log.info("user password is not valid")
        raise HTTPError(401, message="invalid user name/password")

    return
