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
import time
import hashlib
import logging
from pymongo import MongoClient

from tornado.web import HTTPError

import h5serv.config as config
from h5serv.passwordUtil import encrypt_pwd, to_string, to_bytes

cache_expire_time = 10.0  # ten seconds

class AuthClient(object):

    def __init__(self, mongouri):
        self.log = logging.getLogger("h5serv")
        self.log.info("AuthMongo class init(" + mongouri + ")")
        self.client = MongoClient(mongouri)
        db_name = config.get('mongo_dbname')
        self.db = self.client[db_name]
        self.username_cache = {}
        self.userid_cache = {}
         

    """
    Password util helper functions
    """


    def getUserInfo(self, user_name):
        """
        getUserInfo: return user data
        """
         
        userid = None

        if not user_name:
            return None
            
        self.log.info("Auth.getUserInfo: [" + to_string(user_name) + "]")
        
        if user_name in self.username_cache:
            item = self.username_cache[user_name]
            if item['timestamp'] - time.time() > cache_expire_time:
                self.log.info("Auth-cache expired")
                # delete the entry and re-fetch below
                del self.username_cache[user_name]
            else:
                self.log.info("Auth-got cache value")
                data = item['data']
                return data
                    
        # mongodb lookup
        self.log.info("mongo query")
        users = self.db["users"]
        data = users.find_one({"username": to_string(user_name)})
         
        if data is None:
            return None
            
        # add to cache 
        self.log.info("Auth - added to cache")
        item = {}
        timestamp = time.time()
        item['timestamp'] = timestamp
        item['data'] = data
        self.username_cache[user_name] = item
        item = {}
        item['timestamp'] = timestamp
        item['username'] = user_name
        userid = data['userid']
        self.userid_cache[userid] = item
        
        return data


    def getUserId(self, user_name):
        """
        getUserId: get id for given user name
        """
        self.log.info("Auth.getUserId: [" + user_name + "]")
        data = self.getUserInfo(user_name)
        userid = None
        if data is not None:
            userid = data['userid']
        return userid


    def getUserName(self, userid):
        """
        getUserName: return user name for given user id
        #todo: may need to be optimized to support large number of users
        """

        self.log.info("Auth.getUserName: [" + str(userid) + "]")
        
        if userid in self.userid_cache:
            item = self.userid_cache[userid]
            if item['timestamp'] - time.time() > cache_expire_time:
                # delete the entry and re-fetch below
                self.log.info("Auth-cache expired")
                del self.userid_cache[userid]
            else:
                self.log.info("Auth-got cache value")
                username = item['username']
                return to_string(username)
        
        
        # mongodb lookup
        users = self.db["users"]
        data = users.find_one({"userid": userid})
        if data is None:
            return None
        user_name = data["username"]
             
        self.log.info("Auth-add to cachecache")
        item = {}
        item['timestamp'] = time.time()
        item['username'] = user_name
        self.userid_cache[userid] = item
        
        return user_name


    def validateUserPassword(self, user_name, password):
        """
        validateUserPassword: verify user and password.
            throws exception if not valid
        """

        if not user_name:
            self.log.info('validateUserPassword - null user')
            raise HTTPError(401, message="provide user name and password")
        if not password:
            self.log.info('isPasswordValid - null password')
            raise HTTPError(401, message="provide  password")
        data = self.getUserInfo(user_name)

        if data is None:
            self.log.info("user not found")
            raise HTTPError(401, message="provide user and password")

        userid = None
        saved_password = to_bytes(data['password'])
        if saved_password == encrypt_pwd(password):
            self.log.info("user  password validated")
            userid = data['userid']
        else:
            self.log.info("user password is not valid")
            raise HTTPError(401, message="invalid user name/password")

        return userid
