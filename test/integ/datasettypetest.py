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

class DatasetTypeTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(DatasetTypeTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))    
       
    def testGet(self):
        domain = 'tall.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        g2_uuid = helper.getUUID(domain, root_uuid, 'g2')
        dset21_uuid = helper.getUUID(domain, g2_uuid, 'dset2.1') 
        req = helper.getEndpoint() + "/datasets/" + dset21_uuid + '/type'
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        typeItem = rspJson['type']
        self.assertEqual(typeItem['base'], 'H5T_IEEE_F32BE') 
        self.assertEqual(typeItem['class'], 'H5T_FLOAT') 
     
        
    def testGetScalar(self):
        domain = 'scalar.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, '0d') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + '/type'
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        typeItem = rspJson['type']
        self.assertEqual(typeItem['base'], 'H5T_STD_I32LE') 
        self.assertEqual(typeItem['class'], 'H5T_INTEGER') 
       
    def testGetCompound(self):
        domain = 'compound.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        self.assertTrue(helper.validateId(root_uuid))
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + '/type'
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
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
    
        
if __name__ == '__main__':
    unittest.main()
