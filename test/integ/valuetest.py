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

import six
import requests
import config
import helper
import unittest
import json
import base64
 

class ValueTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(ValueTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))  
    
    """
     Test 32-bit memory word at given offset from value against expected.
     Expected must be less than 256.
    """  
    def compareWord32(self, value, offset, expected):
        if six.PY3:
            self.assertEqual(value[offset+0], 0)
            self.assertEqual(value[offset+1], 0)
            self.assertEqual(value[offset+2], 0)
            self.assertEqual(value[offset+3], expected)
        else:
            self.assertEqual(ord(value[offset+0]), 0)
            self.assertEqual(ord(value[offset+1]), 0)
            self.assertEqual(ord(value[offset+2]), 0)
            self.assertEqual(ord(value[offset+3]), expected)
              
       
    def testGet(self):
        for domain_name in ('tall', 'tall_ro'):
            domain = domain_name + '.' + config.get('domain') 
            rootUUID = helper.getRootUUID(domain)
            g1UUID = helper.getUUID(domain, rootUUID, 'g1')
            g11UUID = helper.getUUID(domain, g1UUID, 'g1.1')
               
            # rank 1 dataset
            dset112UUID = helper.getUUID(domain, g11UUID, 'dset1.1.2') 
            req = helper.getEndpoint() + "/datasets/" + dset112UUID
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.assertEqual(rspJson['id'], dset112UUID)
            typeItem = rspJson['type']  
            self.assertEqual(typeItem['base'], 'H5T_STD_I32BE')
            shape = rspJson['shape']
            self.assertEqual(shape['class'], 'H5S_SIMPLE')
            self.assertEqual(len(shape['dims']), 1)
            self.assertEqual(shape['dims'][0], 20)  
            req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value"
            rsp = requests.get(req, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            self.assertEqual(rsp.headers['Content-Type'], "application/json")
            rspJson = json.loads(rsp.text)
            data = rspJson['value'] 
            self.assertEqual(len(data), 20)
            for i in range(20):
                self.assertEqual(data[i], i)
        
            # rank 2 dataset
            dset111UUID = helper.getUUID(domain, g11UUID, 'dset1.1.1') 
            req = helper.getEndpoint() + "/datasets/" + dset111UUID
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            
            self.assertEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.assertEqual(rspJson['id'], dset111UUID)
            typeItem = rspJson['type']  
            self.assertEqual(typeItem['base'], 'H5T_STD_I32BE')
            shape = rspJson['shape']
            self.assertEqual(shape['class'], 'H5S_SIMPLE')
            self.assertEqual(len(shape['dims']), 2)
            self.assertEqual(shape['dims'][0], 10) 
            self.assertEqual(shape['dims'][1], 10)    
            req = helper.getEndpoint() + "/datasets/" + dset111UUID + "/value"
            rsp = requests.get(req, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            self.assertEqual(rsp.headers['Content-Type'], "application/json")
            rspJson = json.loads(rsp.text)
            data = rspJson['value'] 
            self.assertEqual(len(data), 10)  
            for i in range(10):
                arr = data[i]
                self.assertEqual(len(arr), 10)
                for j in range(10):
                    self.assertEqual(arr[j], i*j)
                    
    def testGetBinary(self):
        for domain_name in ('tall', 'tall_ro'):
            domain = domain_name + '.' + config.get('domain') 
            rootUUID = helper.getRootUUID(domain)
            g1UUID = helper.getUUID(domain, rootUUID, 'g1')
            g11UUID = helper.getUUID(domain, g1UUID, 'g1.1')
               
            # rank 1 dataset
            dset112UUID = helper.getUUID(domain, g11UUID, 'dset1.1.2') 
            req = helper.getEndpoint() + "/datasets/" + dset112UUID
            headers = {'host': domain}
            headers_binary = {'host': domain, 'accept': "application/octet-stream"}
            rsp = requests.get(req, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.assertEqual(rspJson['id'], dset112UUID)
            typeItem = rspJson['type']  
            self.assertEqual(typeItem['base'], 'H5T_STD_I32BE')
            shape = rspJson['shape']
            self.assertEqual(shape['class'], 'H5S_SIMPLE')
            self.assertEqual(len(shape['dims']), 1)
            self.assertEqual(shape['dims'][0], 20)  
            req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value"
             
            rsp = requests.get(req, headers=headers_binary)
            self.assertEqual(rsp.status_code, 200)
            self.assertEqual(rsp.headers['Content-Type'], "application/octet-stream")
            
            data = rsp.content
            self.assertEqual(len(data), 80)
            for i in range(20):
                self.compareWord32(data, i*4, i)
                   
            # rank 2 dataset
            dset111UUID = helper.getUUID(domain, g11UUID, 'dset1.1.1') 
            req = helper.getEndpoint() + "/datasets/" + dset111UUID
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            
            self.assertEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.assertEqual(rspJson['id'], dset111UUID)
            typeItem = rspJson['type']  
            self.assertEqual(typeItem['base'], 'H5T_STD_I32BE')
            shape = rspJson['shape']
            self.assertEqual(shape['class'], 'H5S_SIMPLE')
            self.assertEqual(len(shape['dims']), 2)
            self.assertEqual(shape['dims'][0], 10) 
            self.assertEqual(shape['dims'][1], 10)    
            req = helper.getEndpoint() + "/datasets/" + dset111UUID + "/value"
            rsp = requests.get(req, headers=headers_binary)
            self.assertEqual(rsp.status_code, 200)
            self.assertEqual(rsp.headers['Content-Type'], "application/octet-stream")
            data = rsp.content
            self.assertEqual(len(data), 400)
            row_offset = 0
           
            for i in range(10):
                col_offset = 0
                for j in range(10):
                    # 4 byte integers, little indian
                    self.compareWord32(data, row_offset+col_offset, i*j)
                    col_offset += 4
                row_offset += col_offset
                
        
    def testGetSelection(self):
        for domain_name in ('tall', 'tall_ro'):
            domain = domain_name + '.' + config.get('domain')  
            headers = {'host': domain}
            rootUUID = helper.getRootUUID(domain)
            g1UUID = helper.getUUID(domain, rootUUID, 'g1')
            g11UUID = helper.getUUID(domain, g1UUID, 'g1.1')
               
            # rank 1 dataset
            dset112UUID = helper.getUUID(domain, g11UUID, 'dset1.1.2') 
         
            # dataset has shape (20,) and type 'int32'
        
            # get values starting at index 2
            req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?select=[2:]"
            rsp = requests.get(req, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            self.assertEqual(rsp.headers['Content-Type'], "application/json")
            rspJson = json.loads(rsp.text)
            data = rspJson['value']  # should be [2, 3, 4, ..., 19]
            self.assertEqual(len(data), 18)
            self.assertEqual(data, list(range(2, 20)))
        
            # get values starting at index 2 with stop of 10
            req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?select=[2:10]"
            rsp = requests.get(req, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            data = rspJson['value']  # should be [2, 3, 4, ..., 9]
            self.assertEqual(len(data), 8)
            self.assertEqual(data, list(range(2, 10)))
        
            # get values starting at index 2 with stop of 10, and stride of 2
            req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?select=[2:10:2]"
            rsp = requests.get(req, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            self.assertEqual(rsp.headers['Content-Type'], "application/json")
            rspJson = json.loads(rsp.text)
            data = rspJson['value']  # should be [2, 4, 6, 8]
            self.assertEqual(len(data), 4)
            self.assertEqual(data, list(range(2, 9, 2)))
        
            # rank 2 dataset
            dset111UUID = helper.getUUID(domain, g11UUID, 'dset1.1.1') 
         
            # dataset has shape (10,10) and type 'int32'
        
            # get rows 2, 3, 4, and 5
            req = helper.getEndpoint() + "/datasets/" + dset111UUID + "/value" + \
             "?select=[:,2:6]"
            rsp = requests.get(req, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            self.assertEqual(rsp.headers['Content-Type'], "application/json")
            rspJson = json.loads(rsp.text)
            data = rspJson['value']   
            self.assertEqual(len(data), 10)  
            for i in range(10):
                arr = data[i]
                self.assertEqual(len(arr), 4)
                for j in range(4):
                    self.assertEqual(arr[j], i*(j+2))
                
            # get 2d subregion with stride
            req = helper.getEndpoint() + "/datasets/" + dset111UUID + "/value" + \
             "?select=[1:9,1:9:2]"
            rsp = requests.get(req, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            self.assertEqual(rsp.headers['Content-Type'], "application/json")
            rspJson = json.loads(rsp.text)
            data = rspJson['value']   
          
            self.assertEqual(len(data), 8)  
            for i in range(8):
                arr = data[i]
                self.assertEqual(len(arr), 4)
                for j in range(4):
                    self.assertEqual(arr[j], (i+1)*(j*2+1))
                    
    def testGetSelectionBinary(self):
        for domain_name in ('tall', ):
            domain = domain_name + '.' + config.get('domain')  
            headers = {'host': domain}
            headers_binary = {'host': domain, 'accept': "application/octet-stream"}
            rootUUID = helper.getRootUUID(domain)
            g1UUID = helper.getUUID(domain, rootUUID, 'g1')
            g11UUID = helper.getUUID(domain, g1UUID, 'g1.1')
               
            # rank 1 dataset
            dset112UUID = helper.getUUID(domain, g11UUID, 'dset1.1.2') 
         
            # dataset has shape (20,) and type 'int32'
        
            # get values starting at index 2
            req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?select=[2:]"
            rsp = requests.get(req, headers=headers_binary)
            self.assertEqual(rsp.status_code, 200)
            self.assertEqual(rsp.headers['Content-Type'], "application/octet-stream")
            
            # content should be [2, 3, 4, ..., 19]
            data = rsp.content
            self.assertEqual(len(data), 18*4)  # 18 elements with 4 bytes per element
            for i in range(18):
                self.compareWord32(data, i*4, i+2)
                     
            # get values starting at index 2 with stop of 10
            req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?select=[2:10]"
            rsp = requests.get(req, headers=headers_binary)
            self.assertEqual(rsp.status_code, 200)
            self.assertEqual(rsp.headers['Content-Type'], "application/octet-stream")
             
            data = rsp.content  # should be [2, 3, 4, ..., 9]
            self.assertEqual(len(data), 8*4)
            for i in range(8):
                self.compareWord32(data, i*4, i+2)
                 
            
            # get values starting at index 2 with stop of 10, and stride of 2
            req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?select=[2:10:2]"
            rsp = requests.get(req, headers=headers_binary)
            self.assertEqual(rsp.status_code, 200)
            self.assertEqual(rsp.headers['Content-Type'], "application/octet-stream")
            data = rsp.content
            # should be [2, 4, 6, 8]
            self.assertEqual(len(data), 4*4)
            for i in range(4):
                offset = i*4
                self.compareWord32(data, offset, (i*2)+2)
                 
        
            # rank 2 dataset
            dset111UUID = helper.getUUID(domain, g11UUID, 'dset1.1.1') 
         
            # dataset has shape (10,10) and type 'int32'
            # get rows 2, 3, 4, and 5
            req = helper.getEndpoint() + "/datasets/" + dset111UUID + "/value" + \
             "?select=[:,2:6]"
            rsp = requests.get(req, headers=headers_binary)
            self.assertEqual(rsp.status_code, 200)
            self.assertEqual(rsp.headers['Content-Type'], "application/octet-stream")
            data = rsp.content
            self.assertEqual(len(data), 4*10*4)
            row_offset = 0
            for i in range(10):
                col_offset = 0
                for j in range(4):
                    # 4 byte integers, little indian
                    self.compareWord32(data, row_offset+col_offset, i*(j+2))
                     
                    col_offset += 4
                row_offset += col_offset
                    
            # get 2d subregion with stride
            req = helper.getEndpoint() + "/datasets/" + dset111UUID + "/value" + \
             "?select=[1:9,1:9:2]"
            rsp = requests.get(req, headers=headers_binary)
            self.assertEqual(rsp.status_code, 200)
            self.assertEqual(rsp.headers['Content-Type'], "application/octet-stream")
            data = rsp.content
            self.assertEqual(len(data), 8*4*4)
            row_offset = 0
            for i in range(8):
                col_offset = 0
                for j in range(4):
                    # 4 byte integers, little indian
                    self.compareWord32(data, row_offset+col_offset, (i+1)*(j*2+1))
                    col_offset += 4
                row_offset += col_offset
            
                
    def testGetSelectionBadQuery(self):
        domain = 'tall.' + config.get('domain')  
        headers = {'host': domain}
        rootUUID = helper.getRootUUID(domain)
        g1UUID = helper.getUUID(domain, rootUUID, 'g1')
        g11UUID = helper.getUUID(domain, g1UUID, 'g1.1')
               
        # rank 1 dataset
        dset112UUID = helper.getUUID(domain, g11UUID, 'dset1.1.2') 
    
        # don't use  bracket
        req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?select=abc"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 400)
        
        # not a number
        req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?select=[a:b:c]"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 400)
        
        # start is negative
        req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?select=[-1:3]"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 400)
        
        # stop past extent
        req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?select=[1:25]"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 400)
        
        # pass in 0 step
        req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?select=[1:2:0]"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 400)  
        
    def testGetScalar(self):
        domain = 'scalar.' + config.get('domain')
        headers = {'host': domain}  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, '0d') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.headers['Content-Type'], "application/json")
        rspJson = json.loads(rsp.text)
        data = rspJson['value'] 
        self.assertEqual(data, 42)
        
    def testGetNullSpace(self):
        domain = 'null_space_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('value' in rspJson)
        data = rspJson['value'] 
        self.assertEqual(data, None)
         
        
    def testGetScalarString(self):
        domain = 'scalar.' + config.get('domain')  
        headers = {'host': domain}
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, '0ds') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.headers['Content-Type'], "application/json")
        rspJson = json.loads(rsp.text)
        data = rspJson['value'] 
        self.assertEqual(data, "hello")
        
    def testGetScalarStringBinary(self):
        domain = 'scalar.' + config.get('domain')  
        headers = {'host': domain}
        headers_binary = {'host': domain, 'accept': "application/octet-stream"}
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, '0ds') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        rsp = requests.get(req, headers=headers_binary)
        self.assertEqual(rsp.status_code, 200)
        # requested binary, but got json (because it's a variable length string)
        self.assertEqual(rsp.headers['Content-Type'], "application/json")
        rspJson = json.loads(rsp.text)
        data = rspJson['value'] 
        self.assertEqual(data, "hello")
        
    def testGetSimpleOneElement(self):
        domain = 'scalar.' + config.get('domain') 
        headers = {'host': domain} 
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, '1d') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        data = rspJson['value'] 
        self.assertEqual(data, [42,])
        
    def testGetSimpleOneElementString(self):
        domain = 'scalar.' + config.get('domain') 
        headers = {'host': domain} 
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, '1ds') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        data = rspJson['value'] 
        self.assertEqual(data, ["hello",])
        
        
    def testGetCompound(self):
        domain = 'compound.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.headers['Content-Type'], "application/json")
        rspJson = json.loads(rsp.text)
        data = rspJson['value'] 
        self.assertEqual(len(data), 72)
        first = data[0]
        self.assertEqual(len(first), 5)
        self.assertEqual(first[0], 24) 
        self.assertEqual(first[1], "13:53")  
        # get first element via selection query
        # get values starting at index 2
        req += "?select=[0:1]"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.headers['Content-Type'], "application/json")
        rspJson = json.loads(rsp.text)
        data = rspJson['value'] 
        self.assertEqual(len(data), 1)
        first = data[0]
        self.assertEqual(len(first), 5)
        self.assertEqual(first[0], 24) 
        self.assertEqual(first[1], "13:53")
        
    def testGetCompoundBinary(self):
        domain = 'compound.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        headers = {'host': domain}
        headers_binary = {'host': domain, 'accept': "application/octet-stream"}
        rsp = requests.get(req, headers=headers_binary)
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.headers['Content-Type'], "application/octet-stream")
        data = rsp.content
        self.assertEqual(len(data) // 36, 72 )
        
 
        # get first element via selection query
        # get values starting at index 2
        req += "?select=[0:1]"
        rsp = requests.get(req, headers=headers_binary)
        self.assertEqual(rsp.status_code, 200)
        # just one element, so expect json response
        self.assertEqual(rsp.headers['Content-Type'], "application/json")
        rspJson = json.loads(rsp.text)
        data = rspJson['value'] 
        self.assertEqual(len(data), 1)
        first = data[0]
        self.assertEqual(len(first), 5)
        self.assertEqual(first[0], 24) 
        self.assertEqual(first[1], "13:53")
       
        
    def testGetCommitted(self):
        domain = 'committed_type.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        data = rspJson['value'] 
        self.assertEqual(len(data), 4)
         
        
    def testGetArray(self):
        domain = 'array_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('value' in rspJson)
        value = rspJson['value']
        self.assertEqual(len(value), 4)  # four dataset elements (each an array)
        self.assertEqual(len(value[0]), 3)  # 3x5 array shape
        self.assertEqual(len((value[0])[0]), 5)  # 3x5 array shape
        self.assertEqual(value[0][2][4], -8)  # pull out a value from the array
        
    def testGetVLenString(self):
        domain = 'vlen_string_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        rspJson = json.loads(rsp.text)
        self.assertTrue('value' in rspJson)
        value = rspJson['value']
        self.assertEqual(len(value), 4) 
        self.assertEqual(value[0], "Parting")
        self.assertEqual(value[1], "is such")
        self.assertEqual(value[2], "sweet")
        self.assertEqual(value[3], "sorrow.")
        
    def testGetFixedString(self):
        domain = 'fixed_string_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
       
        self.assertTrue('value' in rspJson)
        value = rspJson['value']
        self.assertEqual(len(value), 4) 
        self.assertEqual(value[0], "Parting")
        self.assertEqual(value[1], "is such")
        self.assertEqual(value[2], "sweet")
        self.assertEqual(value[3], "sorrow.")

    def testGetFixedStringBinary(self):
        domain = 'fixed_string_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        headers = {'host': domain, 'accept': "application/octet-stream"}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.headers['Content-Type'], "application/octet-stream")
        data = rsp.content
        self.assertEqual(data, b"Partingis suchsweet\x00\x00sorrow.")
         
        
    def testGetEnum(self):
        domain = 'enum_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('value' in rspJson)
        value = rspJson['value']
        self.assertEqual(len(value), 4) 
        self.assertEqual(value[1][2], 2)
        
    def testGetVlen(self):
        domain = 'vlen_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('value' in rspJson)
        value = rspJson['value']
        self.assertEqual(len(value), 2)
        self.assertEqual(len(value[1]), 12)
        self.assertEqual(value[1][11], 144)
        
    def testGetOpaque(self):
        domain = 'opaque_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        # get for Opaque data is not supported yet.  Check that the call returns 501
        self.assertEqual(rsp.status_code, 501)
        
    def testGetObjectReference(self):
        domain = 'objref_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        ds1_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        ds2_uuid = helper.getUUID(domain, root_uuid, 'DS2') 
        g1_uuid = helper.getUUID(domain, root_uuid, 'G1') 
        req = helper.getEndpoint() + "/datasets/" + ds1_uuid  + "/value"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
         
        self.assertTrue('value' in rspJson)
        value = rspJson['value']
        self.assertEqual(len(value), 2)
        self.assertEqual(value[0], 'groups/' + g1_uuid)
        self.assertEqual(value[1], 'datasets/' + ds2_uuid)
        
    def testGetNullObjReference(self):
        domain = 'null_objref_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('value' in rspJson)
        value = rspJson['value']
        self.assertEqual(len(value), 1)
        self.assertEqual(value[0], "null")
        
    def testGetRegionReference(self):
        domain = 'regionref_dset.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        ds1_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        ds2_uuid = helper.getUUID(domain, root_uuid, 'DS2')
        req = helper.getEndpoint() + "/datasets/" + ds1_uuid + "/value"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('value' in rspJson) 
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
        self.assertEqual(hyperslabs[0][1], [1, 3])
        self.assertEqual(hyperslabs[1][0], [0, 11])
        self.assertEqual(hyperslabs[1][1], [1, 14])
        self.assertEqual(hyperslabs[2][0], [2, 0])
        self.assertEqual(hyperslabs[2][1], [3, 3])
        self.assertEqual(hyperslabs[3][0], [2, 11])
        self.assertEqual(hyperslabs[3][1], [3, 14])

    def testGetFillValue(self):
        domain = 'fillvalue.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)

        # create a new dataset
        payload = {'type': 'H5T_STD_I32LE', 'shape': 10}
        payload['creationProperties'] = {'fillValue': 42 }
        req = self.endpoint + "/datasets"
        headers = {'host': domain}
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset_uuid = rspJson['id']
        self.assertTrue(helper.validateId(dset_uuid))
         
        # link the new dataset 
        name = "dset_new"
        req = self.endpoint + "/groups/" + root_uuid + "/links/" + name 
        payload = {"id": dset_uuid}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)

        # retrieve the values
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        data = rspJson['value'] 
        self.assertEqual(data, [42,]*10)

        
        
    #
    # Query tests
    #
    
    def testQuery(self):
        domain = 'compound.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        req += "?query=date == 23"  # values where date field = 23
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('hrefs' in rspJson)
        self.assertTrue('index' in rspJson)
        index = rspJson['index']
        self.assertEqual(len(index), 24)
        self.assertEqual(index[0], 14)
        self.assertTrue('value' in rspJson)
        value = rspJson['value']
        self.assertEqual(len(value), 24)
        item = value[0]
        self.assertEqual(len(item), 5)
        self.assertEqual(item[0], 23)
        
    """    
    def testsnp(self):
        limit = 20
        domain = 'snp500.demo.hdfgroup.org'  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(root_uuid is not None)
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        req += "?query=symbol == 'AAPL'&Limit=" + str(limit) # values where date field = 23
        print req
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        print rspJson
    """    
    
    
    def testQueries(self):
        # use '%26' rather than '&' since otherwise it will be 
        # interpreted as a http query param seperator
        queries = { "date == 23": 24,
                    "wind == b'W 5'": 3,
                    "temp > 61": 53,
                    "(date >=22) %26 (date <= 24)": 62,
                    "(date == 21) %26 (temp > 70)": 4,
                    "(wind == b'E 7') | (wind == b'S 7')": 7 }
       
        #queries = {    "(date == 21) %26 (temp >= 72)": 4 }
        domain = 'compound.' + config.get('domain') 
        headers = {'host': domain} 
        root_uuid = helper.getRootUUID(domain)
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        for key in queries.keys():
            query = req + "?query=" + key
            rsp = requests.get(query, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.assertTrue('hrefs' in rspJson)
            self.assertTrue('index' in rspJson)
            index = rspJson['index']
            self.assertTrue(len(index), queries[key])
            self.assertTrue('value' in rspJson)
            value = rspJson['value']
            self.assertEqual(len(value), queries[key])
            
    def testQuerySelection(self):
        domain = 'compound.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        req += "?query=date == 23"  # values where date field = 23
        req += "&select=[10:20]"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('hrefs' in rspJson)
        self.assertTrue('index' in rspJson)
        index = rspJson['index']
        self.assertEqual(len(index), 6)
        self.assertEqual(index[0], 14)
        self.assertTrue('value' in rspJson)
        value = rspJson['value']
        self.assertEqual(len(value), 6)
        item = value[0]
        self.assertEqual(len(item), 5)
        self.assertEqual(item[0], 23)
        
    def testQueryBatch(self):
        domain = 'compound.' + config.get('domain')  
        headers = {'host': domain}
        root_uuid = helper.getRootUUID(domain)
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"  
        start = 0
        stop = 72
        count = 0
        count = req_count=0
        limit = 10
        req += "?query=date == 23"     # values where date field = 23
        req += "&Limit=" + str(limit)  # return no more than 10 results at a time
        for i in range(50):
            sreq = req+"&select=[" + str(start) + ":" + str(stop) + "]" 
            rsp = requests.get(sreq, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            req_count += 1
            rspJson = json.loads(rsp.text)
            self.assertTrue('hrefs' in rspJson)
            self.assertTrue('index' in rspJson)
            index = rspJson['index']
            self.assertTrue(len(index) <= limit)
            self.assertTrue('value' in rspJson)
            value = rspJson['value']
            self.assertEqual(len(value), len(index))
            count += len(index)
            if len(index) < limit:
                break  # no more results
            start = index[-1] + 1  # start at next index
        self.assertEqual(count, 24)
        self.assertEqual(req_count, 3)
            
         
        
    def testBadQuery(self):
        domain = 'compound.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        req += "?query=foobar"  
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 400)
         
          
         
        
    #
    # Post tests
    #
    
    def testPost(self):    
        for domain_name in ('tall','tall_ro'):
            domain = domain_name + '.' + config.get('domain') 
            rootUUID = helper.getRootUUID(domain)
            g1UUID = helper.getUUID(domain, rootUUID, 'g1')
            g11UUID = helper.getUUID(domain, g1UUID, 'g1.1')
               
            # rank 1 dataset
            dset112UUID = helper.getUUID(domain, g11UUID, 'dset1.1.2') 
            points = (19, 17, 13, 11, 7, 5, 3, 2)
            req = self.endpoint + "/datasets/" + dset112UUID + "/value" 
            payload = {'points': points}
            headers = {'host': domain}
            
            rsp = requests.post(req, data=json.dumps(payload), headers=headers)
            self.assertEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            data = rspJson['value'] 
            self.assertEqual(len(data), len(points))
            self.assertEqual(points[0], data[0])
            
            # rank 2 dataset
            dset111UUID = helper.getUUID(domain, g11UUID, 'dset1.1.1') 
            points = []
            for i in range(10):
                points.append((i,i))  # get diagonal
            req = self.endpoint + "/datasets/" + dset111UUID + "/value" 
            payload = {'points': points}
            headers = {'host': domain}
            
            rsp = requests.post(req, data=json.dumps(payload), headers=headers)
            self.assertEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            data = rspJson['value'] 
            self.assertEqual(len(data), len(points))
            self.assertEqual(9, data[3]) 
    #
    # Put tests
    #   
        
    def testPut(self):
        # create domain
        domain = 'valueput.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        #create scalar dataset
        payload = {'type': 'H5T_STD_I32LE'}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset0UUID = rspJson['id']
        self.assertTrue(helper.validateId(dset0UUID))
        
        # link new dataset as 'dset0'
        ok = helper.linkObject(domain, dset0UUID, 'dset0')
        self.assertTrue(ok)
        
        # write to dset0
        req = self.endpoint + "/datasets/" + dset0UUID + "/value" 
        data = 42
        payload = { 'value': data }
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)
        # read back the data
        readData = helper.readDataset(domain, dset0UUID)
        self.assertEqual(readData, data)  # verify we got back what we started with
        
        #create 1d/one element dataset
        payload = {'type': 'H5T_STD_I32LE', 'shape': 1}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset1UUID = rspJson['id']
        self.assertTrue(helper.validateId(dset1UUID))
         
        # link new dataset as 'dset1_0'
        ok = helper.linkObject(domain, dset1UUID, 'dset1_0')
        self.assertTrue(ok)
        
        # write to dset1
        req = self.endpoint + "/datasets/" + dset1UUID + "/value" 
        data = [42,]
        payload = { 'value': data }
      
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)
        # read back the data
        readData = helper.readDataset(domain, dset1UUID)
        self.assertEqual(readData, data)  # verify we got back what we started with
        
        
        #create 1d dataset
        payload = {'type': 'H5T_STD_I32LE', 'shape': 10}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset1UUID = rspJson['id']
        self.assertTrue(helper.validateId(dset1UUID))
         
        # link new dataset as 'dset1'
        ok = helper.linkObject(domain, dset1UUID, 'dset1')
        self.assertTrue(ok)
        
        # write to dset1
        req = self.endpoint + "/datasets/" + dset1UUID + "/value" 
        data = [2,3,5,7,11,13,17,19,23,29]
        # payload = {'type': 'H5T_STD_I32LE', 'shape': 10, 'value': data }
        payload = { 'value': data }
      
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)
        # read back the data
        readData = helper.readDataset(domain, dset1UUID)
        self.assertEqual(readData, data)  # verify we got back what we started with
        
        # verify attempting the wrong number of elements fails
        data = [9, 99, 999, 999]
        payload = { 'value': data }
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 400)  # Bad Request
        
        #create 2d dataset
        payload = {'type': 'H5T_STD_I32LE', 'shape': (10,10)}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset2UUID = rspJson['id']
        self.assertTrue(helper.validateId(dset2UUID))
         
        # link new dataset as 'dset2'
        ok = helper.linkObject(domain, dset2UUID, 'dset2')
        self.assertTrue(ok)
        
        req = self.endpoint + "/datasets/" + dset2UUID + "/value" 
        data = []
        for i in range(10):
            row = []
            for j in range(10):
                row.append(i*10 + j)
            data.append(row)
        payload = { 'value': data }
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)
        # read back the data
        readData = helper.readDataset(domain, dset2UUID)
        self.assertEqual(readData, data)  # verify we got back what we started with
        
    def testPutBinary(self):
        # create domain
        domain = 'valueput_binary.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        #create scalar dataset
        payload = {'type': 'H5T_STD_I32LE'}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset0UUID = rspJson['id']
        self.assertTrue(helper.validateId(dset0UUID))
        
        # link new dataset as 'dset0'
        ok = helper.linkObject(domain, dset0UUID, 'dset0')
        self.assertTrue(ok)
        
        # write to dset0
        req = self.endpoint + "/datasets/" + dset0UUID + "/value" 
        byte_array = bytearray(4)
        byte_array[0] = 42  # create 4-byte int, little endian
        data = base64.b64encode(bytes(byte_array))
        data = data.decode("ascii")
        payload = { 'value_base64': data }
   
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)
        # read back the data
        readData = helper.readDataset(domain, dset0UUID)
        self.assertEqual(readData, 42)  # verify we got back what we started with
        
        #create 1d dataset
        payload = {'type': 'H5T_STD_I32LE', 'shape': 10}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset1UUID = rspJson['id']
        self.assertTrue(helper.validateId(dset1UUID))
         
        # link new dataset as 'dset1'
        ok = helper.linkObject(domain, dset1UUID, 'dset1')
        self.assertTrue(ok)
        
        # write to dset1
        req = self.endpoint + "/datasets/" + dset1UUID + "/value" 
        primes = [2,3,5,7,11,13,17,19,23,29]
        data = bytearray(4 * 10)
        for i in range(10):
            data[i*4] = primes[i]
        data = base64.b64encode(bytes(data))
        data = data.decode("ascii")
        
        payload = { 'value_base64': data }
        
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)
        # read back the data
        readData = helper.readDataset(domain, dset1UUID)
        self.assertEqual(readData, primes)  # verify we got back what we started with
        
        #create 2d dataset
        payload = {'type': 'H5T_STD_I32LE', 'shape': (10,10)}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset2UUID = rspJson['id']
        self.assertTrue(helper.validateId(dset2UUID))
         
        # link new dataset as 'dset2'
        ok = helper.linkObject(domain, dset2UUID, 'dset2')
        self.assertTrue(ok)
        
        req = self.endpoint + "/datasets/" + dset2UUID + "/value" 
        data = bytearray(10*10*4)
        for i in range(10):
            for j in range(10):
                data[i*10*4 + j*4] = i*j         
        data = base64.b64encode(bytes(data))
        data = data.decode("ascii")
             
        payload = { 'value_base64': data }
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)
        # read back the data
        read_data = helper.readDataset(domain, dset2UUID)
        self.assertEqual(len(read_data), 10)  # verify we got back what we started with
        for i in range(10):
            row = read_data[i]
            self.assertEqual(len(row), 10)
            for j in range(10):
                self.assertEqual(row[j], i*j)
        
        
    def testPutSelection(self):
        # create domain
        domain = 'valueputsel.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        #create 1d dataset
        payload = {'type': 'H5T_STD_I32LE', 'shape': 10}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset1UUID = rspJson['id']
        self.assertTrue(helper.validateId(dset1UUID))
         
        # link new dataset as 'dset1'
        ok = helper.linkObject(domain, dset1UUID, 'dset1')
        self.assertTrue(ok)
        
        req = self.endpoint + "/datasets/" + dset1UUID + "/value" 
        data = [2,3,5,7,11,13,17,19,23,29]
        data_part1 = data[0:5]
        data_part2 = data[5:10]
        # write part 1
        payload = { 'start': 0, 'stop': 5, 'value': data_part1 }
     
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)
        # write part 2
        payload = { 'start': 5, 'stop': 10, 'value': data_part2 }

        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)  
        
        # read back the data
        readData = helper.readDataset(domain, dset1UUID)
        self.assertEqual(readData, data)  # verify we got back what we started with
        
    def testPutSelectionValueMismatch(self):
        # test that putting the wrong number of items in the value body key is handled correctly.
        # create domain
        domain = 'valueputselvaluemismatch.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        #create 1d dataset
        payload = {'type': 'H5T_STD_I32LE', 'shape': 10}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset1UUID = rspJson['id']
        self.assertTrue(helper.validateId(dset1UUID))
         
        # link new dataset as 'dset1'
        ok = helper.linkObject(domain, dset1UUID, 'dset1')
        self.assertTrue(ok)
        
        req = self.endpoint + "/datasets/" + dset1UUID + "/value" 
        data_9 = [2,3,5,7,11,13,17,19,23]
        data_10 = [2,3,5,7,11,13,17,19,23,29]
        data_11 = [2,3,5,7,11,13,17,19,23,29,31]
        
        # try writing 9 elements when the selection has 10 slots
        payload = { 'start': 0, 'stop': 10, 'value': data_9 }
     
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 400)  # should fail
        
        # try writing 11 elements when the selection has 10 slots
        payload = { 'start': 0, 'stop': 10, 'value': data_11 }
     
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 400)  # should fail
        
        # try writing 10 elements when the selection has 10 slots
        payload = { 'start': 0, 'stop': 10, 'value': data_10 }
     
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)  # just right!
        
    def testPutSelectionBinaryValueMismatch(self):
        # test that putting the wrong number of items in the value body key is handled correctly.
        # create domain
        domain = 'valueputselbinaryvaluemismatch.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        #create 1d dataset
        payload = {'type': 'H5T_STD_I32LE', 'shape': 10}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset1UUID = rspJson['id']
        self.assertTrue(helper.validateId(dset1UUID))
         
        # link new dataset as 'dset1'
        ok = helper.linkObject(domain, dset1UUID, 'dset1')
        self.assertTrue(ok)
        
        req = self.endpoint + "/datasets/" + dset1UUID + "/value" 
        primes = [2,3,5,7,11,13,17,19,23,29,31]
        data_9 = bytearray(4 * 9)    # write 4*9 byte data 
        data_10 = bytearray(4 * 10)  # write 4*10 byte data 
        data_11 = bytearray(4 * 11)  # write 4*11 byte data 
        for i in range(9):
            data_9[i*4] = primes[i]
        for i in range(10):
            data_10[i*4] = primes[i]
        for i in range(11):
            data_11[i*4] = primes[i]
       
        data_9 = base64.b64encode(bytes(data_9))
        data_10 = base64.b64encode(bytes(data_10))
        data_11 = base64.b64encode(bytes(data_11))
        
        data_9 = data_9.decode("ascii")
        data_10 = data_10.decode("ascii")
        data_11 = data_11.decode("ascii")
         
        # try writing 9 elements when the selection has 10 slots
        payload = { 'start': 0, 'stop': 10, 'value_base64': data_9 }
     
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 400)  # should fail
        
        # try writing 11 elements when the selection has 10 slots
        payload = { 'start': 0, 'stop': 10, 'value_base64': data_11 }
     
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 400)  # should fail
        
        # try writing 10 elements when the selection has 10 slots
        payload = { 'start': 0, 'stop': 10, 'value_base64': data_10 }
     
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)  # just right!
         
    
    def testPutSelectionBinary(self):
        # create domain
        domain = 'valueputsel_binary.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        #create 1d dataset
        payload = {'type': 'H5T_STD_I32LE', 'shape': 10}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset1UUID = rspJson['id']
        self.assertTrue(helper.validateId(dset1UUID))
         
        # link new dataset as 'dset1'
        ok = helper.linkObject(domain, dset1UUID, 'dset1')
        self.assertTrue(ok)
        
        req = self.endpoint + "/datasets/" + dset1UUID + "/value" 
        primes = [2,3,5,7,11,13,17,19,23,29]
        data_part1 = bytearray(4 * 5)  # write 4*10 byte data in two parts of 20 bytes
        data_part2 = bytearray(4 * 5)  # 2nd part
        for i in range(5):
            data_part1[i*4] = primes[i]
            data_part2[i*4] = primes[i+5]
        data_part1 = base64.b64encode(bytes(data_part1))
        data_part2 = base64.b64encode(bytes(data_part2))
        data_part1 = data_part1.decode("ascii")
        data_part2 = data_part2.decode("ascii")
        # write part 1
        payload = { 'start': 0, 'stop': 5, 'value_base64': data_part1 }
     
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)
        # write part 2
        payload = { 'start': 5, 'stop': 10, 'value_base64': data_part2 }
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)  
        
        # read back the data
        readData = helper.readDataset(domain, dset1UUID)
        self.assertEqual(readData, primes)  # verify we got back what we started with
        
    def testPutPointSelection(self):
        # create domain
        domain = 'valueputpointsel.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        #create 1d dataset
        payload = {'type': 'H5T_STD_I32LE', 'shape': 100}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset1UUID = rspJson['id']
        self.assertTrue(helper.validateId(dset1UUID))
         
        # link new dataset as 'dset1'
        ok = helper.linkObject(domain, dset1UUID, 'dset1')
        self.assertTrue(ok)
        
        req = self.endpoint + "/datasets/" + dset1UUID + "/value" 
        primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
        value = [1,] * len(primes)  # write 1's at indexes that are prime
        # write 1's to all the prime indexes
        payload = { 'points': primes, 'value': value }
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)
         
        # read back the data
        readData = helper.readDataset(domain, dset1UUID)
        self.assertEqual(readData[37], 1)  # prime
        self.assertEqual(readData[38], 0)  # not prime
        
    def testPutPointSelectionBinary(self):
        # create domain
        domain = 'valueputpointsel_binary.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        #create 1d dataset
        payload = {'type': 'H5T_STD_I32LE', 'shape': 100}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset1UUID = rspJson['id']
        self.assertTrue(helper.validateId(dset1UUID))
         
        # link new dataset as 'dset1'
        ok = helper.linkObject(domain, dset1UUID, 'dset1')
        self.assertTrue(ok)
        
        req = self.endpoint + "/datasets/" + dset1UUID + "/value" 
        primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
        value = [1,] * len(primes)  # write 1's at indexes that are prime
        data = bytearray(4 * len(primes))   
        for i in range(len(primes)):
            data[i*4] = 1
        data = base64.b64encode(bytes(data))
        data = data.decode("ascii")
        
        # write 1's to all the prime indexes
        payload = { 'points': primes, 'value_base64': data }
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)
         
        # read back the data
        readData = helper.readDataset(domain, dset1UUID)
        self.assertEqual(readData[37], 1)  # prime
        self.assertEqual(readData[38], 0)  # not prime
        
        
    def testPutCompound(self):
        domain = 'valueputcompound.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201) # creates domain
        
        root_uuid = helper.getRootUUID(domain)
        headers = {'host': domain}
        
        fields = ({'name': 'temp', 'type': 'H5T_STD_I32LE'}, 
                    {'name': 'pressure', 'type': 'H5T_IEEE_F32LE'}) 
        datatype = {'class': 'H5T_COMPOUND', 'fields': fields }
        
        #
        #create compound dataset
        #
        payload = {'type': datatype}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        
        rspJson = json.loads(rsp.text)
        dset0UUID = rspJson['id']
        self.assertTrue(helper.validateId(dset0UUID))
         
        # link new dataset as 'dset0_compound'
        ok = helper.linkObject(domain, dset0UUID, 'dset0_compound')
        self.assertTrue(ok)
        
        # write entire array
        value = (42, 0.42)
        payload = {'value': value}
        req = self.endpoint + "/datasets/" + dset0UUID + "/value"
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)  # write value
        
         
        # read back the data
        readData = helper.readDataset(domain, dset0UUID)
        self.assertEqual(readData[0], 42)   
        
        #    
        #create 1d dataset
        #
        num_elements = 10
        payload = {'type': datatype, 'shape': num_elements}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        
        rspJson = json.loads(rsp.text)
        dset1UUID = rspJson['id']
        self.assertTrue(helper.validateId(dset1UUID))
         
        # link new dataset as 'dset1'
        ok = helper.linkObject(domain, dset1UUID, 'dset_compound')
        self.assertTrue(ok)
        
        # write entire array
        value = [] 
        for i in range(num_elements):
            item = (i*10, i*10+i/10.0) 
            value.append(item)
        payload = {'value': value}
        req = self.endpoint + "/datasets/" + dset1UUID + "/value"
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)  # write value
        
        # selection write
        payload = { 'start': 0, 'stop': 1, 'value': (42, .42) }
        req = self.endpoint + "/datasets/" + dset1UUID + "/value"
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)  # write value
        
        # read back the data
        readData = helper.readDataset(domain, dset1UUID)
        
        self.assertEqual(readData[0][0], 42)   
        self.assertEqual(readData[1][0], 10)   

        #
        # Create 2d dataset
        #
        dims = [2,2]
        payload = {'type': datatype, 'shape': dims}
        req = self.endpoint + "/datasets"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # create dataset
        
        rspJson = json.loads(rsp.text)
        dset2UUID = rspJson['id']
        self.assertTrue(helper.validateId(dset2UUID))
         
        # link new dataset as 'dset2d_compound'
        ok = helper.linkObject(domain, dset2UUID, 'dset2d_compound')
        self.assertTrue(ok)

        # write entire array
        value = [] 
        for i in range(dims[0]):
            row = []
            for j in range(dims[1]):
                item = (i*10, i*10+j/2.0) 
                row.append(item)
            value.append(row)
        payload = {'value': value}
         
        req = self.endpoint + "/datasets/" + dset2UUID + "/value"
        data = json.dumps(payload)
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)  # write value

   
    def testPutObjectReference(self):
        domain = 'objref_dset_updated.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        ds1_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        ds2_uuid = helper.getUUID(domain, root_uuid, 'DS2') 
        g1_uuid = helper.getUUID(domain, root_uuid, 'G1') 
        req = helper.getEndpoint() + "/datasets/" + ds1_uuid  + "/value"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)

        value = ('datasets/' + ds2_uuid, 'groups/' + g1_uuid)
        payload = {'value': value}
        req = self.endpoint + "/datasets/" + ds1_uuid + "/value"
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)  # write value
        
    def testPutRegionReference(self):
        domain = 'regionref_dset_updated.' + config.get('domain')
        root_uuid = helper.getRootUUID(domain)
        ds1_uuid = helper.getUUID(domain, root_uuid, 'DS1') 
        ds2_uuid = helper.getUUID(domain, root_uuid, 'DS2')
        
        req = helper.getEndpoint() + "/datasets/" + ds1_uuid  + "/value"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('value' in rspJson)
        value = rspJson['value']
        self.assertEqual(len(value), 2)
         
        
        updated_value = ( value[1], value[0] )  # switch elements
        payload = {'value': updated_value}
        
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)  # write value
           
             
if __name__ == '__main__':
    unittest.main()
