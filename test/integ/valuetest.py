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

class ValueTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(ValueTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))    
       
    def testGet(self):
        domain = 'tall.' + config.get('domain')  
        rootUUID = helper.getRootUUID(domain)
        g1UUID = helper.getUUID(domain, rootUUID, 'g1')
        g11UUID = helper.getUUID(domain, g1UUID, 'g1.1')
               
        # rank 1 dataset
        dset112UUID = helper.getUUID(domain, g11UUID, 'dset1.1.2') 
        req = helper.getEndpoint() + "/datasets/" + dset112UUID
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(rspJson['id'], dset112UUID)
        self.assertEqual(rspJson['type'], 'int32')
        self.assertEqual(len(rspJson['shape']), 1)
        self.assertEqual(rspJson['shape'][0], 20)  
        req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value"
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        data = rspJson['values'] 
        self.assertEqual(len(data), 20)
        for i in range(20):
            self.assertEqual(data[i], i)
        
        # rank 2 dataset
        dset111UUID = helper.getUUID(domain, g11UUID, 'dset1.1.1') 
        req = helper.getEndpoint() + "/datasets/" + dset111UUID
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(rspJson['id'], dset111UUID)
        self.assertEqual(rspJson['type'], 'int32')
        self.assertEqual(len(rspJson['shape']), 2)
        self.assertEqual(rspJson['shape'][0], 10)  
        req = helper.getEndpoint() + "/datasets/" + dset111UUID + "/value"
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        data = rspJson['values'] 
        self.assertEqual(len(data), 10)  
        for i in range(10):
            arr = data[i]
            self.assertEqual(len(arr), 10)
            for j in range(10):
                self.assertEqual(arr[j], i*j)
        
    def testGetSelection(self):
        domain = 'tall.' + config.get('domain')  
        headers = {'host': domain}
        rootUUID = helper.getRootUUID(domain)
        g1UUID = helper.getUUID(domain, rootUUID, 'g1')
        g11UUID = helper.getUUID(domain, g1UUID, 'g1.1')
               
        # rank 1 dataset
        dset112UUID = helper.getUUID(domain, g11UUID, 'dset1.1.2') 
         
        # dataset has shape (20,) and type 'int32'
        
        # get values starting at index 2
        req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?dim1_start=2"
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        data = rspJson['values']  # should be [2, 3, 4, ..., 19]
        self.assertEqual(len(data), 18)
        self.assertEqual(data, range(2, 20))
        
        # get values starting at index 2 with stop of 10
        req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?dim1_start=2&dim1_stop=10"
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        data = rspJson['values']  # should be [2, 3, 4, ..., 9]
        self.assertEqual(len(data), 8)
        self.assertEqual(data, range(2, 10))
        
        # get values starting at index 2 with stop of 10, and stride of 2
        req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?dim1_start=2&dim1_stop=10&dim1_step=2"
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        data = rspJson['values']  # should be [2, 4, 6, 8]
        self.assertEqual(len(data), 4)
        self.assertEqual(data, range(2, 9, 2))
        
        # rank 2 dataset
        dset111UUID = helper.getUUID(domain, g11UUID, 'dset1.1.1') 
         
        # dataset has shape (10,10) and type 'int32'
        
        # get rows 2, 3, 4, and 5
        req = helper.getEndpoint() + "/datasets/" + dset111UUID + "/value" + \
             "?dim2_start=2&dim2_stop=6"
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        data = rspJson['values']   
        self.assertEqual(len(data), 10)  
        for i in range(10):
            arr = data[i]
            self.assertEqual(len(arr), 4)
            for j in range(4):
                self.assertEqual(arr[j], i*(j+2))
                
        # get 2d subregion with stride
        req = helper.getEndpoint() + "/datasets/" + dset111UUID + "/value" + \
             "?dim1_start=1&dim1_end=9&dim2_start=1&dim2_stop=9&dim2_step=2"
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        data = rspJson['values']   
        self.assertEqual(len(data), 9)  
        for i in range(9):
            arr = data[i]
            self.assertEqual(len(arr), 4)
            for j in range(4):
                self.assertEqual(arr[j], (i+1)*(j*2+1))
                
    def testGetSelectionBadQuery(self):
        domain = 'tall.' + config.get('domain')  
        headers = {'host': domain}
        rootUUID = helper.getRootUUID(domain)
        g1UUID = helper.getUUID(domain, rootUUID, 'g1')
        g11UUID = helper.getUUID(domain, g1UUID, 'g1.1')
               
        # rank 1 dataset
        dset112UUID = helper.getUUID(domain, g11UUID, 'dset1.1.2') 
         
        # pass in non-numeric start
        req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?dim1_start=abc"
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)
        
        # pass in 0 step
        req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?dim1_start=2&dim1_step=0"
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)       
        
     
        
if __name__ == '__main__':
    unittest.main()