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
            self.assertTrue('type' in rspJson)
            type = rspJson['type']
            self.assertEqual(type['class'], 'H5T_INTEGER')
            self.assertEqual(type['base'], 'H5T_STD_I8LE')
            self.assertTrue('shape' in rspJson)
            shape = rspJson['shape']
            self.assertEqual(shape['class'], 'H5S_SIMPLE')
            self.assertEqual(len(shape['dims']), 1)
            self.assertEqual(shape['dims'][0], 10) 
            self.assertTrue('maxdims' not in shape) 
            data = rspJson['value'] 
            self.assertEqual(len(data), 10)
            # data should be the array [97, 98, 99, ..., 105, 0]
            expected = range(97, 107)
            expected[9] = 0
            self.assertEqual(data, expected) 
            self.assertEqual(len(rspJson['hrefs']), 4)
            
    def testGetAll(self):
        for domain_name in ('tall', 'tall_ro'):
            domain = domain_name + '.' + config.get('domain') 
            rootUUID = helper.getRootUUID(domain)
            req = helper.getEndpoint() + "/groups/" + rootUUID + "/attributes"
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.assertEqual(len(rspJson['hrefs']), 4)
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
            shape = rspJson['shape']
            self.assertEqual(shape['class'], 'H5S_SIMPLE')
            self.assertEqual(len(shape['dims']), 1)
            self.assertEqual(shape['dims'][0], 1) 
            typeItem = rspJson['type']
            self.assertEqual(typeItem['class'], 'H5T_COMPOUND')
            self.assertEqual(len(typeItem['fields']), 4)
            fields = typeItem['fields']
            field0 = fields[0]
            self.assertEqual(field0['name'], 'time')
            field0Type = field0['type']
            self.assertEqual(field0Type['class'], 'H5T_INTEGER')
            self.assertEqual(field0Type['base'], 'H5T_STD_I64LE')
            field1 = fields[1]
            self.assertEqual(field1['name'], 'temp')
            field1Type = field1['type']
            self.assertEqual(field1Type['class'], 'H5T_INTEGER')
            self.assertEqual(field1Type['base'], 'H5T_STD_I64LE')
            field2 = fields[2]
            self.assertEqual(field2['name'], 'pressure')
            field2Type = field2['type']
            self.assertEqual(field2Type['class'], 'H5T_FLOAT')
            self.assertEqual(field2Type['base'], 'H5T_IEEE_F64LE')
            field3 = fields[3]
            self.assertEqual(field3['name'], 'wind')
            field3Type = field3['type']
            self.assertEqual(field3Type['class'], 'H5T_STRING')
            self.assertEqual(field3Type['cset'], 'H5T_CSET_ASCII')
            self.assertEqual(field3Type['order'], 'H5T_ORDER_NONE')
            self.assertEqual(field3Type['strsize'], 6)
            self.assertEqual(field3Type['strpad'], 'H5T_STR_NULLPAD')
            
    def testGetCommitted(self):
        domain = 'committed_type.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        req = helper.getEndpoint() + "/groups/" + root_uuid + "/attributes/attr1"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SCALAR')
        self.assertTrue('dims' not in shape)
        typeItem = rspJson['type']  # returns '/datatypes/<uuid>'
        npos = typeItem.rfind('/')
        type_uuid = typeItem[(npos+1):]
        self.assertTrue(helper.validateId(type_uuid))
             
    def testGetArray(self):
        domain = 'array_attr.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/attributes/A1"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 4) 
        typeItem = rspJson['type']    
        self.assertEqual(typeItem['class'], 'H5T_ARRAY')
        self.assertTrue('dims' in typeItem)
        typeShape = typeItem['dims']
        self.assertEqual(len(typeShape), 2)
        self.assertEqual(typeShape[0], 3)
        self.assertEqual(typeShape[1], 5)
        typeBase = typeItem['base']
        self.assertEqual(typeBase['class'], 'H5T_INTEGER')
        self.assertEqual(typeBase['base'], 'H5T_STD_I64LE')
        # bug! - unable to read value from attribute with array type
        # code is not returning 'value' key in this case
        # h5py issue: https://github.com/h5py/h5py/issues/498 
        if 'value' in rspJson:
            print 'remove above if check once h5py 2.4 is released'
            self.assertTrue('value' in rspJson)
            value = rspJson['value']
            self.assertEqual(len(value), 4)
            elem = value[0] # elem should be a 3x5 array 
            self.assertEqual(elem[2], [0, -2, -4, -6, -8])
        
    def testGetVLenString(self):
        domain = 'vlen_string_attr.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/attributes/A1"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 4) 
        typeItem = rspJson['type']   
        self.assertEqual(typeItem['class'], 'H5T_STRING')
        self.assertEqual(typeItem['cset'], 'H5T_CSET_ASCII')
        self.assertEqual(typeItem['order'], 'H5T_ORDER_NONE')
        self.assertEqual(typeItem['strsize'], 'H5T_VARIABLE')
        self.assertEqual(typeItem['strpad'], 'H5T_STR_NULLTERM')
        self.assertTrue('value' in rspJson)
        value = rspJson['value']
        self.assertEqual(len(value), 4) 
        self.assertEqual(value[0], "Parting")
        self.assertEqual(value[1], "is such")
        self.assertEqual(value[2], "sweet")
        self.assertEqual(value[3], "sorrow.")
        
    def testGetFixedString(self):
        domain = 'fixed_string_attr.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/attributes/A1"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 4)  
        typeItem = rspJson['type']
        
        self.assertEqual(typeItem['class'], 'H5T_STRING')
        self.assertEqual(typeItem['cset'], 'H5T_CSET_ASCII')
        self.assertEqual(typeItem['order'], 'H5T_ORDER_NONE')
        self.assertEqual(typeItem['strsize'], 7)
        self.assertEqual(typeItem['strpad'], 'H5T_STR_NULLPAD')
        self.assertTrue('value' in rspJson)
        value = rspJson['value']
        self.assertEqual(len(value), 4) 
        self.assertEqual(value[0], "Parting")
        self.assertEqual(value[1], "is such")
        self.assertEqual(value[2], "sweet")
        self.assertEqual(value[3], "sorrow.")
        
    def testGetEnum(self):
        domain = 'enum_attr.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/attributes/A1"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 2)
        self.assertEqual(shape['dims'][0], 4)
        self.assertEqual(shape['dims'][1], 7) 
        typeItem = rspJson['type']
        
        self.assertEqual(typeItem['class'], 'H5T_ENUM')
        baseType = typeItem['base']
        self.assertEqual(baseType['class'], 'H5T_INTEGER')
        self.assertEqual(baseType['base'], 'H5T_STD_I16BE')
        self.assertTrue('mapping' in typeItem)
        mapping = typeItem['mapping']
        self.assertEqual(len(mapping), 4)
        self.assertEqual(mapping['SOLID'], 0)
        self.assertEqual(mapping['LIQUID'], 1)
        self.assertEqual(mapping['GAS'], 2)
        self.assertEqual(mapping['PLASMA'], 3)
        self.assertTrue('value' in rspJson)
        value = rspJson['value']
        self.assertEqual(len(value), 4) 
        self.assertEqual(value[1][2], mapping['GAS'])
        
    def testGetVlen(self):
        domain = 'vlen_attr.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/attributes/A1"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 2)
        typeItem = rspJson['type']
        
        self.assertEqual(typeItem['class'], 'H5T_VLEN')
        baseType = typeItem['base']
        self.assertEqual(baseType['class'], 'H5T_INTEGER')
        self.assertEqual(baseType['base'], 'H5T_STD_I32LE')
        #verify data returned
        value = rspJson['value']
        self.assertEqual(len(value), 2)
        self.assertEqual(len(value[1]), 12)
        self.assertEqual(value[1][11], 144)
        
    def testGetOpaque(self):
        domain = 'opaque_attr.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/attributes/A1"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 4) 
        typeItem = rspJson['type']   
        
        self.assertEqual(typeItem['class'], 'H5T_OPAQUE')
        self.assertEqual(typeItem['size'], 7)
        self.assertTrue('value' not in rspJson)  # opaque data is not supported yet
        
    def testGetObjectReference(self):
        domain = 'objref_attr.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        ds1_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        ds2_uuid = helper.getUUID(domain, root_uuid, 'DS2') 
        g1_uuid = helper.getUUID(domain, root_uuid, 'G1') 
        req = helper.getEndpoint() + "/datasets/" + ds1_uuid + "/attributes/A1"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 2)  
        typeItem = rspJson['type']     
        self.assertEqual(typeItem['class'], 'H5T_REFERENCE')
        self.assertEqual(typeItem['base'], 'H5T_STD_REF_OBJ')
        self.assertTrue('value' in rspJson)
        value = rspJson['value']
        self.assertEqual(len(value), 2)
        self.assertEqual(value[0], '/groups/' + g1_uuid)
        self.assertEqual(value[1], '/datasets/' + ds2_uuid)
        
    def testGetRegionReference(self):
        domain = 'regionref_attr.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        ds1_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        ds2_uuid = helper.getUUID(domain, root_uuid, 'DS2') 
        req = helper.getEndpoint() + "/datasets/" + ds1_uuid + "/attributes/A1"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 2) 
        typeItem = rspJson['type']     
        self.assertEqual(typeItem['class'], 'H5T_REFERENCE')
        self.assertEqual(typeItem['base'], 'H5T_STD_REF_DSETREG')
        self.assertTrue('value' in rspJson)
        value = rspJson['value']
        self.assertEqual(len(value), 2)
        value = rspJson['value']
        self.assertEqual(len(value), 2)
        ref0 = value[0]
        self.assertEqual(ref0['select_type'], 'H5S_SEL_POINTS')
        self.assertEqual(ref0['id'], ds2_uuid)
        points = ref0['selection']
        self.assertEqual(len(points), 4)
        self.assertEqual(points[0], [0, 1])
        self.assertEqual(points[1], [2,11])
        self.assertEqual(points[2], [1, 0])
        self.assertEqual(points[3], [2, 4])
        
        ref1 = value[1]
        self.assertEqual(ref1['select_type'], 'H5S_SEL_HYPERSLABS')
        self.assertEqual(ref1['id'], ds2_uuid)
        hyperslabs = ref1['selection'] 
        self.assertEqual(len(hyperslabs), 4)
        self.assertEqual(hyperslabs[0][0], [0, 0])
        self.assertEqual(hyperslabs[0][1], [0, 2])
        self.assertEqual(hyperslabs[1][0], [0, 11])
        self.assertEqual(hyperslabs[1][1], [0, 13])
        self.assertEqual(hyperslabs[2][0], [2, 0])
        self.assertEqual(hyperslabs[2][1], [2, 2])
        self.assertEqual(hyperslabs[3][0], [2, 11])
        self.assertEqual(hyperslabs[3][1], [2, 13])
        
            
    def testGetScalar(self):
        domain = 'scalar.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        req = helper.getEndpoint() + "/groups/" + root_uuid + "/attributes/attr1"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SCALAR')
        self.assertTrue('dims' not in shape)
        typeItem = rspJson['type']
        self.assertEqual(typeItem['class'], 'H5T_INTEGER')
        self.assertEqual(typeItem['base'], 'H5T_STD_I64LE')
        data = rspJson['value'] 
        self.assertEqual(type(data), int)
        self.assertEqual(data, 42)
        
    def testPut(self):
        domain = 'tall_updated.' + config.get('domain') 
        attr_name = 'attr3'
        rootUUID = helper.getRootUUID(domain) 
        headers = {'host': domain}
           
        payload = {'type': 'H5T_IEEE_F32LE', 'shape': (0,), 'value': 3.12}
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
           
        payload = {'type': 'H5T_STD_I32LE', 'shape': (10,), 'value': data}
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
        
        fields = ({'name': 'temp', 'type': 'H5T_STD_I32LE'}, 
                    {'name': 'pressure', 'type': 'H5T_IEEE_F32LE'}) 
        datatype = {'class': 'H5T_COMPOUND', 'fields': fields }
        
        value = ((55, 32.34), (59, 29.34)) 
        payload = {'type': datatype, 'shape': 2, 'value': value}
        req = self.endpoint + "/groups/" + root_uuid + "/attributes/" + attr_name
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)  # create attribute
        rspJson = json.loads(rsp.text)
        self.assertEqual(len(rspJson['hrefs']), 3)
        
    def testPutCommittedType(self):
        domain = 'tall_updated.' + config.get('domain')
        attr_name = 'attr_committed'
        root_uuid = helper.getRootUUID(domain)
        headers = {'host': domain}
        
        # create the datatype
        payload = {'type': 'H5T_IEEE_F32LE'}
        req = self.endpoint + "/datatypes/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)  # create datatype
        rspJson = json.loads(rsp.text)
        dtype_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dtype_uuid))
         
        # link new datatype as 'dtype1'
        root_uuid = helper.getRootUUID(domain)
        name = 'dtype1'
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {'id': dtype_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        
        # create the attribute using the type created above
        value = []
        for i in range(10):
            value.append(i*0.5) 
        payload = {'type': dtype_uuid, 'shape': 10, 'value': value}
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
