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
        req = helper.getEndpoint() + "/datasets/" + dset21UUID
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(rspJson['type'], 'float32')
        self.assertEqual(len(rspJson['shape']), 1)
        self.assertEqual(rspJson['shape'][0], 10)  
        
    def testPost(self):
        domain = 'newdset.datasettest.' + config.get('domain')
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
         
        # link new dataset as 'dset1'
        rootUUID = helper.getRootUUID(domain)
        name = 'dset1'
        req = self.endpoint + "/groups/" + rootUUID + "/links/" + name 
        payload = {"id": dsetUUID}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        
    def testPostTypes(self):
        domain = 'datatypes.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200) # creates domain
        
        rootUUID = helper.getRootUUID(domain)
        
        # list of types supported
        # 'Sn' is supported for any positive n, so we'll just use 
        # a few specific examples
        datatypes = ( 'S1', 'S10', 'S100', 
                       'int8',  'int16',   'int32',  'int64',
                      'uint8',       'uint16',  'uint32', 'uint64',
                    'float16',      'float32', 'float64',
                  'complex64',   'complex128',
                 'vlen_bytes', 'vlen_unicode')
        for datatype in datatypes:   
            payload = {'type': datatype, 'shape': 10}
            req = self.endpoint + "/datasets/"
            rsp = requests.post(req, data=json.dumps(payload), headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)  # create dataset
            rspJson = json.loads(rsp.text)
            dsetUUID = rspJson['id']
            self.assertTrue(helper.validateId(dsetUUID))
         
            # link new dataset using the type name
            name = datatype
            req = self.endpoint + "/groups/" + rootUUID + "/links/" + name 
            payload = {"id": dsetUUID}
            headers = {'host': domain}
            rsp = requests.put(req, data=json.dumps(payload), headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
        
    def testPostInvalidType(self):
        domain = 'tall.' + config.get('domain')  
        rootUUID = helper.getRootUUID(domain)
        payload = {'type': 'badtype', 'shape': 10}
        headers = {'host': domain}
        req = self.endpoint + "/datasets/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)
        
    def testPostInvalidShape(self):
        domain = 'tall.' + config.get('domain')  
        rootUUID = helper.getRootUUID(domain)
        payload = {'type': 'int32', 'shape': -5}
        headers = {'host': domain}
        req = self.endpoint + "/datasets/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)
       
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