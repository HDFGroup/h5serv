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
    
import requests
import config
import unittest
import json
import base64



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
Helper function - get auth string
"""
def getAuthString(user, password):   
    auth_string = user + ':' + password
    auth_string = auth_string.encode('utf-8')
    auth_string = base64.b64encode(auth_string)
    auth_string = b"Basic " + auth_string
    return auth_string
        

"""
Helper function - get root uuid  
""" 
def getRootUUID(domain, user=None, password=None):
    req = getEndpoint() + "/"
    headers = {'host': domain}
    if user is not None:
        # if user is supplied, add the auth header
        headers['Authorization'] = getAuthString(user, password)
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
    if type(name) != str or len(name) == 0:
        return None
    req = getEndpoint() + "/groups/" + parentUuid + "/links/" + name
    headers = {'host': domain}
    rsp = requests.get(req, headers=headers)
    tgtUuid = None
    if rsp.status_code == 200:
        rspJson = json.loads(rsp.text)
        target = rspJson['link']
        if target['class'] != 'H5L_TYPE_HARD':
            # soft/external links
            return None
        tgtUuid = target['id']

    return tgtUuid
"""
Helper function - get uuid for a given path
"""
def getUUIDByPath(domain, path, user=None, password=None):
    if path[0] != '/':
        raise KeyError("only abs paths") # only abs paths
            
    parent_uuid = getRootUUID(domain, user=user, password=password)  
     
    if path == '/':
        return parent_uuid
            
    headers = {'host': domain}
    if user is not None:
        # if user is supplied, add the auth header
        headers['Authorization'] = getAuthString(user, password)
            
    # make a fake tgt_json to represent 'link' to root group
    tgt_json = {'collection': "groups", 'class': "H5L_TYPE_HARD", 'id': parent_uuid }
    tgt_uuid = None
            
    names = path.split('/')         
                      
    for name in names:
        if not name: 
            continue
        if parent_uuid is None:
            raise KeyError("not found")
                 
        req = getEndpoint() + "/groups/" + parent_uuid + "/links/" + name
        rsp = requests.get(req, headers=headers)
        if rsp.status_code != 200:
            raise KeyError("not found")
        rsp_json = json.loads(rsp.text)    
        tgt_json = rsp_json['link']
            
        if tgt_json['class'] == 'H5L_TYPE_HARD':
            #print "hard link, collection:", link_json['collection']
            if tgt_json['collection'] == 'groups':
                parent_uuid = tgt_json['id']    
            else:
                parent_uuid = None
            tgt_uuid = tgt_json['id']
        else:
            raise KeyError("non-hard link")
    return tgt_uuid
            
"""
Helper function - create an anonymous group
"""    
def createGroup(domain):
    # test PUT_root
    req = getEndpoint() + "/groups"
    headers = {'host': domain}
    # create a new group
    rsp = requests.post(req, headers=headers)
    if rsp.status_code != 201:
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
    if rsp.status_code == 201:
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
    
"""
Helper function - convert name to url-friendly format
  Replaces all non-alphanumeric characters with '%<ascii_hex>'
"""
def nameEncode(name):
    out = []
    for ch in name:
        if ch.isalnum():
            out.append(ch)
        elif ch == ' ':
            out.append('+')
        else:
            hex = format(ord(ch), '02X')
            out.append('%' + hex)
    return ''.join(out)
         
    
            
