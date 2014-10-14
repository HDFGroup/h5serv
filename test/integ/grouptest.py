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
import helper
import unittest
import json

class GroupTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(GroupTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))
       
    def testGet(self):
        for domain_name in ('tall', 'tall_ro'):
            domain = domain_name + '.' + config.get('domain')    
            req = self.endpoint + "/"
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            rootUUID = rspJson["root"]
            self.assertTrue(helper.validateId(rootUUID))
            self.failUnlessEqual(rspJson["groupCount"], 6)
            self.failUnlessEqual(rspJson["datasetCount"], 4)
        
            req = self.endpoint + "/groups/" + rootUUID
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.failUnlessEqual(rspJson["linkCount"], 2)
            self.failUnlessEqual(rspJson["attributeCount"], 2)
            self.failUnlessEqual(rsp.status_code, 200)
        
    def testGetGroups(self):
        domain = 'tall.' + config.get('domain')    
        headers = {'host': domain}
        req = self.endpoint + "/groups/" 
        rsp = requests.get(req, headers=headers)
        # to do - implement groups (iterate through all groups)
        # self.failUnlessEqual(rsp.status_code, 200)
        # rspJson = json.loads(rsp.text)
          
    def testPost(self):
        # test PUT_root
        domain = 'testGroupPost.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)   
        req = self.endpoint + "/groups/"
        headers = {'host': domain}
        # create a new group
        rsp = requests.post(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) 
        rspJson = json.loads(rsp.text)
        id = rspJson["id"]
        self.assertTrue(helper.validateId(id))   
       
    def testBadPost(self):
        domain = 'tall.' + config.get('domain')    
        req = self.endpoint + "/groups/dff53814-2906-11e4-9f76-3c15c2da029e"
        headers = {'host': domain}
        rsp = requests.post(req, headers=headers)
        # post is not allowed to provide uri, so should fail
        self.failUnlessEqual(rsp.status_code, 405) 
        
    def testDelete(self):
        domain = 'tall_g2_deleted.' + config.get('domain')  
        rootUUID = helper.getRootUUID(domain)
        helper.validateId(rootUUID)
        g2UUID = helper.getUUID(domain, rootUUID, 'g2')
        self.assertTrue(helper.validateId(g2UUID))
        req = self.endpoint + "/groups/" + g2UUID
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        
        
    def testDeleteBadUUID(self):
        domain = 'tall_g2_deleted.' + config.get('domain')    
        req = self.endpoint + "/groups/dff53814-2906-11e4-9f76-3c15c2da029e"
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 404)
        
    def testDeleteRoot(self):
        domain = 'tall.' + config.get('domain')    
        headers = {'host': domain}
        req = self.endpoint + "/"
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        rootUUID = rspJson["root"]
        req = self.endpoint + "/groups/" + rootUUID
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 403)
        
    
       
        
    
       
if __name__ == '__main__':
    unittest.main()