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
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.assertEqual(rspJson['id'], dset112UUID)
            self.assertEqual(rspJson['type'], 'H5T_STD_I32BE')
            self.assertEqual(len(rspJson['shape']), 1)
            self.assertEqual(rspJson['shape'][0], 20)  
            req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value"
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
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
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.assertEqual(rspJson['id'], dset111UUID)
            self.assertEqual(rspJson['type'], 'H5T_STD_I32BE')
            self.assertEqual(len(rspJson['shape']), 2)
            self.assertEqual(rspJson['shape'][0], 10)  
            req = helper.getEndpoint() + "/datasets/" + dset111UUID + "/value"
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            data = rspJson['value'] 
            self.assertEqual(len(data), 10)  
            for i in range(10):
                arr = data[i]
                self.assertEqual(len(arr), 10)
                for j in range(10):
                    self.assertEqual(arr[j], i*j)
                
    def testGetZeroDim(self):
        domain = 'zerodim.subdir.' + config.get('domain')  
        rootUUID = helper.getRootUUID(domain)
        dsetUUID = helper.getUUID(domain, rootUUID, 'dset')
               
        # rank 0 dataset
        req = helper.getEndpoint() + "/datasets/" + dsetUUID
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertEqual(rspJson['id'], dsetUUID)
        self.assertEqual(rspJson['type'], 'H5T_STD_I64LE')
        self.assertEqual(len(rspJson['shape']), 0)
        req = helper.getEndpoint() + "/datasets/" + dsetUUID + "/value"
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        data = rspJson['value'] 
        self.assertEqual(data, 42)
         
        
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
             "?dim1_start=2"
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            data = rspJson['value']  # should be [2, 3, 4, ..., 19]
            self.assertEqual(len(data), 18)
            self.assertEqual(data, range(2, 20))
        
            # get values starting at index 2 with stop of 10
            req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?dim1_start=2&dim1_stop=10"
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            data = rspJson['value']  # should be [2, 3, 4, ..., 9]
            self.assertEqual(len(data), 8)
            self.assertEqual(data, range(2, 10))
        
            # get values starting at index 2 with stop of 10, and stride of 2
            req = helper.getEndpoint() + "/datasets/" + dset112UUID + "/value" + \
             "?dim1_start=2&dim1_stop=10&dim1_step=2"
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            data = rspJson['value']  # should be [2, 4, 6, 8]
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
            data = rspJson['value']   
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
            data = rspJson['value']   
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
        
    def testGetCompound(self):
        domain = 'compound.' + config.get('domain')  
        root_uuid = helper.getRootUUID(domain)
        dset_uuid = helper.getUUID(domain, root_uuid, 'dset') 
        req = helper.getEndpoint() + "/datasets/" + dset_uuid + "/value"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        data = rspJson['value'] 
        self.failUnlessEqual(len(data), 72)
        first = data[0]
        self.failUnlessEqual(len(first), 5)
        self.failUnlessEqual(first[0], 24) 
        self.failUnlessEqual(first[1], "13:53")  
        
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
            self.failUnlessEqual(rsp.status_code, 200)
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
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            data = rspJson['value'] 
            self.assertEqual(len(data), len(points))
            self.assertEqual(9, data[3])
            
        
        
        
    def testPut(self):
        # create domain
        domain = 'valueput.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) # creates domain
        
        #create 1d dataset
        payload = {'type': 'int32', 'shape': 10}
        req = self.endpoint + "/datasets/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)  # create dataset
        rspJson = json.loads(rsp.text)
        dset1UUID = rspJson['id']
        self.assertTrue(helper.validateId(dset1UUID))
         
        # link new dataset as 'dset1'
        ok = helper.linkObject(domain, dset1UUID, 'dset1')
        self.assertTrue(ok)
        
        req = self.endpoint + "/datasets/" + dset1UUID + "/value" 
        data = [2,3,5,7,11,13,17,19,23,29]
        payload = {'type': 'int32', 'shape': 10, 'value': data }
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        # read back the data
        readData = helper.readDataset(domain, dset1UUID)
        self.failUnlessEqual(readData, data)  # verify we got back what we started with
        
        #create 2d dataset
        payload = {'type': 'int32', 'shape': (10,10)}
        req = self.endpoint + "/datasets/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)  # create dataset
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
        payload = {'type': 'int32', 'shape': [10, 10], 'value': data }
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        # read back the data
        readData = helper.readDataset(domain, dset2UUID)
        self.failUnlessEqual(readData, data)  # verify we got back what we started with
        
    def testPutSelection(self):
        # create domain
        domain = 'valueputsel.datasettest.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 201) # creates domain
        
        #create 1d dataset
        payload = {'type': 'int32', 'shape': 10}
        req = self.endpoint + "/datasets/"
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)  # create dataset
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
        payload = {'type': 'int32', 'shape': 5, 'start': 0, 'stop': 5, 'value': data_part1 }
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        # write part 2
        payload = {'type': 'int32', 'shape': 5, 'start': 5, 'stop': 10, 'value': data_part2 }
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)  
        
        # read back the data
        readData = helper.readDataset(domain, dset1UUID)
        self.failUnlessEqual(readData, data)  # verify we got back what we started with
             
if __name__ == '__main__':
    unittest.main()