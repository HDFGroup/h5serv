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
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
      
        self.assertTrue('type' in rspJson)
        type_json = rspJson['type']
        self.assertEqual(type_json['class'], 'H5T_FLOAT')
        self.assertEqual(type_json['base'], 'H5T_IEEE_F32BE')
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
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        type_json = rspJson['type']
        self.assertEqual(type_json['class'], 'H5T_INTEGER')
        self.assertEqual(type_json['base'], 'H5T_STD_I64LE')
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 10)  
        self.assertEqual(shape['maxdims'][0], 20)
        
        resizable_2d_uuid = helper.getUUID(domain, root_uuid, 'resizable_2d') 
        req = helper.getEndpoint() + "/datasets/" + resizable_2d_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        type_json = rspJson['type']
        self.assertEqual(type_json['class'], 'H5T_INTEGER')
        self.assertEqual(type_json['base'], 'H5T_STD_I64LE')
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 2)
        self.assertEqual(shape['dims'][1], 10)  
        self.assertEqual(shape['maxdims'][1], 20)
        
        unlimited_1d_uuid = helper.getUUID(domain, root_uuid, 'unlimited_1d') 
        req = helper.getEndpoint() + "/datasets/" + unlimited_1d_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        type_json = rspJson['type']
        self.assertEqual(type_json['class'], 'H5T_INTEGER')
        self.assertEqual(type_json['base'], 'H5T_STD_I64LE')
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 10)  
        self.assertEqual(shape['maxdims'][0], 0)
        
        unlimited_2d_uuid = helper.getUUID(domain, root_uuid, 'unlimited_2d') 
        req = helper.getEndpoint() + "/datasets/" + unlimited_2d_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        type_json = rspJson['type']
        self.assertEqual(type_json['class'], 'H5T_INTEGER')
        self.assertEqual(type_json['base'], 'H5T_STD_I64LE')
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
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        type_json = rspJson['type']
        self.assertEqual(type_json['class'], 'H5T_INTEGER')
        self.assertEqual(type_json['base'], 'H5T_STD_I32LE')
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
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        type_json = rspJson['type']
        self.assertEqual(type_json['class'], 'H5T_STRING')
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
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        type_json = rspJson['type']
        self.assertEqual(type_json['class'], 'H5T_INTEGER')
        self.assertEqual(type_json['base'], 'H5T_STD_I32LE')
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
        self.assertEqual(rsp.status_code, 200)
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
        self.assertEqual(rsp.status_code, 200)
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
        self.assertEqual(rsp.status_code, 200)
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
        self.assertEqual(timeFieldType['charSet'], 'H5T_CSET_ASCII')
        self.assertEqual(timeFieldType['length'], 6)
        self.assertEqual(timeFieldType['strPad'], 'H5T_STR_NULLPAD')
        tempField = fields[2]
        self.assertEqual(tempField['name'], 'temp')
        tempFieldType = tempField['type']
        self.assertEqual(tempFieldType['class'], 'H5T_INTEGER')
        self.assertEqual(tempFieldType['base'], 'H5T_STD_I64LE')
        
    def testGetCompoundArray(self):
        for domain_name in ('compound_array_dset', ):
            domain = domain_name + '.' + config.get('domain') 
            root_uuid = helper.getRootUUID(domain)
            dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
            req = helper.getEndpoint() + "/datasets/" + dset_uuid
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            shape = rspJson['shape']
            self.assertEqual(shape['class'], 'H5S_SIMPLE')
            self.assertEqual(len(shape['dims']), 10)
            typeItem = rspJson['type']
            self.assertEqual(typeItem['class'], 'H5T_COMPOUND')
            self.assertEqual(len(typeItem['fields']), 2)
            fields = typeItem['fields']
            field0 = fields[0]
            self.assertEqual(field0['name'], 'temp')
            field0Type = field0['type']
            self.assertEqual(field0Type['class'], 'H5T_FLOAT')
            self.assertEqual(field0Type['base'], 'H5T_IEEE_F64LE')
            field1 = fields[1]
            self.assertEqual(field1['name'], '2x2')
            field1Type = field1['type']
            self.assertEqual(field1Type['class'], 'H5T_ARRAY')
            self.assertEqual(field1Type['dims'], [2, 2])
            baseType = field1Type['base']
            self.assertEqual(baseType['class'], 'H5T_FLOAT')
            self.assertEqual(baseType['base'], 'H5T_IEEE_F32LE')
        
    def testGetCompoundCommitted(self):
        domain = 'compound_committed.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
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
        self.assertEqual(timeFieldType['charSet'], 'H5T_CSET_ASCII')
        self.assertEqual(timeFieldType['length'], 6)
        self.assertEqual(timeFieldType['strPad'], 'H5T_STR_NULLPAD')
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
        self.assertEqual(rsp.status_code, 200)
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
        self.assertEqual(strFieldTypeBase['charSet'], 'H5T_CSET_ASCII')
        self.assertEqual(strFieldTypeBase['length'], 32)
        # todo - fix, cf https://github.com/HDFGroup/h5serv/issues/20
        #self.assertEqual(strFieldTypeBase['strPad'], 'H5T_STR_SPACEPAD')
        
    def testGetCommitted(self):
        domain = 'committed_type.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
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
        self.assertEqual(rsp.status_code, 200)
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
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 4)   
        typeItem = rspJson['type']
        
        self.assertEqual(typeItem['class'], 'H5T_STRING')
        self.assertEqual(typeItem['charSet'], 'H5T_CSET_ASCII')
        self.assertEqual(typeItem['length'], 7)
        self.assertEqual(typeItem['strPad'], 'H5T_STR_NULLPAD')
        
    def testGetEnum(self):
        domain = 'enum_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
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

    def testGetBool(self):
        domain = 'bool_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 4)  
        typeItem = rspJson['type']
        
        self.assertEqual(typeItem['class'], 'H5T_ENUM')
        typeBase = typeItem['base']
        self.assertEqual(typeBase['class'], 'H5T_INTEGER')
        self.assertEqual(typeBase['base'], 'H5T_STD_I8LE')
        self.assertTrue('mapping' in typeItem)
        mapping = typeItem['mapping']
        self.assertEqual(len(mapping), 2)
        self.assertEqual(mapping['FALSE'], 0)
        self.assertEqual(mapping['TRUE'], 1)
         
        
    def testGetVlen(self):
        domain = 'vlen_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
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
        self.assertEqual(rsp.status_code, 200)
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
        self.assertEqual(rsp.status_code, 200)
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
        self.assertEqual(rsp.status_code, 200)
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
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 2)  
        typeItem = rspJson['type']
        self.assertEqual(typeItem['class'], 'H5T_REFERENCE')
        self.assertEqual(typeItem['base'], 'H5T_STD_REF_DSETREG')
        
    def testGetFillValueProp(self):
        domain = 'fillvalue.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid  
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('creationProperties' in rspJson)
        creationProps = rspJson['creationProperties']
        self.assertTrue('fillValue' in creationProps)   
        self.assertEqual(creationProps['fillValue'], 42)
        
    def testGetCreationProps(self):
        
        domain = 'dset_gzip.' + config.get('domain')  
        headers = {'host': domain}
        root_uuid = helper.getRootUUID(domain)
        
        # dset1
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid  
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('creationProperties' in rspJson)
        creationProps = rspJson['creationProperties']
        self.assertTrue('fillTime' in creationProps)
        self.assertEqual(creationProps['fillTime'], 'H5D_FILL_TIME_ALLOC')
        self.assertTrue('layout' in creationProps)
        layout = creationProps['layout']
        self.assertEqual(layout['class'], 'H5D_CHUNKED')
        self.assertEqual(layout['dims'], [100, 100])
        self.assertTrue('allocTime' in creationProps)
        self.assertEqual(creationProps['allocTime'], 'H5D_ALLOC_TIME_INCR')
        self.assertTrue('filters' in creationProps)
        filters = creationProps['filters']
        self.assertEqual(len(filters), 1)
        deflate_filter = filters[0]
        self.assertTrue('id' in deflate_filter)
        self.assertEqual(deflate_filter['id'], 1)
        self.assertTrue('class' in deflate_filter)
        self.assertEqual(deflate_filter['class'], 'H5Z_FILTER_DEFLATE')
        self.assertTrue('level' in deflate_filter)
        self.assertEqual(deflate_filter['level'], 9)
        self.assertTrue('name' in deflate_filter)
        self.assertEqual(deflate_filter['name'], 'deflate')
        
        # dset2
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset2') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid  
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('creationProperties' in rspJson)
        creationProps = rspJson['creationProperties']
        self.assertTrue('fillTime' in creationProps)
        self.assertEqual(creationProps['fillTime'], 'H5D_FILL_TIME_ALLOC')
        self.assertTrue('layout' in creationProps)
        layout = creationProps['layout']
        self.assertEqual(layout['class'], 'H5D_CHUNKED')
        self.assertEqual(layout['dims'], [100, 100])
        self.assertTrue('allocTime' in creationProps)
        self.assertEqual(creationProps['allocTime'], 'H5D_ALLOC_TIME_INCR')
        self.assertTrue('filters' in creationProps)
        
        filters = creationProps['filters']
        self.assertEqual(len(filters), 2)
        
        shuffle_filter = filters[0]
        self.assertTrue('id' in shuffle_filter)
        self.assertEqual(shuffle_filter['id'], 2)
        self.assertTrue('class' in shuffle_filter)
        self.assertEqual(shuffle_filter['class'], 'H5Z_FILTER_SHUFFLE')
        self.assertTrue('name' in shuffle_filter)
        self.assertEqual(shuffle_filter['name'], 'shuffle')
        
        deflate_filter = filters[1]
        self.assertTrue('id' in deflate_filter)
        self.assertEqual(deflate_filter['id'], 1)
        self.assertTrue('class' in deflate_filter)
        self.assertEqual(deflate_filter['class'], 'H5Z_FILTER_DEFLATE')
        self.assertTrue('level' in deflate_filter)
        self.assertEqual(deflate_filter['level'], 9)
        self.assertTrue('name' in deflate_filter)
        self.assertEqual(deflate_filter['name'], 'deflate')
        
        # dset3
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset3') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid  
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('creationProperties' in rspJson)
        creationProps = rspJson['creationProperties']
        self.assertTrue('fillTime' in creationProps)
        self.assertEqual(creationProps['fillTime'], 'H5D_FILL_TIME_ALLOC')
        self.assertTrue('layout' in creationProps)
        layout = creationProps['layout']
        self.assertEqual(layout['class'], 'H5D_CHUNKED')
        self.assertEqual(layout['dims'], [100, 100])
        self.assertTrue('allocTime' in creationProps)
        self.assertEqual(creationProps['allocTime'], 'H5D_ALLOC_TIME_INCR')
        self.assertTrue('filters' in creationProps)
        
        filters = creationProps['filters']
        self.assertEqual(len(filters), 3)
        
        fletcher_filter = filters[0]
        self.assertTrue('id' in fletcher_filter)
        self.assertEqual(fletcher_filter['id'], 3)
        self.assertTrue('class' in fletcher_filter)
        self.assertEqual(fletcher_filter['class'], 'H5Z_FILTER_FLETCHER32')
        self.assertTrue('name' in fletcher_filter)
        self.assertEqual(fletcher_filter['name'], 'fletcher32')
        
        shuffle_filter = filters[1]
        self.assertTrue('id' in shuffle_filter)
        self.assertEqual(shuffle_filter['id'], 2)
        self.assertTrue('class' in shuffle_filter)
        self.assertEqual(shuffle_filter['class'], 'H5Z_FILTER_SHUFFLE')
        self.assertTrue('name' in shuffle_filter)
        self.assertEqual(shuffle_filter['name'], 'shuffle')
        
        deflate_filter = filters[2]
        self.assertTrue('id' in deflate_filter)
        self.assertEqual(deflate_filter['id'], 1)
        self.assertTrue('class' in deflate_filter)
        self.assertEqual(deflate_filter['class'], 'H5Z_FILTER_DEFLATE')
        self.assertTrue('level' in deflate_filter)
        self.assertEqual(deflate_filter['level'], 9)
        self.assertTrue('name' in deflate_filter)
        self.assertEqual(deflate_filter['name'], 'deflate')
        
    def testGetFilters(self):
        #
        # map of filter properties we expect to get
        #
        filter_props = {"h5ex_d_checksum": [{'id': 3},], 
            "h5ex_d_gzip":  [{'id': 1, 'level': 9},], 
            "h5ex_d_nbit":  [{'id': 5},],
            "h5ex_d_shuffle":  [{'id': 2}, {'id': 1, 'level': 9}], 
            "h5ex_d_sofloat":  [{'id': 6},], 
            "h5ex_d_soint":  [{'id': 6, 'scaleType': 'H5Z_SO_INT'},],
            "h5ex_d_unlimgzip":  [{'id': 1, 'level': 9},] }
            
            
        for domain_val in filter_props.keys():
            domain = domain_val + '.' + config.get('domain')  
            #print "domain", domain_val
            headers = {'host': domain}
            root_uuid = helper.getRootUUID(domain)
        
            dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
            req = helper.getEndpoint() + "/datasets/" + dset_uuid  
            rsp = requests.get(req, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.assertTrue('creationProperties' in rspJson)
            creationProps = rspJson['creationProperties']
            self.assertTrue('filters' in creationProps)
            filters = creationProps['filters']
            num_filters = len(filters)
            ref_vals = filter_props[domain_val]
            # check we got the expected number of filters
            self.assertTrue(num_filters, len(ref_vals))
            
            for i in range(num_filters):
                #print "filter:", i
                filter_prop = filters[i]
                #print "filter_prop", filter_prop
                ref_val = ref_vals[i]
                # check filter property values are correct
                for k in ref_val.keys():
                    #print "checking key:", k
                    self.assertTrue(k in filter_prop)
                    self.assertEqual(filter_prop[k], ref_val[k])
             
        
        
    def testPost(self):
        domain = 'newdset.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        payload = {'type': 'H5T_IEEE_F32LE', 'shape': 10}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
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
        self.assertEqual(rsp.status_code, 201)
        
        # verify we can read the dataset back
        req = self.endpoint + "/datasets/" + dset_uuid
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        # verify type class is float
        rsp_type = rspJson['type']
        self.assertEqual(rsp_type['class'], 'H5T_FLOAT')
        
    def testPostScalar(self):
        domain = 'newscalar.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        str_type = { 'charSet':   'H5T_CSET_ASCII', 
                     'class':  'H5T_STRING', 
                     'strPad': 'H5T_STR_NULLPAD', 
                     'length': 40}
        payload = {'type': str_type}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
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
        self.assertEqual(rsp.status_code, 201)
        
        # verify the dataspace is scalar
        req = self.endpoint + "/datasets/" + dset_uuid
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SCALAR')
        # verify type class is string
        rsp_type = rspJson['type']
        self.assertEqual(rsp_type['class'], 'H5T_STRING')
    
        
    def testPostNullSpace(self):
        domain = 'newnullspace.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        payload = {'type': 'H5T_IEEE_F32LE', 'shape': 'H5S_NULL'}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
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
        self.assertEqual(rsp.status_code, 201)
        
        # verify the dataspace is has a null dataspace
        req = self.endpoint + "/datasets/" + dset_uuid
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_NULL')
        # verify type class is string
        type_json = rspJson['type']
        self.assertEqual(type_json['class'], 'H5T_FLOAT')
    
         
    def testPostZeroDim(self):
        domain = 'new0d.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        payload = {'type': 'H5T_STD_I32LE', 'shape': (1,)}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
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
        self.assertEqual(rsp.status_code, 201)
        
        # verify the dataspace is one dimensional/one-element
        req = self.endpoint + "/datasets/" + dset_uuid
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 1)  
        
        
    def testPostTypes(self):
        domain = 'datatypes.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        root_uuid = helper.getRootUUID(domain)
        
        # todo - add 8-bit types to list:
        #  'H5T_STD_I8',   'H5T_STD_U8'
        # See https://github.com/HDFGroup/h5serv/issues/51
        
        datatypes = ( 'H5T_STD_I16',  'H5T_STD_U16',    
                      'H5T_STD_I32',  'H5T_STD_U32',   
                      'H5T_STD_I64',  'H5T_STD_U64',  
                      'H5T_IEEE_F32', 'H5T_IEEE_F64' )
                      
        endianess = ('LE', 'BE')
        
        for datatype in datatypes:
            for endian in endianess:  
                payload = {'type': datatype+endian, 'shape': 10}
                req = self.endpoint + "/datasets"
                rsp = requests.post(req, data=json.dumps(payload), headers=headers)
                self.assertEqual(rsp.status_code, 201)  # create dataset
                rspJson = json.loads(rsp.text)
                dset_uuid = rspJson['id']
                self.assertTrue(helper.validateId(dset_uuid))
         
                # link new dataset using the type name
                name = datatype + endian
                req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
                payload = {"id": dset_uuid}
                headers = {'host': domain}
                rsp = requests.put(req, data=json.dumps(payload), headers=headers)
                self.assertEqual(rsp.status_code, 201)
            
                # Do a GET on the datasets we just created
                req = helper.getEndpoint() + "/datasets/" + dset_uuid
                rsp = requests.get(req, headers=headers)
                self.assertEqual(rsp.status_code, 200)
                rspJson = json.loads(rsp.text)
                # verify the type
                self.assertTrue('type' in rspJson)
                type_json = rspJson['type']
                self.assertTrue(type_json['class'] in ('H5T_FLOAT', 'H5T_INTEGER'))
                self.assertEqual(type_json['base'], datatype+endian)      
                     
    def testPostCompoundType(self):
        domain = 'compound.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        root_uuid = helper.getRootUUID(domain)
        
        fields = ({'name': 'temp', 'type': 'H5T_STD_I32LE'}, 
                    {'name': 'pressure', 'type': 'H5T_IEEE_F32LE'}) 
        datatype = {'class': 'H5T_COMPOUND', 'fields': fields }
        payload = {'type': datatype, 'shape': 10}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dset_uuid))
         
        # link the new dataset 
        name = "dset"
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {"id": dset_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)
        
    def testPostCompoundArrayVLenStringType(self):
        domain = 'compound_array_vlen_string.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        root_uuid = helper.getRootUUID(domain)
        
        fields = [ {"type": {"class": "H5T_INTEGER", "base": "H5T_STD_U64BE"}, "name": "VALUE1"}, 
                   {"type": {"class": "H5T_FLOAT", "base": "H5T_IEEE_F64BE"}, "name": "VALUE2"}, 
                   {"type": {"class": "H5T_ARRAY", "dims": [8], "base": 
                         {"class": "H5T_STRING", "charSet": "H5T_CSET_ASCII",
                          "strPad": "H5T_STR_NULLTERM", "length": "H5T_VARIABLE"}}, "name": "VALUE3"}]
                           
        datatype = {'class': 'H5T_COMPOUND', 'fields': fields }
        payload = {'type': datatype, 'shape': 5}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dset_uuid))
         
        # link the new dataset 
        name = "dset"
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {"id": dset_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)
        
    def testPostCompoundFillValue(self):
        domain = 'compound_fillvalue.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        root_uuid = helper.getRootUUID(domain)
        
        fields = ({'name': 'temp', 'type': 'H5T_STD_I32LE'}, 
                    {'name': 'pressure', 'type': 'H5T_IEEE_F32LE'}) 
        datatype = {'class': 'H5T_COMPOUND', 'fields': fields }
        payload = {'type': datatype, 'shape': 10}
        payload['creationProperties'] = {'fillValue': [42, 3.12] }
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dset_uuid))
         
        # link the new dataset 
        name = "dset"
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {"id": dset_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)
        
    def testPostCompoundArray(self):
        domain = 'compound_array.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        root_uuid = helper.getRootUUID(domain)
        
        fields = ({'name': 'temp', 'type': 'H5T_STD_I32LE'}, 
                    {'name': '2x2', 'type': { 'class': 'H5T_ARRAY', 'dims': [2,2],
                    'base': 'H5T_IEEE_F32LE'} }) 
        datatype = {'class': 'H5T_COMPOUND', 'fields': fields }
        
         
        payload = {'type': datatype, 'shape': 2 }
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dset_uuid))
         
        # link the new dataset 
        name = "dset"
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {"id": dset_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)
        
    def testPostCommittedType(self):
        domain = 'committedtype.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        # create the datatype
        payload = {'type': 'H5T_IEEE_F32LE'}
        req = self.endpoint + "/datatypes"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create datatype
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
        self.assertEqual(rsp.status_code, 201)
        
        # create the dataset
        payload = {'type': dtype_uuid, 'shape': [10, 10]}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dset_uuid))
         
        # link new dataset as 'dset1'
        name = 'dset1'
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {"id": dset_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)

        # Verify the dataset type
        req = self.endpoint + "/datasets/" + dset_uuid + "/type"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue("type" in rspJson)
        rsp_type = rspJson["type"]
        self.assertEqual(rsp_type["base"], 'H5T_IEEE_F32LE')
        self.assertEqual(rsp_type["class"], 'H5T_FLOAT')


    def testPostObjReference(self):
        domain = 'objref.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain

        datatype = {'class': 'H5T_REFERENCE', 'base': 'H5T_STD_REF_OBJ' }
        payload = {'type': datatype, 'shape': (1,)}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
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
        self.assertEqual(rsp.status_code, 201)

        
    def testPostArray(self):
        domain = 'newarraydset.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        datatype = {'class': 'H5T_ARRAY', 'base': 'H5T_STD_I64LE', 'dims': (3, 5) }
        
        payload = {'type': datatype, 'shape': 10}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
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
        self.assertEqual(rsp.status_code, 201)
        
        
    def testPostResizable(self):
        domain = 'resizabledset.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        payload = {'type': 'H5T_IEEE_F32LE', 'shape': 10, 'maxdims': 20}
        payload['creationProperties'] = {'fillValue': 3.12 }
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
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
        self.assertEqual(rsp.status_code, 201)
        
        # verify type and shape
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        type_json = rspJson['type']
        self.assertEqual(type_json['class'], 'H5T_FLOAT')
        self.assertEqual(type_json['base'], 'H5T_IEEE_F32LE')
        shape = rspJson['shape']
        self.assertEqual(shape['class'], 'H5S_SIMPLE')
        
        self.assertEqual(len(shape['dims']), 1)
        self.assertEqual(shape['dims'][0], 10)  
        self.assertTrue('maxdims' in shape)
        self.assertEqual(shape['maxdims'][0], 20)
        
        # create a datataset with unlimited dimension
        payload = {'type': 'H5T_IEEE_F32LE', 'shape': 10, 'maxdims': 0}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
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
        self.assertEqual(rsp.status_code, 201)     
        
    def testPostInvalidType(self):
        domain = 'tall.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        payload = {'type': 'badtype', 'shape': 10}
        headers = {'host': domain}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 400)
        
    def testPostInvalidShape(self):
        domain = 'tall.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        payload = {'type': 'H5T_STD_I32LE', 'shape': -5}
        headers = {'host': domain}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 400)
        
    def testPostNoBody(self):
        domain = 'tall.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        headers = {'host': domain}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, headers=headers)
        self.assertEqual(rsp.status_code, 400)
        
    def testPostWithLink(self):
        domain = 'newdsetwithlink.datasettest.' + config.get('domain')
        
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        root_uuid = helper.getRootUUID(domain)
        
        type_vstr = {"charSet": "H5T_CSET_ASCII", 
            "class": "H5T_STRING", 
            "strPad": "H5T_STR_NULLTERM", 
            "length": "H5T_VARIABLE" } 
        payload = {'type': type_vstr, 'shape': 10,
             'link': {'id': root_uuid, 'name': 'linked_dset'} }
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dset_uuid))
        
    def testPostCreationProps(self):
        domain = 'newdset_creationprops.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        creation_props = { 'allocTime': 'H5D_ALLOC_TIME_INCR',
                           'fillTime': 'H5D_FILL_TIME_NEVER',
                           'layout': {'class': 'H5D_CHUNKED', 'dims': [10, 10] }}
        payload = {'type': 'H5T_IEEE_F32LE', 'shape': (100, 100), 'creationProperties': creation_props }
                                                           
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
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
        self.assertEqual(rsp.status_code, 201)
        
        # read back the dataset and verify the creation props are returned
        req = self.endpoint + "/datasets/" + dset_uuid
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('creationProperties' in rspJson)
        creationProps = rspJson['creationProperties']
        
        self.assertTrue('allocTime' in creationProps)
        self.assertEqual(creationProps['allocTime'], 'H5D_ALLOC_TIME_INCR')
        self.assertTrue('fillTime' in creationProps)
        self.assertEqual(creationProps['fillTime'], 'H5D_FILL_TIME_NEVER')
        self.assertTrue('layout' in creationProps)
        layout = creationProps['layout']
        self.assertTrue('class' in layout)
        self.assertEqual(layout['class'], 'H5D_CHUNKED')
        self.assertTrue('dims' in layout)
        self.assertEqual(layout['dims'], [10, 10])
        self.assertEqual(len(creationProps.keys()), 3)  # just return what we set
    
    def testInvalidCreationProps(self):
        domain = 'newdset_badcreationprops.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        creation_props = { 'layout': {'class': 'H5D_CHUNKED', 'dims': [200, 200] }}
        payload = {'type': 'H5T_IEEE_F32LE', 'shape': (100, 100), 'creationProperties': creation_props }
                                                           
        req = self.endpoint + "/datasets"
        # should fail because the chunk dimension is larger than the dataset dimensions
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 400)  # bad request
                 
        
    def testPostDeflateFilter(self):
        domain = 'newdset_gzip.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        filters = [ { 'id': 1, 'level': 9 }, ]  # deflate filter (gzip)
        creation_props = { 'layout': {'class': 'H5D_CHUNKED', 'dims': [100, 100] }, 'filters': filters }  
        payload = {'type': 'H5T_IEEE_F32LE', 'shape': (1000, 1000), 'creationProperties': creation_props }
                                                           
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
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
        self.assertEqual(rsp.status_code, 201)
        
        # read back the dataset and verify the creation props are returned
        req = self.endpoint + "/datasets/" + dset_uuid
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('creationProperties' in rspJson)
        creationProps = rspJson['creationProperties']
        
        self.assertTrue('filters' in creationProps)
        filters = creationProps['filters']
        self.assertEqual(len(filters), 1)
        filter_prop = filters[0]
        self.assertTrue('id' in filter_prop)
        self.assertEqual(filter_prop['id'], 1)
        self.assertTrue('class' in filter_prop)
        self.assertEqual(filter_prop['class'], 'H5Z_FILTER_DEFLATE')
        self.assertTrue('level' in filter_prop)
        self.assertEqual(filter_prop['level'], 9)
        self.assertTrue('layout' in creationProps)
        # should see chunks returned, even though it was specified in creation
        layout = creationProps['layout']
        self.assertTrue('class' in layout)
        self.assertEqual(layout['class'], 'H5D_CHUNKED')
        self.assertTrue('dims' in layout)
         
        
    def testPostLZFFilter(self):
        domain = 'newdset_lzf.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        filters = [ { 'id': 32000}, ]  # LZF filter 
        creation_props = { 'filters': filters }  
        payload = {'type': 'H5T_IEEE_F32LE', 'shape': (1000, 1000), 'creationProperties': creation_props }
                                                           
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
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
        self.assertEqual(rsp.status_code, 201)
        
        # read back the dataset and verify the creation props are returned
        req = self.endpoint + "/datasets/" + dset_uuid
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('creationProperties' in rspJson)
        creationProps = rspJson['creationProperties']
        
        
        self.assertTrue('filters' in creationProps)
        filters = creationProps['filters']
        self.assertEqual(len(filters), 1)
        filter_prop = filters[0]
        self.assertTrue('id' in filter_prop)
        self.assertEqual(filter_prop['id'], 32000)
        self.assertTrue('class' in filter_prop)
        self.assertEqual(filter_prop['class'], 'H5Z_FILTER_LZF')
        self.assertTrue('level' not in filter_prop)
        
        self.assertTrue('layout' in creationProps)
        # should see chunks returned, even though it was specified in creation
        layout = creationProps['layout']
        self.assertTrue('class' in layout)
        self.assertEqual(layout['class'], 'H5D_CHUNKED')
        self.assertTrue('dims' in layout)
        
    def testPostSZIPFilter(self):
        domain = 'newdset_szip.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        filters = [ { 'id': 4, 'bitsPerPixel': 8, 'coding': 'H5_SZIP_EC_OPTION_MASK',
            'pixelsPerBlock': 32, 'pixelsPerScanline': 100}, ]  # SZIP filter 
        creation_props = { 'layout': {'class': 'H5D_CHUNKED', 'dims': (100, 100) }, 'filters': filters }  
        payload = {'type': 'H5T_IEEE_F32LE', 'shape': (1000, 1000), 'creationProperties': creation_props }
                                                              
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
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
        self.assertEqual(rsp.status_code, 201)
        
        # read back the dataset and verify the creation props are returned
        req = self.endpoint + "/datasets/" + dset_uuid
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('creationProperties' in rspJson)
        creationProps = rspJson['creationProperties']
        
        
        self.assertTrue('filters' in creationProps)
        filters = creationProps['filters']
        self.assertEqual(len(filters), 1)
        filter_prop = filters[0]
        self.assertTrue('id' in filter_prop)
        self.assertEqual(filter_prop['id'], 4)
        self.assertTrue('class' in filter_prop)
        self.assertEqual(filter_prop['class'], 'H5Z_FILTER_SZIP')
        self.assertTrue('level' not in filter_prop)
        self.assertTrue('bitsPerPixel' in filter_prop)
        self.assertEqual(filter_prop['bitsPerPixel'], 8)
        self.assertTrue('coding' in filter_prop)
        self.assertEqual(filter_prop['coding'], 'H5_SZIP_EC_OPTION_MASK')
        
        self.assertTrue('layout' in creationProps)
        # should see chunks returned, even though it was specified in creation
        layout = creationProps['layout']
        self.assertTrue('class' in layout)
        self.assertEqual(layout['class'], 'H5D_CHUNKED')
        self.assertTrue('dims' in layout)
              
       
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
        self.assertEqual(rsp.status_code, 200)
        # verify that a GET on the dataset fails
        req = helper.getEndpoint() + "/datasets/" + d112_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 410)
    
        
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
        self.assertEqual(rsp.status_code, 200)
        # now delete the dataset
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        # verify that a GET on the dataset fails
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 410)
        
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
        self.assertEqual(rsp.status_code, 200)
        
        # verify that a GET on the dataset succeeds still
        req = helper.getEndpoint() + "/datasets/" + d22_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        
        # delete dataset...
        req = self.endpoint + "/datasets/" + d22_uuid
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        
        # verify that a GET on the dataset fails
        req = helper.getEndpoint() + "/datasets/" + d22_uuid
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 410)
        
    def testDeleteBadUUID(self):
        domain = 'tall_dset112_deleted.' + config.get('domain')    
        req = self.endpoint + "/datasets/dff53814-2906-11e4-9f76-3c15c2da029e"
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 404)
        
    def testGetCollection(self):
        for domain_name in ('tall', 'tall_ro'):
            domain = domain_name + '.' + config.get('domain')    
            req = self.endpoint + "/datasets"
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            datasetIds = rspJson["datasets"]
            
            self.assertEqual(len(datasetIds), 4)
            for uuid in datasetIds:
                self.assertTrue(helper.validateId(uuid))
                
    def testGetCollectionBatch(self):
        domain = 'dset1k.' + config.get('domain')   
        req = self.endpoint + "/datasets" 
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
            dsetIds = rspJson['datasets']
            self.assertEqual(len(dsetIds) <= 50, True)
            for dsetId in dsetIds:
                uuids.add(dsetId)
                last_uuid = dsetId
            if len(dsetIds) == 0:
                break
        self.assertEqual(len(uuids), 1000)  # should get 1000 unique uuid's 
        
if __name__ == '__main__':
    unittest.main()
