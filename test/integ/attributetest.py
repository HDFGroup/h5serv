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

class AttributeTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(AttributeTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))    
       
    def testGet(self):
        for domain_name in ('tall', 'tall_ro'):
            domain = domain_name + '.' + config.get('domain') 
            rootUUID = helper.getRootUUID(domain)
            req = helper.getEndpoint() + "/groups/" + rootUUID + "/attributes/attr1"
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.assertEqual(rspJson['name'], 'attr1')
            self.assertEqual(rspJson['type'], 'H5T_STD_I8LE')
            self.assertEqual(len(rspJson['shape']), 1)
            self.assertEqual(rspJson['shape'][0], 10)
            data = rspJson['value'] 
            self.assertEqual(len(data), 10)
            # data should be the array [97, 98, 99, ..., 105, 0]
            expected = range(97, 107)
            expected[9] = 0
            self.assertEqual(data, expected) 
            self.assertEqual(len(rspJson['hrefs']), 3)
            
    def testGetString(self):
        for domain_name in ('attr1k',):   
            domain = domain_name + '.' + config.get('domain') 
            rootUUID = helper.getRootUUID(domain)
            req = helper.getEndpoint() + "/groups/" + rootUUID + "/attributes/a0001"
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.assertEqual(rspJson['name'], 'a0001')
            typeItem = rspJson['type']
            self.assertEqual(typeItem['class'], 'H5T_STRING')
            self.assertEqual(typeItem['cset'], 'H5T_CSET_ASCII')
            self.assertEqual(typeItem['order'], 'H5T_ORDER_NONE')
            self.assertEqual(typeItem['strpad'], 'H5T_STR_NULLTERM') 
            self.assertEqual(typeItem['strsize'], 'H5T_VARIABLE') 
            self.assertEqual(len(rspJson['shape']), 0)
            data = rspJson['value'] 
            self.assertEqual(data, "this is attribute: 1") 
            self.assertEqual(len(rspJson['hrefs']), 3)
            
    def testGetAll(self):
        for domain_name in ('tall', 'tall_ro'):
            domain = domain_name + '.' + config.get('domain') 
            rootUUID = helper.getRootUUID(domain)
            req = helper.getEndpoint() + "/groups/" + rootUUID + "/attributes"
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.assertEqual(len(rspJson['hrefs']), 3)
            attrsJson = rspJson['attributes']
            self.assertEqual(len(attrsJson), 2)
            self.assertEqual(attrsJson[0]['name'], 'attr1')
            self.assertEqual(attrsJson[1]['name'], 'attr2')
            self.assertFalse('value' in attrsJson[0])
            
    def testGetBatch(self):
        domain = 'attr1k.' + config.get('domain')   
        rootUUID = helper.getRootUUID(domain)     
        req = helper.getEndpoint() + "/groups/" + rootUUID + "/attributes"
        headers = {'host': domain}
        params = {'Limit': 50 }
        names = set()
        # get attributes in 20 batches of 50 links each
        lastName = None
        for batchno in range(20):
            if lastName:
                params['Marker'] = lastName
            rsp = requests.get(req, headers=headers, params=params)
            self.failUnlessEqual(rsp.status_code, 200)
            if rsp.status_code != 200:
                break
            rspJson = json.loads(rsp.text)
            attrs = rspJson['attributes']
            self.failUnlessEqual(len(attrs) <= 50, True)
            for attr in attrs:
                lastName = attr['name']
                names.add(lastName)
            if len(attrs) == 0:
                break
        self.failUnlessEqual(len(names), 1000)  # should get 1000 unique attributes
        
    def testGetCompound(self):
        for domain_name in ('compound_attr', ):
            domain = domain_name + '.' + config.get('domain') 
            rootUUID = helper.getRootUUID(domain)
            req = helper.getEndpoint() + "/groups/" + rootUUID + "/attributes/weather"
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.assertEqual(rspJson['name'], 'weather')
            typeItem = rspJson['type']
            self.assertEqual(typeItem['class'], 'H5T_COMPOUND')
            self.assertEqual(len(typeItem['fields']), 4)
            fields = typeItem['fields']
            field0 = fields[0]
            self.assertEqual(field0['name'], 'time')
            self.assertEqual(field0['type'], 'H5T_STD_I64LE')
            field1 = fields[1]
            self.assertEqual(field1['name'], 'temp')
            self.assertEqual(field1['type'], 'H5T_STD_I64LE')
            field2 = fields[2]
            self.assertEqual(field2['name'], 'pressure')
            self.assertEqual(field2['type'], 'H5T_IEEE_F64LE')
            field3 = fields[3]
            self.assertEqual(field3['name'], 'wind')
            field3Type = field3['type']
            self.assertEqual(field3Type['class'], 'H5T_STRING')
            self.assertEqual(field3Type['cset'], 'H5T_CSET_ASCII')
            self.assertEqual(field3Type['order'], 'H5T_ORDER_NONE')
            self.assertEqual(field3Type['strsize'], 6)
            self.assertEqual(field3Type['strpad'], 'H5T_STR_NULLPAD')
             
            
    def testGetScalar(self):
        domain = 'scalar.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        req = helper.getEndpoint() + "/groups/" + root_uuid + "/attributes/attr1"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(rspJson['class'], 'scalar')
        self.assertEqual(len(rspJson['shape']), 0)
        self.assertEqual(rspJson['type'], 'H5T_STD_I64LE')
        data = rspJson['value'] 
        self.assertEqual(type(data), int)
        self.assertEqual(data, 42)
        
    def testPut(self):
        domain = 'tall_updated.' + config.get('domain') 
        attr_name = 'attr3'
        rootUUID = helper.getRootUUID(domain) 
        headers = {'host': domain}
           
        payload = {'type': 'float32', 'shape': (0,), 'value': 3.12}
        req = self.endpoint + "/groups/" + rootUUID + "/attributes/" + attr_name
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)  # create attribute
        rspJson = json.loads(rsp.text)
        self.assertEqual(len(rspJson['hrefs']), 3)
        
    def testPutList(self):
        domain = 'tall_updated.' + config.get('domain') 
        attr_name = 'attr4'
        rootUUID = helper.getRootUUID(domain) 
        headers = {'host': domain}
        data = range(10)
           
        payload = {'type': 'int32', 'shape': (10,), 'value': data}
        req = self.endpoint + "/groups/" + rootUUID + "/attributes/" + attr_name
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)  # create attribute
        rspJson = json.loads(rsp.text)
        self.assertEqual(len(rspJson['hrefs']), 3)
        
    def testPutCompound(self):
        domain = 'tall_updated.' + config.get('domain')
        attr_name = 'attr_compound'
        root_uuid = helper.getRootUUID(domain)
        headers = {'host': domain}
        
        datatype = ({'name': 'temp', 'type': 'int32'}, 
                    {'name': 'pressure', 'type': 'float32'})
        value = ((55, 32.34), (59, 29.34)) 
        payload = {'type': datatype, 'shape': 2, 'value': value}
        req = self.endpoint + "/groups/" + root_uuid + "/attributes/" + attr_name
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)  # create attribute
        rspJson = json.loads(rsp.text)
        self.assertEqual(len(rspJson['hrefs']), 3)
        
    def testDelete(self):
        domain = 'tall_updated.' + config.get('domain') 
        attr_name = 'attr1'
        rootUUID = helper.getRootUUID(domain) 
        headers = {'host': domain}
           
        req = self.endpoint + "/groups/" + rootUUID + "/attributes/" + attr_name
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)  # delete attribute
        
                         
            
if __name__ == '__main__':
    unittest.main()