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
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(rspJson['id'], dtype_uuid)
        typeItem = rspJson['type']
        self.assertEqual(typeItem['class'], 'H5T_FLOAT')
        self.assertEqual(typeItem['base'], 'H5T_IEEE_F32LE')
        self.assertEqual(rspJson['attributeCount'], 1)
       
    def testGetCompound(self):
        domain = 'namedtype.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        dtype_uuid = helper.getUUID(domain, root_uuid, 'dtype_compound') 
        req = helper.getEndpoint() + "/datatypes/" + dtype_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        typeItem = rspJson['type']
        self.assertEqual(typeItem['class'], 'H5T_COMPOUND')
        self.assertTrue('fields' in typeItem)
        fields = typeItem['fields']
        self.assertEqual(len(fields), 2)
        tempField = fields[0]
        self.assertEqual(tempField['name'], 'temp')
        tempFieldType = tempField['type']
        self.assertEqual(tempFieldType['class'], 'H5T_INTEGER')
        self.assertEqual(tempFieldType['base'], 'H5T_STD_I32LE')
        pressureField = fields[1]
        self.assertEqual(pressureField['name'], 'pressure')
        pressureFieldType = pressureField['type']
        self.assertEqual(pressureFieldType['class'], 'H5T_FLOAT')
        self.assertEqual(pressureFieldType['base'], 'H5T_IEEE_F32LE')
    
    def testPost(self):
        domain = 'newdtype.datatypetest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        payload = {'type': 'H5T_IEEE_F32LE'}
        req = self.endpoint + "/datatypes"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create datatype
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
        self.assertEqual(rsp.status_code, 201)
        
    def testPostWithLink(self):
        # test PUT_root
        domain = 'newlinkedtype.datatypetest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201)  
        
        root_uuid = helper.getRootUUID(domain)
        
        payload = { 
            'type': 'H5T_IEEE_F64LE', 
            'link': {'id': root_uuid, 'name': 'linked_dtype'} 
        }
         
        req = self.endpoint + "/datatypes"
        headers = {'host': domain}
        # create a new group
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201) 
        rspJson = json.loads(rsp.text)
        self.assertEqual(rspJson["attributeCount"], 0)
        self.assertTrue(helper.validateId(rspJson["id"]) ) 
        
        
    def testPostTypes(self):
        domain = 'datatypes.datatypetest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        root_uuid = helper.getRootUUID(domain)
        
        # list of types supported
        datatypes = ( 'H5T_STD_I8LE',   'H5T_STD_U8LE',  
                      'H5T_STD_I16LE',  'H5T_STD_U16LE',    
                      'H5T_STD_I32LE',  'H5T_STD_U32LE',   
                      'H5T_STD_I64LE',  'H5T_STD_U64LE',  
                      'H5T_IEEE_F32LE', 'H5T_IEEE_F64LE' )
                     
               #todo: check on  'vlen_bytes', 'vlen_unicode'
        for datatype in datatypes:  
            payload = {'type': datatype}
            req = self.endpoint + "/datatypes"
            rsp = requests.post(req, data=json.dumps(payload), headers=headers)
            self.assertEqual(rsp.status_code, 201)  # create datatypes
            rspJson = json.loads(rsp.text)
            dtype_uuid = rspJson['id']
            self.assertTrue(helper.validateId(dtype_uuid))
         
            # link new datatype using the type name
            name = datatype
            req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
            payload = {"id": dtype_uuid}
            headers = {'host': domain}
            rsp = requests.put(req, data=json.dumps(payload), headers=headers)
            self.assertEqual(rsp.status_code, 201)
            
    def testPostCompoundType(self):
        domain = 'compound.datatypetest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        root_uuid = helper.getRootUUID(domain)
        fields = ({'name': 'temp', 'type': 'H5T_STD_I32LE'}, 
                    {'name': 'pressure', 'type': 'H5T_IEEE_F32LE'}) 
        datatype = {'class': 'H5T_COMPOUND', 'fields': fields }
        payload = {'type': datatype}
        req = self.endpoint + "/datatypes"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create datatype
        rspJson = json.loads(rsp.text)
        dtype_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dtype_uuid))
         
        # link the new datatype 
        name = "dtype_compound"
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {"id": dtype_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)
    
    """
    This test fails due to h5py issue #540: https://github.com/h5py/h5py/issues/540
    Commenting out for now.
        
    def testPostVLenStringType(self):
        domain = 'vlenstr.datatypetest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        root_uuid = helper.getRootUUID(domain)
        data_type = { 'charSet':   'H5T_CSET_ASCII', 
                     'class':  'H5T_STRING', 
                     'strPad': 'H5T_STR_NULLPAD', 
                     'length': 'H5T_VARIABLE'}
                     
        payload = {'type': data_type}
        req = self.endpoint + "/datatypes"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create datatype
        rspJson = json.loads(rsp.text)
        dtype_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dtype_uuid))
         
        # link the new datatype 
        name = "dtype_vlenstr"
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {"id": dtype_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)
    """
         
    def testPostInvalidType(self):
        domain = 'tall.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        payload = {'type': 'badtype'}
        headers = {'host': domain}
        req = self.endpoint + "/datatypes"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 400)
        
    def testDelete(self):
        domain = 'namedtype_deleted.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        dtype_uuid = helper.getUUID(domain, root_uuid, 'dtype_simple')
        self.assertTrue(helper.validateId(dtype_uuid))
         
        req = helper.getEndpoint() + "/datatypes/" + dtype_uuid
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        
        # verify that it's gone
        req = helper.getEndpoint() + "/datatypes/" + dtype_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 410)
        
    def testGetCollection(self):
        domain = 'namedtype.' + config.get('domain') 
        req = self.endpoint + "/datatypes"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        datatypeIds = rspJson["datatypes"]
            
        self.assertEqual(len(datatypeIds), 2)
        for uuid in datatypeIds:
            self.assertTrue(helper.validateId(uuid))
            
    def testGetCollectionBatch(self):
        domain = 'type1k.' + config.get('domain')   
        req = self.endpoint + "/datatypes" 
        headers = {'host': domain}
        params = {'Limit': 50 }
        uuids = set()
        # get ids in 20 batches of 50 links each
        last_uuid = None
        for batchno in range(20):
            if last_uuid:
                params['Marker'] = last_uuid
            rsp = requests.get(req, headers=headers, params=params)
            self.assertEqual(rsp.status_code, 200)
            if rsp.status_code != 200:
                break
            rspJson = json.loads(rsp.text)
            typeIds = rspJson["datatypes"]
            self.assertEqual(len(typeIds) <= 50, True)
            for typeId in typeIds:
                uuids.add(typeId)
                last_uuid = typeId
            if len(typeIds) == 0:
                break
        self.assertEqual(len(uuids), 1000)  # should get 1000 unique uuid's 
        
    
     
if __name__ == '__main__':
    unittest.main()
