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
import logging

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
        logging.info("LinkTest.testGet")
        domain = 'tall.' + config.get('domain')   
        rootUUID = self.getRootId(domain)     
        req = self.endpoint + "/group/" + rootUUID + "/links"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.failUnlessEqual(rsp.status_code, 200)
        
    def testPut(self):
        logging.info("LinkTest.testPut")
        domain = 'tall.' + config.get('domain') 
        grpId = self.createGroup(domain)
        rootId = self.getRootId(domain)   
        name = 'g3'
        req = self.endpoint + "/group/" + rootId + "/links/" + name 
        payload = {"id": grpId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        # make a request second time (verify idempotent)
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        
    def testPutBadReqId(self):
        logging.info("LinkTest.testPutBadReqId")
        domain = 'tall.' + config.get('domain') 
        grpId = self.createGroup(domain)
        badReqId  = 'b2771194-347f-11e4-bb67-3c15c2da029e' # doesn't exist in tall.h5
        name = 'g3'
        req = self.endpoint + "/group/" + badReqId + "/links/" + name 
        payload = {"id": grpId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 404)
        
    def testPutBadLinkId(self):
        logging.info("LinkTest.testPutBadLinkId")
        domain = 'tall.' + config.get('domain') 
        grpId = self.createGroup(domain)
        rootId = self.getRootId(domain)  
        badLinkId  = 'b2771194-347f-11e4-bb67-3c15c2da029e' # doesn't exist in tall.h5
        name = 'g3'
        req = self.endpoint + "/group/" + rootId + "/links/" + name 
        payload = {"id": badLinkId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 404)
        
    def testPutNoName(self):
        logging.info("LinkTest.testPutNoName")
        domain = 'tall.' + config.get('domain') 
        grpId = self.createGroup(domain)
        rootId = self.getRootId(domain)   
        req = self.endpoint + "/group/" + rootId + "/links/"  
        payload = {"id": grpId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)
        
    def testPutBadName(self):
        logging.info("LinkTest.testPutBadName")
        domain = 'tall.' + config.get('domain') 
        grpId = self.createGroup(domain)
        rootId = self.getRootId(domain)   
        name = 'bad/name'  # forward slash not allowed
        req = self.endpoint + "/group/" + rootId + "/links/" + name 
        payload = {"id": grpId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)
        
    def testPutSoftLink(self):
        logging.info("LinkTest.testPutSoftLink")
        domain = 'tall.' + config.get('domain') 
        grpId = self.createGroup(domain)
        rootId = self.getRootId(domain)   
        name = 'softlink'
        req = self.endpoint + "/group/" + rootId + "/links/" + name 
        payload = {"h5path": "/somewhere"}
        headers = {'host': domain}
        # make request
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        # verify idempotent
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        
    def testDelete(self):
        logging.info("LinkTest.testDelete")
        domain = 'tall.' + config.get('domain') 
        grpId = self.createGroup(domain)
        rootId = self.getRootId(domain)   
        name = 'deleteme'
        req = self.endpoint + "/group/" + rootId + "/links/" + name 
        payload = {"id": grpId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        
        # now remove the link
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
    
       
if __name__ == '__main__':
    unittest.main()