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
        root_uuid = helper.getRootUUID(domain)
        g2_uuid = helper.getUUID(domain, root_uuid, 'g2')
        dset21_uuid = helper.getUUID(domain, g2_uuid, 'dset2.1') 
        req = helper.getEndpoint() + "/datasets/" + dset21_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(rspJson['type'], 'float32')
        self.assertEqual(rspJson['class'], 'simple')
        self.assertEqual(len(rspJson['shape']), 1)
        self.assertEqual(rspJson['shape'][0], 10)  
        self.assertEqual(rspJson['maxshape'][0], 10)
        
    def testGetResizable(self):
        domain = 'resizable.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        resizable_1d_uuid = helper.getUUID(domain, root_uuid, 'resizable_1d') 
        req = helper.getEndpoint() + "/datasets/" + resizable_1d_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(rspJson['type'], 'int64')
        self.assertEqual(len(rspJson['shape']), 1)
        self.assertEqual(rspJson['shape'][0], 10)  
        self.assertEqual(rspJson['maxshape'][0], 20)
        
        resizable_2d_uuid = helper.getUUID(domain, root_uuid, 'resizable_2d') 
        req = helper.getEndpoint() + "/datasets/" + resizable_2d_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(rspJson['type'], 'int64')
        self.assertEqual(len(rspJson['shape']), 2)
        self.assertEqual(rspJson['shape'][1], 10)  
        self.assertEqual(rspJson['maxshape'][1], 20)
        
        unlimited_1d_uuid = helper.getUUID(domain, root_uuid, 'unlimited_1d') 
        req = helper.getEndpoint() + "/datasets/" + unlimited_1d_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(rspJson['type'], 'int64')
        self.assertEqual(len(rspJson['shape']), 1)
        self.assertEqual(rspJson['shape'][0], 10)  
        self.assertEqual(rspJson['maxshape'][0], 0)
        
        unlimited_2d_uuid = helper.getUUID(domain, root_uuid, 'unlimited_2d') 
        req = helper.getEndpoint() + "/datasets/" + unlimited_2d_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(rspJson['type'], 'int64')
        self.assertEqual(len(rspJson['shape']), 2)
        self.assertEqual(rspJson['shape'][1], 10)  
        self.assertEqual(rspJson['maxshape'][1], 0)
        
    def testGetScalar(self):
        domain = 'scalar.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        dset_uuid = helper.getUUID(domain, root_uuid, '0d') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(rspJson['class'], 'scalar')
        self.assertEqual(len(rspJson['shape']), 0)
        self.assertEqual(rspJson['type'], 'int32')
       
    def testGetCompound(self):
        domain = 'compound.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(len(rspJson['shape']), 1)
        self.assertEqual(rspJson['shape'][0], 72)  
        self.assertEqual(len(rspJson['type']), 5)
        field0 = rspJson['type'][0]
        self.assertEqual(field0['date'], 'int64')
        field1 = rspJson['type'][1]
        self.assertEqual(field1['time'], 'S6')
    
    def testPost(self):
        domain = 'newdset.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) # creates domain
        
        payload = {'type': 'float32', 'shape': 10}
        req = self.endpoint + "/datasets/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dset_uuid))
         
        # link new dataset as 'dset1'
        root_uuid = helper.getRootUUID(domain)
        name = 'dset1'
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {"id": dset_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        
    def testPostScalar(self):
        domain = 'newscalar.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) # creates domain
        
        payload = {'type': 'int32'}
        req = self.endpoint + "/datasets/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dset_uuid))
         
        # link new dataset as 'dset1'
        root_uuid = helper.getRootUUID(domain)
        name = 'dset1'
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {"id": dset_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        
    def testPostTypes(self):
        domain = 'datatypes.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) # creates domain
        
        root_uuid = helper.getRootUUID(domain)
        
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
            self.failUnlessEqual(rsp.status_code, 201)  # create dataset
            rspJson = json.loads(rsp.text)
            dset_uuid = rspJson['id']
            self.assertTrue(helper.validateId(dset_uuid))
         
            # link new dataset using the type name
            name = datatype
            req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
            payload = {"id": dset_uuid}
            headers = {'host': domain}
            rsp = requests.put(req, data=json.dumps(payload), headers=headers)
            self.failUnlessEqual(rsp.status_code, 201)
            
    def testPostCompoundType(self):
        domain = 'compound.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) # creates domain
        
        root_uuid = helper.getRootUUID(domain)
        
        datatype = ({'name': 'temp', 'type': 'int32'}, 
                    {'name': 'pressure', 'type': 'float32'}) 
        payload = {'type': datatype, 'shape': 10}
        req = self.endpoint + "/datasets/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dset_uuid))
         
        # link the new dataset 
        name = "dset"
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {"id": dset_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        
    def testPostResizable(self):
        domain = 'resizabledset.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) # creates domain
        
        payload = {'type': 'float32', 'shape': 10, 'maxshape': 20}
        req = self.endpoint + "/datasets/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dset_uuid))
         
        # link new dataset as 'resizable'
        root_uuid = helper.getRootUUID(domain)
        name = 'resizable'
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {"id": dset_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        
        # create a datataset with unlimited dimension
        payload = {'type': 'float32', 'shape': 10, 'maxshape': 0}
        req = self.endpoint + "/datasets/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dset_uuid))
         
        # link new dataset as 'resizable'
        root_uuid = helper.getRootUUID(domain)
        name = 'unlimited'
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {"id": dset_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)     
        
    def testPostInvalidType(self):
        domain = 'tall.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        payload = {'type': 'badtype', 'shape': 10}
        headers = {'host': domain}
        req = self.endpoint + "/datasets/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)
        
    def testPostInvalidShape(self):
        domain = 'tall.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        payload = {'type': 'int32', 'shape': -5}
        headers = {'host': domain}
        req = self.endpoint + "/datasets/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)
       
    def testDelete(self):
        domain = 'tall_dset112_deleted.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        helper.validateId(root_uuid)
        g1_uuid = helper.getUUID(domain, root_uuid, 'g1')
        self.assertTrue(helper.validateId(g1_uuid))
        g11_uuid = helper.getUUID(domain, g1_uuid, 'g1.1')
        self.assertTrue(helper.validateId(g11_uuid))
        d112_uuid = helper.getUUID(domain, g11_uuid, 'dset1.1.2')
        self.assertTrue(helper.validateId(d112_uuid))
        req = self.endpoint + "/datasets/" + d112_uuid
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
             
    def testDeleteBadUUID(self):
        domain = 'tall_dset112_deleted.' + config.get('domain')    
        req = self.endpoint + "/datasets/dff53814-2906-11e4-9f76-3c15c2da029e"
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 404)
        
    def testGetCollection(self):
        for domain_name in ('tall', 'tall_ro'):
            domain = domain_name + '.' + config.get('domain')    
            req = self.endpoint + "/datasets"
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            datasetIds = rspJson["datasets"]
            
            self.failUnlessEqual(len(datasetIds), 4)
            for uuid in datasetIds:
                self.assertTrue(helper.validateId(uuid))
        
if __name__ == '__main__':
    unittest.main()