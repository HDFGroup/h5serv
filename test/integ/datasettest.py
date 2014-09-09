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

class DatasetTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(DatasetTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))    
       
    def testGet(self):
        domain = 'tall.' + config.get('domain')  
        rootUUID = helper.getRootUUID(domain)
        g2UUID = helper.getUUID(domain, rootUUID, 'g2')
        dset21UUID = helper.getUUID(domain, g2UUID, 'dset2.1') 
        print 'uuid:', dset21UUID
        req = helper.getEndpoint() + "/datasets/" + dset21UUID
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(rspJson['type'], 'float32')
        self.assertEqual(len(rspJson['shape']), 1)
        self.assertEqual(rspJson['shape'][0], 10)  
        
    def testPost(self):
        domain = 'newdset.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200) # creates domain
        
        payload = {'type': 'float32', 'shape': 10}
        req = self.endpoint + "/datasets/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)  # create dataset
        rspJson = json.loads(rsp.text)
        dsetUUID = rspJson['id']
        self.assertTrue(helper.validateId(dsetUUID))
         
        rootUUID = helper.getRootUUID(domain)
        name = 'dset1'
        req = self.endpoint + "/groups/" + rootUUID + "/links/" + name 
        payload = {"id": dsetUUID}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
       
    def testDelete(self):
        domain = 'tall_dset112_deleted.' + config.get('domain')  
        rootUUID = helper.getRootUUID(domain)
        helper.validateId(rootUUID)
        g1UUID = helper.getUUID(domain, rootUUID, 'g1')
        self.assertTrue(helper.validateId(g1UUID))
        g11UUID = helper.getUUID(domain, g1UUID, 'g1.1')
        self.assertTrue(helper.validateId(g11UUID))
        d112UUID = helper.getUUID(domain, g11UUID, 'dset1.1.2')
        self.assertTrue(helper.validateId(d112UUID))
        req = self.endpoint + "/datasets/" + d112UUID
        headers = {'host': domain}
        print 'deleting dataset:', d112UUID
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        
        
    def testDeleteBadUUID(self):
        domain = 'tall_dset112_deleted.' + config.get('domain')    
        req = self.endpoint + "/datasets/dff53814-2906-11e4-9f76-3c15c2da029e"
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 404)
        
if __name__ == '__main__':
    unittest.main()