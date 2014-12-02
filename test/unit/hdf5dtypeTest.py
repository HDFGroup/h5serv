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
import unittest
import logging
import numpy as np
import sys
from h5py import special_dtype

sys.path.append('../../server')
import hdf5dtype 


class Hdf5dtypeTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Hdf5dtypeTest, self).__init__(*args, **kwargs)
        # main
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        
    def testBaseIntegerTypeItem(self):
        dt = np.dtype('<i1')
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_INTEGER')
        self.failUnlessEqual(typeItem['size'], 1)
        self.failUnlessEqual(typeItem['base_size'], 1)
        self.failUnlessEqual(typeItem['order'], 'H5T_ORDER_LE')
        self.failUnlessEqual(typeItem['base'], 'H5T_STD_I8LE')
        
    def testBaseFloatTypeItem(self):
        dt = np.dtype('<f8')
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_FLOAT')
        self.failUnlessEqual(typeItem['size'], 8)
        self.failUnlessEqual(typeItem['base_size'], 8)
        self.failUnlessEqual(typeItem['order'], 'H5T_ORDER_LE')
        self.failUnlessEqual(typeItem['base'], 'H5T_IEEE_F64LE')
        typeItem = hdf5dtype.getTypeResponse(typeItem) # non-verbose format
        self.failUnlessEqual(typeItem, 'H5T_IEEE_F64LE')
        
    def testBaseStringTypeItem(self):
        dt = np.dtype('S3')
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_STRING')
        self.failUnlessEqual(typeItem['size'], 3)
        self.failUnlessEqual(typeItem['base_size'], 3)
        self.failUnlessEqual(typeItem['strsize'], 3)
        self.failUnlessEqual(typeItem['order'], 'H5T_ORDER_NONE')
        self.failUnlessEqual(typeItem['strpad'], 'H5T_STR_NULLPAD')
        self.failUnlessEqual(typeItem['cset'], 'H5T_CSET_ASCII')
        
    def testBaseVLenAsciiTypeItem(self):
        dt = special_dtype(vlen=str)
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_STRING')
        self.failUnlessEqual(typeItem['base_size'], 8)
        self.failUnlessEqual(typeItem['strsize'], 'H5T_VARIABLE')
        self.failUnlessEqual(typeItem['order'], 'H5T_ORDER_NONE')
        self.failUnlessEqual(typeItem['strpad'], 'H5T_STR_NULLTERM')
        self.failUnlessEqual(typeItem['cset'], 'H5T_CSET_ASCII')
        
    def testBaseVLenUnicodeTypeItem(self):
        dt = special_dtype(vlen=unicode)
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_STRING')
        self.failUnlessEqual(typeItem['base_size'], 8)
        self.failUnlessEqual(typeItem['strsize'], 'H5T_VARIABLE')
        self.failUnlessEqual(typeItem['order'], 'H5T_ORDER_NONE')
        self.failUnlessEqual(typeItem['strpad'], 'H5T_STR_NULLTERM')
        self.failUnlessEqual(typeItem['cset'], 'H5T_CSET_UTF8')
        
    def testBaseEnumTypeItem(self):
        mapping = {'RED': 0, 'GREEN': 1, 'BLUE': 2}
        dt = special_dtype(enum=(np.int8, mapping) )
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_ENUM')
        self.failUnlessEqual(typeItem['size'], 1)
        self.failUnlessEqual(typeItem['base_size'], 1)
        self.failUnlessEqual(typeItem['order'], 'H5T_ORDER_LE')
        self.failUnlessEqual(typeItem['base'], 'H5T_STD_I8LE')
        self.assertTrue('mapping' in typeItem)
        self.failUnlessEqual(typeItem['mapping']['GREEN'], 1)
        
    def testBaseArrayTypeItem(self):
        dt = np.dtype('(2,2)<int32')
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_ARRAY')
        self.failUnlessEqual(typeItem['size'], 16)
        self.failUnlessEqual(typeItem['base_size'], 4)
        self.failUnlessEqual(typeItem['order'], 'H5T_ORDER_LE')
        self.failUnlessEqual(typeItem['base'], 'H5T_STD_I32LE')
        
    def testOpaqueTypeItem(self):
        dt = np.dtype('V200')
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_OPAQUE')
        self.failUnlessEqual(typeItem['size'], 200)
        self.failUnlessEqual(typeItem['base_size'], 200)
        self.failUnlessEqual(typeItem['order'], 'H5T_ORDER_NONE')
        self.assertTrue('base' not in typeItem)
        
    def testVlenDataItem(self):
        dt = special_dtype(vlen=np.dtype('int32')) 
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_VLEN')
        self.failUnlessEqual(typeItem['size'], 'H5T_VARIABLE')
        self.failUnlessEqual(typeItem['base_size'], 8)
        self.failUnlessEqual(typeItem['order'], 'H5T_ORDER_LE')
        self.failUnlessEqual(typeItem['base'], 'H5T_STD_I32LE')
        
    def testCompoundTypeItem(self): 
        dt = np.dtype([("temp", np.float32), ("pressure", np.float32), ("wind", np.int16)])
        typeItem = hdf5dtype.getTypeItem(dt)
        self.assertEqual(typeItem['class'], 'H5T_COMPOUND')
        self.assertTrue('fields' in typeItem)
        fields = typeItem['fields']
        self.assertEqual(len(fields), 3)
        tempField = fields[0]
        self.assertEqual(tempField['name'], 'temp')
        self.assertTrue('type' in tempField)
        tempFieldType = tempField['type']
        self.assertEqual(tempFieldType['class'], 'H5T_FLOAT')
        self.failUnlessEqual(tempFieldType['size'], 4)
        self.failUnlessEqual(tempFieldType['base_size'], 4)
        self.failUnlessEqual(tempFieldType['order'], 'H5T_ORDER_LE')
        self.failUnlessEqual(tempFieldType['base'], 'H5T_IEEE_F32LE')   
        
        typeItem = hdf5dtype.getTypeResponse(typeItem) # non-verbose format  
        self.assertEqual(typeItem['class'], 'H5T_COMPOUND')
        self.assertTrue('fields' in typeItem)
        fields = typeItem['fields']
        self.assertEqual(len(fields), 3)
        tempField = fields[0]
        self.assertEqual(tempField['name'], 'temp')
        self.assertTrue('type' in tempField)
        self.failUnlessEqual(tempField['type'], 'H5T_IEEE_F32LE')  
        
    def testCreateBaseType(self):
        dt = hdf5dtype.createDataType('H5T_STD_UI32BE') 
        self.assertEqual(dt.name, 'uint32')
        self.assertEqual(dt.byteorder, '>')
        self.assertEqual(dt.kind, 'u')
        
        dt = hdf5dtype.createDataType('H5T_STD_I16LE')  
        self.assertEqual(dt.name, 'int16')
        self.assertEqual(dt.kind, 'i')
        
        dt = hdf5dtype.createDataType('H5T_IEEE_F64LE')                            
        self.assertEqual(dt.name, 'float64')
        self.assertEqual(dt.kind, 'f')
        
        dt = hdf5dtype.createDataType('H5T_IEEE_F32LE')                              
        self.assertEqual(dt.name, 'float32')
        self.assertEqual(dt.kind, 'f')
        
        typeItem = { 'class': 'H5T_INTEGER', 'base': 'H5T_STD_I32BE' }
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'int32')
        self.assertEqual(dt.kind, 'i')
          
        
    def testCreateBaseStringType(self):
        typeItem = { 'class': 'H5T_STRING', 'cset': 'H5T_CSET_ASCII', 'strsize': 6 }
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'string48')
        self.assertEqual(dt.kind, 'S')
        
    def testCreateVLenStringType(self):
        typeItem = { 'class': 'H5T_STRING', 'cset': 'H5T_CSET_ASCII', 'strsize': 'H5T_VARIABLE' }
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'object')
        self.assertEqual(dt.kind, 'O')
        
        typeItem = { 'class': 'H5T_STRING', 'cset': 'H5T_CSET_UTF8', 'strsize': 'H5T_VARIABLE' }
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'object')
        self.assertEqual(dt.kind, 'O')
        
    def testCreateVLenDataType(self):
        typeItem = { 'class': 'H5T_VLEN', 'base': 'H5T_STD_I32BE' }
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'object')
        self.assertEqual(dt.kind, 'O')
        
    def testCreateOpaqueType(self):
        typeItem = { 'class': 'H5T_OPAQUE', 'size': 200 }
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'void1600')
        self.assertEqual(dt.kind, 'V')
        
    def testCreateCompoundType(self):
        typeItem = {'class': 'H5T_COMPOUND', 'fields': 
                [{'name': 'temp',     'type': 'H5T_IEEE_F32LE'},
                 {'name': 'pressure', 'type': 'H5T_IEEE_F32LE'}, 
                 {'name': 'wind',     'type': 'H5T_STD_I16LE'} ] }
        
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'void80')
        self.assertEqual(dt.kind, 'V')
        self.assertEqual(len(dt.fields), 3)
        
    def testCreateCompoundTypeUnicodeFields(self):
        typeItem = {'class': 'H5T_COMPOUND', 'fields': 
                [{'name': u'temp',     'type': 'H5T_IEEE_F32LE'},
                 {'name': u'pressure', 'type': 'H5T_IEEE_F32LE'}, 
                 {'name': u'wind',     'type': 'H5T_STD_I16LE'} ] }
        
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'void80')
        self.assertEqual(dt.kind, 'V')
        self.assertEqual(len(dt.fields), 3)  
        
    def testCreateArrayType(self):
        typeItem = {'class': 'H5T_ARRAY', 
                    'base': 'H5T_STD_I64LE', 
                    'shape': (3, 5) }   
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'void960')
        self.assertEqual(dt.kind, 'V')
        
    def testCreateArrayIntegerType(self):
        typeItem = {'class': 'H5T_INTEGER', 
                    'base': 'H5T_STD_I64LE', 
                    'shape': (3, 5) }   
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'void960')
        self.assertEqual(dt.kind, 'V')
        
if __name__ == '__main__':
    #setup test files
    
    unittest.main()
    

 



