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
import requests
import config
import unittest
import json

"""
    Helper function - get endpoint we'll send http requests to 
    """ 
def getEndpoint():
    endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))
    return endpoint

"""
Helper function - return true if the parameter looks like a UUID
"""
def validateId(id):
    if type(id) != str and type(id) != unicode: 
        # should be a string
        return False
    if len(id) != 36:
        # id's returned by uuid.uuid1() are always 36 chars long
        return False
    return True
    

"""
Helper function - get root uuid  
""" 
def getRootUUID(domain):
    req = getEndpoint() + "/"
    headers = {'host': domain}
    rsp = requests.get(req, headers=headers)
    rootUUID = None
    if rsp.status_code == 200:
        rspJson = json.loads(rsp.text)
        rootUUID = rspJson["root"]
    return rootUUID
           
"""
Helper function - get uuid given parent group uuid and link name
"""
def getUUID(domain, parentUuid, name):
    req = getEndpoint() + "/groups/" + parentUuid + "/links"
    headers = {'host': domain}
    rsp = requests.get(req, headers=headers)
    tgtUuid = None
    if rsp.status_code == 200:
        rspJson = json.loads(rsp.text)
        links = rspJson['links']
        tgtUuid = None
        for link in links:
            if link['name'] == name:
                tgtUuid = link['id']
                break
    return tgtUuid
"""
Helper function - create an anonymous group
"""    
def createGroup(domain):
    # test PUT_root
    req = getEndpoint() + "/groups/"
    headers = {'host': domain}
    # create a new group
    rsp = requests.post(req, headers=headers)
    if rsp.status_code != 200:
        return None
    rspJson = json.loads(rsp.text)
    id = rspJson["id"] 
    return id
        
"""
Helper function - link given object/name
"""
def linkObject(domain, objUuid, name, parentUuid=None):
    if parentUuid == None:
        # use root as parent if not specified
        parentUuid = getRootUUID(domain)
    req = getEndpoint() + "/groups/" + parentUuid + "/links/" + name 
    payload = {"id": objUuid}
    headers = {'host': domain}
    rsp = requests.put(req, data=json.dumps(payload), headers=headers)
    if rsp.status_code == 200:
        return True
    else: 
        return False
        
"""
Helper function - return data from dataset
"""
def readDataset(domain, dsetUuid):
    req = getEndpoint() + "/datasets/" + dsetUuid + "/value"
    headers = {'host': domain}
    rsp = requests.get(req, headers=headers)
    if rsp.status_code != 200:
        return None
    rspJson = json.loads(rsp.text)
    data = rspJson['value']
    return data
         
    
            
