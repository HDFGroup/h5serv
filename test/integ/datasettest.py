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
        self.assertTrue(helper.validateId(root_uuid))
        g2_uuid = helper.getUUID(domain, root_uuid, 'g2')
        dset21_uuid = helper.getUUID(domain, g2_uuid, 'dset2.1') 
        req = helper.getEndpoint() + "/datasets/" + dset21_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('type' in rspJson)
        type = rspJson['type']
        self.assertEqual(type['class'], 'H5T_FLOAT')
        self.assertEqual(type['base'], 'H5T_IEEE_F32BE')
        self.assertTrue('shape' in rspJson)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 10)  
        self.assertTrue('maxdims' not in shape)
        
    def testGetResizable(self):
        domain = 'resizable.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        resizable_1d_uuid = helper.getUUID(domain, root_uuid, 'resizable_1d') 
        req = helper.getEndpoint() + "/datasets/" + resizable_1d_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        type = rspJson['type']
        self.assertEqual(type['class'], 'H5T_INTEGER')
        self.assertEqual(type['base'], 'H5T_STD_I64LE')
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 10)  
        self.assertEqual(shape['maxdims'][0], 20)
        
        resizable_2d_uuid = helper.getUUID(domain, root_uuid, 'resizable_2d') 
        req = helper.getEndpoint() + "/datasets/" + resizable_2d_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        type = rspJson['type']
        self.assertEqual(type['class'], 'H5T_INTEGER')
        self.assertEqual(type['base'], 'H5T_STD_I64LE')
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 2)
        self.assertEqual(shape['dims'][1], 10)  
        self.assertEqual(shape['maxdims'][1], 20)
        
        unlimited_1d_uuid = helper.getUUID(domain, root_uuid, 'unlimited_1d') 
        req = helper.getEndpoint() + "/datasets/" + unlimited_1d_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        type = rspJson['type']
        self.assertEqual(type['class'], 'H5T_INTEGER')
        self.assertEqual(type['base'], 'H5T_STD_I64LE')
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 10)  
        self.assertEqual(shape['maxdims'][0], 0)
        
        unlimited_2d_uuid = helper.getUUID(domain, root_uuid, 'unlimited_2d') 
        req = helper.getEndpoint() + "/datasets/" + unlimited_2d_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        type = rspJson['type']
        self.assertEqual(type['class'], 'H5T_INTEGER')
        self.assertEqual(type['base'], 'H5T_STD_I64LE')
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 2)
        self.assertEqual(shape['dims'][1], 10)  
        self.assertEqual(shape['maxdims'][1], 0)
        
    def testGetScalar(self):
        domain = 'scalar.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, '0d') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        type = rspJson['type']
        self.assertEqual(type['class'], 'H5T_INTEGER')
        self.assertEqual(type['base'], 'H5T_STD_I32LE')
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SCALAR')
        self.assertTrue('dims' not in shape)
        self.assertTrue('maxdims' not in shape)
        
    def testGetScalarString(self):
        domain = 'scalar.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, '0ds') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        type = rspJson['type']
        self.assertEqual(type['class'], 'H5T_STRING')
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SCALAR')
        self.assertTrue('dims' not in shape)
        self.assertTrue('maxdims' not in shape)
        
    def testGetSimpleOneElement(self):
        domain = 'scalar.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, '1d') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        type = rspJson['type']
        self.assertEqual(type['class'], 'H5T_INTEGER')
        self.assertEqual(type['base'], 'H5T_STD_I32LE')
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertTrue('dims' in shape)
        self.assertEqual(shape['dims'][0], 1) 
        
    def testGetSimpleOneElementString(self):
        domain = 'scalar.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, '1ds') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        type = rspJson['type']
        self.assertEqual(type['class'], 'H5T_STRING')
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertTrue('dims' in shape)
        self.assertEqual(shape['dims'][0], 1) 
        
        
    def testGetNullSpace(self):
        domain = 'null_space_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        type = rspJson['type']
        self.assertEqual(type['class'], 'H5T_INTEGER')
        self.assertEqual(type['base'], 'H5T_STD_I32LE')
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_NULL')
        self.assertTrue('dims' not in shape)
        self.assertTrue('maxdims' not in shape)
       
    def testGetCompound(self):
        domain = 'compound.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 72)  
        typeItem = rspJson['type']   
        self.assertEqual(typeItem['class'], 'H5T_COMPOUND')
        self.assertTrue('fields' in typeItem)
        fields = typeItem['fields']
        self.assertEqual(len(fields), 5)
        timeField = fields[1]
        self.assertEqual(timeField['name'], 'time')
        self.assertTrue('type' in timeField)
        timeFieldType = timeField['type']
        self.assertEqual(timeFieldType['class'], 'H5T_STRING')
        self.assertEqual(timeFieldType['cset'], 'H5T_CSET_ASCII')
        self.assertEqual(timeFieldType['order'], 'H5T_ORDER_NONE')
        self.assertEqual(timeFieldType['strsize'], 6)
        self.assertEqual(timeFieldType['strpad'], 'H5T_STR_NULLPAD')
        tempField = fields[2]
        self.assertEqual(tempField['name'], 'temp')
        tempFieldType = tempField['type']
        self.assertEqual(tempFieldType['class'], 'H5T_INTEGER')
        self.assertEqual(tempFieldType['base'], 'H5T_STD_I64LE')
        
    def testGetCompoundCommitted(self):
        domain = 'compound_committed.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 72)  
        typeItem = rspJson['type']   
        self.assertEqual(typeItem['class'], 'H5T_COMPOUND')
        self.assertTrue('fields' in typeItem)
        fields = typeItem['fields']
        self.assertEqual(len(fields), 3)
        timeField = fields[1]
        self.assertEqual(timeField['name'], 'time')
        self.assertTrue('type' in timeField)
        timeFieldType = timeField['type']
        self.assertEqual(timeFieldType['class'], 'H5T_STRING')
        self.assertEqual(timeFieldType['cset'], 'H5T_CSET_ASCII')
        self.assertEqual(timeFieldType['order'], 'H5T_ORDER_NONE')
        self.assertEqual(timeFieldType['strsize'], 6)
        self.assertEqual(timeFieldType['strpad'], 'H5T_STR_NULLPAD')
        tempField = fields[2]
        self.assertEqual(tempField['name'], 'temp')
        tempFieldType = tempField['type']
        self.assertEqual(tempFieldType['class'], 'H5T_INTEGER')
        self.assertEqual(tempFieldType['base'], 'H5T_STD_I32LE')
        
    def testGetCompoundArray(self):
        # compound where the fields are array type
        domain = 'tstr.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'comp1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 2)
        self.assertEqual(shape['dims'][0], 3) 
        self.assertEqual(shape['dims'][1], 6)   
        typeItem = rspJson['type'] 
        self.assertEqual(typeItem['class'], 'H5T_COMPOUND')
        self.assertTrue('fields' in typeItem)
        fields = typeItem['fields']
        self.assertEqual(len(fields), 2)
        intField = fields[0]
        self.assertEqual(intField['name'], 'int_array')
        self.assertTrue('type' in intField)
        intFieldType = intField['type']
        self.assertEqual(intFieldType['class'], 'H5T_ARRAY')
        intFieldTypeDims = intFieldType['dims']
        self.assertEqual(len(intFieldTypeDims), 2)
        self.assertEqual(intFieldTypeDims[0], 8)
        self.assertEqual(intFieldTypeDims[1], 10)
        self.assertTrue('base' in intFieldType)
        intFieldTypeBase = intFieldType['base']
        self.assertEqual(intFieldTypeBase['class'], 'H5T_INTEGER')
        self.assertEqual(intFieldTypeBase['base'], 'H5T_STD_I32BE')
        
        strField = fields[1]
        self.assertEqual(strField['name'], 'string')
        self.assertTrue('type' in strField)
        strFieldType = strField['type']
        self.assertEqual(strFieldType['class'], 'H5T_ARRAY')
        strFieldTypeDims = strFieldType['dims']
        self.assertEqual(len(strFieldTypeDims), 2)
        self.assertEqual(strFieldTypeDims[0], 3)
        self.assertEqual(strFieldTypeDims[1], 4)
        self.assertTrue('base' in strFieldType)
        strFieldTypeBase = strFieldType['base']
        
        self.assertEqual(strFieldTypeBase['class'], 'H5T_STRING')
        self.assertEqual(strFieldTypeBase['cset'], 'H5T_CSET_ASCII')
        self.assertEqual(strFieldTypeBase['order'], 'H5T_ORDER_NONE')
        self.assertEqual(strFieldTypeBase['strsize'], 32)
        # todo - fix, cf https://github.com/HDFGroup/h5serv/issues/20
        #self.assertEqual(strFieldTypeBase['strpad'], 'H5T_STR_SPACEPAD')
        
    def testGetCommitted(self):
        domain = 'committed_type.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 4)  
        typeItem = rspJson['type']  # returns '/datatypes/<uuid>'
        npos = typeItem.rfind('/')
        type_uuid = typeItem[(npos+1):]
        self.assertTrue(helper.validateId(type_uuid))
        
    def testGetArray(self):
        domain = 'array_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
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
        typeItemBase = typeItem['base']
        self.assertEqual(typeItemBase['class'], 'H5T_INTEGER')
        self.assertEqual(typeItemBase['base'], 'H5T_STD_I64LE')
        
    def testGetFixedString(self):
        domain = 'fixed_string_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
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
        
    def testGetEnum(self):
        domain = 'enum_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
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
        typeBase = typeItem['base']
        self.assertEqual(typeBase['class'], 'H5T_INTEGER')
        self.assertEqual(typeBase['base'], 'H5T_STD_I16BE')
        self.assertTrue('mapping' in typeItem)
        mapping = typeItem['mapping']
        self.assertEqual(len(mapping), 4)
        self.assertEqual(mapping['SOLID'], 0)
        self.assertEqual(mapping['LIQUID'], 1)
        self.assertEqual(mapping['GAS'], 2)
        self.assertEqual(mapping['PLASMA'], 3)
        
    def testGetVlen(self):
        domain = 'vlen_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
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
        typeBase = typeItem['base']
        self.assertEqual(typeBase['class'], 'H5T_INTEGER')
        self.assertEqual(typeBase['base'], 'H5T_STD_I32LE')
        
    def testGetOpaque(self):
        domain = 'opaque_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
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
        
    def testGetObjReference(self):
        domain = 'objref_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
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
        
    def testGetNullObjReference(self):
        domain = 'null_objref_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 1)   
        typeItem = rspJson['type']
        self.assertEqual(typeItem['class'], 'H5T_REFERENCE')
        self.assertEqual(typeItem['base'], 'H5T_STD_REF_OBJ')
        
    def testGetRegionReference(self):
        domain = 'regionref_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
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
        
    def testPost(self):
        domain = 'newdset.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) # creates domain
        
        payload = {'type': 'H5T_IEEE_F32LE', 'shape': 10}
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
        
        payload = {'type': 'H5T_STD_I32LE'}
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
        
        
        datatypes = ( 'H5T_STD_I8LE',   'H5T_STD_UI8LE',  
                      'H5T_STD_I16LE',  'H5T_STD_UI16LE',    
                      'H5T_STD_I32LE',  'H5T_STD_UI32LE',   
                      'H5T_STD_I64LE',  'H5T_STD_I64LE',  
                      'H5T_IEEE_F32LE', 'H5T_IEEE_F64LE' )
        
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
            
            # Do a GET on the datasets we just created
            req = helper.getEndpoint() + "/datasets/" + dset_uuid
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            # verify the type
            self.assertTrue('type' in rspJson)
            type = rspJson['type']
            self.assertTrue(type['class'] in ('H5T_FLOAT', 'H5T_INTEGER'))
            self.assertEqual(type['base'], datatype)      
            
            
    def testPostCompoundType(self):
        domain = 'compound.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) # creates domain
        
        root_uuid = helper.getRootUUID(domain)
        
        fields = ({'name': 'temp', 'type': 'H5T_STD_I32LE'}, 
                    {'name': 'pressure', 'type': 'H5T_IEEE_F32LE'}) 
        datatype = {'class': 'H5T_COMPOUND', 'fields': fields }
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
        
    def testPostCommittedType(self):
        domain = 'committedtype.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) # creates domain
        
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
        
        # create the dataset
        payload = {'type': dtype_uuid, 'shape': 10}
        req = self.endpoint + "/datasets/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dset_uuid))
         
        # link new dataset as 'dset1'
        name = 'dset1'
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {"id": dset_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        
    def testPostArray(self):
        domain = 'newarraydset.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) # creates domain
        datatype = {'class': 'H5T_ARRAY', 'base': 'H5T_STD_I64LE', 'shape': (3, 5) }
        
        payload = {'type': datatype, 'shape': 10}
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
        
        
    def testPostResizable(self):
        domain = 'resizabledset.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) # creates domain
        
        payload = {'type': 'H5T_IEEE_F32LE', 'shape': 10, 'maxshape': 20}
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
        payload = {'type': 'H5T_IEEE_F32LE', 'shape': 10, 'maxshape': 0}
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
        payload = {'type': 'H5T_STD_I32LE', 'shape': -5}
        headers = {'host': domain}
        req = self.endpoint + "/datasets/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)
       
    def testDelete(self):
        domain = 'tall_dset112_deleted.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
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
        # verify that a GET on the dataset fails
        req = helper.getEndpoint() + "/datasets/" + d112_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 410)
    
        
    def testDeleteRootChild(self):
        # test delete with a dset that is child of root
        domain = 'scalar_1d_deleted.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, '1d')
        self.assertTrue(helper.validateId(dset_uuid))
        req = self.endpoint + "/datasets/" + dset_uuid
        headers = {'host': domain}
        # verify that a GET on the dataset succeeds
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        # now delete the dataset
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        # verify that a GET on the dataset fails
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 410)
        
    def testDeleteAnonymous(self):
        # test delete works with anonymous dataset
        domain = 'tall_dset22_deleted.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        g2_uuid = helper.getUUID(domain, root_uuid, 'g2')
        self.assertTrue(helper.validateId(g2_uuid))
        d22_uuid = helper.getUUID(domain, g2_uuid, 'dset2.2')
        self.assertTrue(helper.validateId(d22_uuid))
        
        # delete g2, that will make dataset anonymous
        req = self.endpoint + "/groups/" + g2_uuid
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        
        # verify that a GET on the dataset succeeds still
        req = helper.getEndpoint() + "/datasets/" + d22_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        
        # delete dataset...
        req = self.endpoint + "/datasets/" + d22_uuid
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        
        # verify that a GET on the dataset fails
        req = helper.getEndpoint() + "/datasets/" + d22_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 410)
        
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