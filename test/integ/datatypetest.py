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

class DatatypeTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(DatatypeTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))    
       
    def testGet(self):
        domain = 'namedtype.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        dtype_uuid = helper.getUUID(domain, root_uuid, 'dtype_simple')
        self.assertTrue(helper.validateId(dtype_uuid))
         
        req = helper.getEndpoint() + "/datatypes/" + dtype_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(rspJson['id'], dtype_uuid)
        self.assertEqual(rspJson['type'], 'float32')
        self.assertEqual(rspJson['attributeCount'], 1)
       
    def testGetCompound(self):
        domain = 'namedtype.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        dtype_uuid = helper.getUUID(domain, root_uuid, 'dtype_compound') 
        req = helper.getEndpoint() + "/datatypes/" + dtype_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        typeJson = rspJson['type']
        self.assertEqual(len(typeJson), 2)
        field0 = typeJson[0]
        self.assertEqual(field0['temp'], 'int32')
        field1 = typeJson[1]
        self.assertEqual(field1['pressure'], 'float32')
    
    def testPost(self):
        domain = 'newdtype.datatypetest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200) # creates domain
        
        payload = {'type': 'float32'}
        req = self.endpoint + "/datatypes/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)  # create datatype
        rspJson = json.loads(rsp.text)
        dtype_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dtype_uuid))
         
        # link new dataset as 'dtype1'
        root_uuid = helper.getRootUUID(domain)
        name = 'dtype1'
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {'id': dtype_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        
        
    def testPostTypes(self):
        domain = 'datatypes.datatypetest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200) # creates domain
        
        root_uuid = helper.getRootUUID(domain)
        
        # list of types supported
        # 'Sn' is supported for any positive n, so we'll just use 
        # a few specific examples
        datatypes = ( 'S1', 'S10', 'S100', 
                       'int8',  'int16',   'int32',  'int64',
                      'uint8',       'uint16',  'uint32', 'uint64',
                    'float16',      'float32', 'float64',
                  'complex64',   'complex128')
                     
               #todo: check on  'vlen_bytes', 'vlen_unicode'
        for datatype in datatypes:  
            payload = {'type': datatype}
            req = self.endpoint + "/datatypes/"
            rsp = requests.post(req, data=json.dumps(payload), headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)  # create datatypes
            rspJson = json.loads(rsp.text)
            dtype_uuid = rspJson['id']
            self.assertTrue(helper.validateId(dtype_uuid))
         
            # link new dataset using the type name
            name = datatype
            req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
            payload = {"id": dtype_uuid}
            headers = {'host': domain}
            rsp = requests.put(req, data=json.dumps(payload), headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            
    def testPostCompoundType(self):
        domain = 'compound.datatypetest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200) # creates domain
        
        root_uuid = helper.getRootUUID(domain)
        
        datatype = ({'name': 'temp', 'type': 'int32'}, 
                    {'name': 'pressure', 'type': 'float32'}) 
        payload = {'type': datatype}
        req = self.endpoint + "/datatypes/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)  # create datatype
        rspJson = json.loads(rsp.text)
        dtype_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dtype_uuid))
         
        # link the new dataset 
        name = "dtype_compound"
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {"id": dtype_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
         
    def testPostInvalidType(self):
        domain = 'tall.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        payload = {'type': 'badtype'}
        headers = {'host': domain}
        req = self.endpoint + "/datasets/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)
        
    def testDelete(self):
        domain = 'namedtype_deleted.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        dtype_uuid = helper.getUUID(domain, root_uuid, 'dtype_simple')
        self.assertTrue(helper.validateId(dtype_uuid))
         
        req = helper.getEndpoint() + "/datatypes/" + dtype_uuid
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        
        # verify that it's gone
        dtype_uuid = helper.getUUID(domain, root_uuid, 'dtype_simple')
        self.failUnlessEqual(dtype_uuid, None)
        
    
     
if __name__ == '__main__':
    unittest.main()