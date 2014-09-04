##############################################################################
# Copyright by The HDF Group.                                                #
# All rights reserved.                                                       #
#                                                                            #
# This file is part of H5Serv (HDF5 REST Server) Service, Libraries and      #
# Utilities.  The full HDF5 REST Server copyright notice, including         #
# terms governing use, modification, and redistribution, is contained in     #
# the file COPYING, which can be found at the root of the source code        #
# distribution tree.  If you do not have access to this file, you may        #
# request a copy from help@hdfgroup.org.                                     #
##############################################################################
import requests
import config
import unittest
import json

class LinkTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(LinkTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))
        
    def getRootId(self, domain):
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        rootUUID = rspJson["root"]
        self.assertTrue(len(rootUUID) == 36)
        return rootUUID
            
    def createGroup(self, domain):
        # test PUT_root
        req = self.endpoint + "/group/"
        headers = {'host': domain}
        # create a new group
        rsp = requests.post(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200) 
        rspJson = json.loads(rsp.text)
        id = rspJson["id"]
        self.assertTrue(len(id) == 36) 
        return id
       
    def testGet(self):
        domain = 'tall.' + config.get('domain')   
        rootUUID = self.getRootId(domain)
        
        req = self.endpoint + "/group/" + rootUUID + "/links"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        print rspJson
        self.failUnlessEqual(rsp.status_code, 200)
        
    def testPut(self):
        domain = 'tall.' + config.get('domain') 
        grpId = self.createGroup(domain)
        rootId = self.getRootId(domain)   
        name = 'g3'
        req = self.endpoint + "/group/" + rootId + "/links/" + name + "?id=" + grpId
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
         
    
       
if __name__ == '__main__':
    unittest.main()