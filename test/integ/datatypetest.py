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
        self.assertEqual(rspJson['type'], 'H5T_IEEE_F32LE')
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
        typeItem = rspJson['type']
        self.assertEqual(typeItem['class'], 'H5T_COMPOUND')
        self.assertTrue('fields' in typeItem)
        fields = typeItem['fields']
        self.assertEqual(len(fields), 2)
        tempField = fields[0]
        self.assertEqual(tempField['name'], 'temp')
        self.assertEqual(tempField['type'], 'H5T_STD_I32LE')
        pressureField = fields[1]
        self.assertEqual(pressureField['name'], 'pressure')
        self.assertEqual(pressureField['type'], 'H5T_IEEE_F32LE')
    
    def testPost(self):
        domain = 'newdtype.datatypetest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) # creates domain
        
        payload = {'type': 'H5T_IEEE_F32LE'}
        req = self.endpoint + "/datatypes/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)  # create datatype
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
        self.failUnlessEqual(rsp.status_code, 201)
        
        
    def testPostTypes(self):
        domain = 'datatypes.datatypetest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) # creates domain
        
        root_uuid = helper.getRootUUID(domain)
        
        # list of types supported
        datatypes = ( 'H5T_STD_I8LE',   'H5T_STD_UI8LE',  
                      'H5T_STD_I16LE',  'H5T_STD_UI16LE',    
                      'H5T_STD_I32LE',  'H5T_STD_UI32LE',   
                      'H5T_STD_I64LE',  'H5T_STD_I64LE',  
                      'H5T_IEEE_F32LE', 'H5T_IEEE_F64LE' )
                     
               #todo: check on  'vlen_bytes', 'vlen_unicode'
        for datatype in datatypes:  
            payload = {'type': datatype}
            req = self.endpoint + "/datatypes/"
            rsp = requests.post(req, data=json.dumps(payload), headers=headers)
            self.failUnlessEqual(rsp.status_code, 201)  # create datatypes
            rspJson = json.loads(rsp.text)
            dtype_uuid = rspJson['id']
            self.assertTrue(helper.validateId(dtype_uuid))
         
            # link new datatype using the type name
            name = datatype
            req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
            payload = {"id": dtype_uuid}
            headers = {'host': domain}
            rsp = requests.put(req, data=json.dumps(payload), headers=headers)
            self.failUnlessEqual(rsp.status_code, 201)
            
    def testPostCompoundType(self):
        domain = 'compound.datatypetest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) # creates domain
        
        root_uuid = helper.getRootUUID(domain)
        fields = ({'name': 'temp', 'type': 'H5T_STD_I32LE'}, 
                    {'name': 'pressure', 'type': 'H5T_IEEE_F32LE'}) 
        datatype = {'class': 'H5T_COMPOUND', 'fields': fields }
        payload = {'type': datatype}
        req = self.endpoint + "/datatypes/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)  # create datatype
        rspJson = json.loads(rsp.text)
        dtype_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dtype_uuid))
         
        # link the new datatype 
        name = "dtype_compound"
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {"id": dtype_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
         
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
        req = helper.getEndpoint() + "/datatypes/" + dtype_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 410)
        
    def testGetCollection(self):
        domain = 'namedtype.' + config.get('domain') 
        req = self.endpoint + "/datatypes"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        datatypeIds = rspJson["datatypes"]
            
        self.failUnlessEqual(len(datatypeIds), 2)
        for uuid in datatypeIds:
            self.assertTrue(helper.validateId(uuid))
        
    
     
if __name__ == '__main__':
    unittest.main()