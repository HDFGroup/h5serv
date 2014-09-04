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

class GroupTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(GroupTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))
       
    def testGet(self):
        domain = 'tall.' + config.get('domain')    
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        rootUUID = rspJson["root"]
        self.assertTrue(len(rootUUID) == 36)
        self.failUnlessEqual(rspJson["groupCount"], 6)
        self.failUnlessEqual(rspJson["datasetCount"], 4)
        
        req = self.endpoint + "/group/" + rootUUID
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.failUnlessEqual(rspJson["linkCount"], 2)
        self.failUnlessEqual(rspJson["attributeCount"], 2)
        self.failUnlessEqual(rsp.status_code, 200)
          
    def testPost(self):
        # test PUT_root
        domain = 'testGroupPost.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)   
        req = self.endpoint + "/group/"
        headers = {'host': domain}
        # create a new group
        rsp = requests.post(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200) 
        rspJson = json.loads(rsp.text)
        id = rspJson["id"]
        self.assertTrue(len(id) == 36)   
       
    def testBadPost(self):
        domain = 'tall.' + config.get('domain')    
        req = self.endpoint + "/group/dff53814-2906-11e4-9f76-3c15c2da029e"
        headers = {'host': domain}
        rsp = requests.post(req, headers=headers)
        # post is not allowed to provide uri, so should fail
        self.failUnlessEqual(rsp.status_code, 405) 
        
    def testDeleteBadUUID(self):
        domain = 'tall.' + config.get('domain')    
        req = self.endpoint + "/group/dff53814-2906-11e4-9f76-3c15c2da029e"
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
        req = self.endpoint + "/group/" + rootUUID
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 403)
        
    
       
        
    
       
if __name__ == '__main__':
    unittest.main()