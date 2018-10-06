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
import base64

no_perm = { 'read': False, 'create': False, 'update': False, 
             'delete': False, 'readACL': False, 'updateACL': False }
readonly_perm = { 'read': True, 'create': False, 'update': False, 
             'delete': False, 'readACL': False, 'updateACL': False }
allaccess_perm = { 'read': True, 'create': True, 'update': True, 
             'delete': True, 'readACL': True, 'updateACL': True }

class AclTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(AclTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))
        self.domain = None  
        self.user1 = {'username':'test_user1', 'password':'test'}
        self.user2 = {'username':'test_user2', 'password':'test'}
         
        
    def getHeaders(self, user=None):
        headers = {'host': self.domain}
        if user is not None:
            # if user is supplied, add the auth header
            headers['Authorization'] = helper.getAuthString(user['username'], user['password'])
        return headers
              
        
    def getUUIDByPath(self, path):
        username = self.user1['username']
        password = self.user1['password']
        
        obj_uuid = helper.getUUIDByPath(self.domain, path, user=username, password=password)
        return obj_uuid
        
        
    def setupAcls(self):
         
          
        rootUUID = self.getUUIDByPath('/')
        self.assertTrue(helper.validateId(rootUUID))
        
        headers = self.getHeaders()
           
        # set allaccess acl for test_user2
        payload = allaccess_perm 
        req = self.endpoint + "/acls/test_user2"
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        
        if rsp.status_code == 401:
            # acl is already setup by another test, return
            return
            
        self.assertEqual(rsp.status_code, 201)      
        
        # set read-only acl for test_user1
        payload =  readonly_perm 
        req = self.endpoint + "/acls/test_user1"
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)
        
        # set default acl for domain
        payload =  no_perm 
        req = self.endpoint + "/acls/default"
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201) 
        
        # try - again - should report authorizationis required now
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 401) 
         
           
            
    def testGetDomainDefaultAcls(self):
        self.domain = 'tall.' + config.get('domain')   
        req = self.endpoint + "/acls"
        headers = self.getHeaders()
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.headers['content-type'], 'application/json')
        rspJson = json.loads(rsp.text)
        self.assertTrue('acls' in rspJson)
        
    def testGetDomainAcls(self):
        self.domain = 'tall_acl.' + config.get('domain')  
        self.setupAcls()
        self.assertEqual(self.domain, 'tall_acl.' + config.get('domain')  )
         
        headers = self.getHeaders()    
        
        # read domain acls
        req = self.endpoint + "/acls"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 401)  # needs Authorization
        
        # try with test_user1
        headers = self.getHeaders(self.user1)   
        req = self.endpoint + "/acls"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 403)  # unAuthorization - test_user1 only has read access
        
        # try with test_user2
        headers = self.getHeaders(self.user2)  
        req = self.endpoint + "/acls"
        rsp = requests.get(req, headers=headers)
    
        self.assertEqual(rsp.status_code, 200)   
        
        rspJson = json.loads(rsp.text)
        self.assertTrue('acls' in rspJson)
        acls = rspJson['acls']
        self.assertEqual(len(acls), 3)
        
        # get acl for a particular user
        headers = self.getHeaders(self.user2)  
        req = self.endpoint + "/acls/" + self.user1['username']
        rsp = requests.get(req, headers=headers)
    
        self.assertEqual(rsp.status_code, 200)   
        
        rspJson = json.loads(rsp.text)
        self.assertTrue('acl' in rspJson)
        acl = rspJson['acl']
        self.assertEqual(len(acl.keys()), 7)
        
    def testPutDomain(self):
        
        self.domain = 'new_domain.test_user1.' + config.get('home_domain')  
        
        headers = self.getHeaders()    
        
        # put domain in user home folder
        req = self.endpoint + "/"
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201)  
        # todo - above should fail with 401 - need authorization
                
        
    def testAttributes(self):
        self.domain = 'tall_acl.' + config.get('domain')  
        self.setupAcls()
        rootUUID = self.getUUIDByPath('/')
        self.assertTrue(helper.validateId(rootUUID))
        
        # create attribute
        headers = self.getHeaders()  
        payload = {'type': 'H5T_STD_I32LE', 'value': 42}    
        req = self.endpoint + "/groups/" + rootUUID + "/attributes/a1"
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 401)  # auth needed
        
        headers = self.getHeaders(user=self.user1)
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 403)  # not authorized
        
        headers = self.getHeaders(user=self.user2)
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # OK
        
        # read group attribute
        headers = self.getHeaders()
        req = self.endpoint + "/groups/" + rootUUID + "/attributes/a1"  
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 401)  # un-authorized                
        
        headers = self.getHeaders(user=self.user1)
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)  # OK
        rspJson = json.loads(rsp.text)  
        self.assertEqual(rspJson['value'], 42)  
               
        # delete attribute
        headers = self.getHeaders()
        req = self.endpoint + "/groups/" + rootUUID + "/attributes/" + 'a1'
        rsp = requests.delete(req, headers=headers)     
        self.assertEqual(rsp.status_code, 401)  # auth needed
        
        headers = self.getHeaders(user=self.user1)
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 403)  # not authorized
        
        headers = self.getHeaders(user=self.user2)
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 200) 
        
    def testDataset(self):
        self.domain = 'tall_acl.' + config.get('domain')  
        self.setupAcls()
        rootUUID = self.getUUIDByPath('/')
        self.assertTrue(helper.validateId(rootUUID))
            
        # create dataset
        headers = self.getHeaders()  
        payload = {'type': 'H5T_STD_I32LE' }    
        req = self.endpoint + "/datasets"  
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 401)  # auth needed
        
        headers = self.getHeaders(user=self.user1)
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 403)  # not authorized
        
        headers = self.getHeaders(user=self.user2)
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # OK
        
        rspJson = json.loads(rsp.text)  
        dataset_uuid = rspJson['id']
        
        # read dataset  
        headers = self.getHeaders()
        req = self.endpoint + "/datasets/" + dataset_uuid  
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 401)  # un-authorized                    
        
        headers = self.getHeaders(user=self.user1)
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)  # OK

        # read dataset acls
        req += "/acls"
        rsp = requests.get(req, headers=headers)  
        self.assertEqual(rsp.status_code, 403)  # test_user1 doesn't have readACL permission
        headers = self.getHeaders(user=self.user2)
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text) 
        self.assertTrue("acls" in rspJson)
        acls = rspJson["acls"]
        self.assertEqual(len(acls), 0)  # empty list of acls
        
        # delete dataset
        headers = self.getHeaders()
        req = self.endpoint + "/datasets/" + dataset_uuid  
        rsp = requests.delete(req, headers=headers)     
        self.assertEqual(rsp.status_code, 401)  # auth needed
        
        headers = self.getHeaders(user=self.user1)
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 403)  # not authorized
        
        headers = self.getHeaders(user=self.user2)
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)  # OK
        
    def testValue(self):
        self.domain = 'tall_acl.' + config.get('domain')  
        self.setupAcls()
        
        dset_uuid = self.getUUIDByPath('/g1/g1.1/dset1.1.1')  
        self.assertTrue(helper.validateId(dset_uuid))   
        
        # read value
        headers = self.getHeaders()
        req = self.endpoint + "/datasets/" + dset_uuid + "/value"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 401)  # auth needed
        
        headers = self.getHeaders(user=self.user1)
        req = self.endpoint + "/datasets/" + dset_uuid + "/value"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)  # OK
        
        # point selection
        points = []
        for i in range(10):
            points.append((i,i))  # get diagonal
        req = self.endpoint + "/datasets/" + dset_uuid + "/value" 
        payload = {'points': points}
        headers = self.getHeaders()    
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 401)  # auth needed
        
        # write values
        data = []
        for i in range(10):
            row = []
            for j in range(10):
                row.append(j*10 + i)
            data.append(row)
        req = self.endpoint + "/datasets/" + dset_uuid + "/value" 
        payload = { 'value': data }
        headers = self.getHeaders()
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 401)  # auth needed
        
        headers = self.getHeaders(user=self.user1)
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 403)  # not authorized
        
        headers = self.getHeaders(user=self.user2)
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)  # OK
        
    def testDatatypes(self):
        self.domain = 'tall_acl.' + config.get('domain')  
        self.setupAcls()
        
        payload = {'type': 'H5T_IEEE_F32LE'}
        req = self.endpoint + "/datatypes"
        
        # test create
        headers = self.getHeaders()
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 401)  # auth needed  
         
        headers = self.getHeaders(user=self.user1)
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 403)  # not authorized
        
        headers = self.getHeaders(user=self.user2)
        rsp = requests.post(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)  # created
        rspJson = json.loads(rsp.text) 
        type_uuid = rspJson['id']
        self.assertTrue(helper.validateId(type_uuid))
        
        # test read
        req = self.endpoint + "/datatypes/" + type_uuid 
        headers = self.getHeaders()
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 401)  # auth needed  
        
        headers = self.getHeaders(user=self.user1)
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)  # OK

        # read dataset acls
        req += "/acls"
        rsp = requests.get(req, headers=headers)  
        self.assertEqual(rsp.status_code, 403)  # test_user1 doesn't have readACL permission
        headers = self.getHeaders(user=self.user2)
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text) 
        self.assertTrue("acls" in rspJson)
        acls = rspJson["acls"]
        self.assertEqual(len(acls), 0)  # empty list of acls
           
        # test delete
        headers = self.getHeaders()
        req = self.endpoint + "/datatypes/" + type_uuid 
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 401)  # auth needed
        
        headers = self.getHeaders(user=self.user1)
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 403)  # un authorized
        
        headers = self.getHeaders(user=self.user1)
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 403)  # OK
         
    def testGroups(self):
        self.domain = 'tall_acl.' + config.get('domain')  
        self.setupAcls()
        
        g1_uuid = self.getUUIDByPath('/g1')
       
        self.assertTrue(helper.validateId(g1_uuid))
        
        # read group g1
        headers = self.getHeaders()
        req = self.endpoint + "/groups/" + g1_uuid
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 401)  # needs Authorization
        headers = self.getHeaders(user=self.user1)
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)

        # read group acls
        req += "/acls"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 403)  # test_user1 doesn't have readACL permission
        headers = self.getHeaders(user=self.user2)
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text) 
        self.assertTrue("acls" in rspJson)
        acls = rspJson["acls"]
        self.assertEqual(len(acls), 0)  # empty list of acls
         
        # read links
        headers = self.getHeaders()
        req = self.endpoint + "/groups/" + g1_uuid + '/links'
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 401)  # needs Authorization
        headers = self.getHeaders(user=self.user1)
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)  # OK
        
        # read link
        headers = self.getHeaders()
        req = self.endpoint + "/groups/" + g1_uuid + '/links/g1.1'
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 401)  # needs Authorization
        headers = self.getHeaders(user=self.user1)
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200) # OK
        
        # create group
        headers = self.getHeaders()
        req = self.endpoint + "/groups"
        rsp = requests.post(req, headers=headers)
        self.assertEqual(rsp.status_code, 401)  # needs Authorization
        headers = self.getHeaders(user=self.user1)
        rsp = requests.post(req, headers=headers)
        self.assertEqual(rsp.status_code, 403)  # un-authorized
        headers = self.getHeaders(user=self.user2)
        rsp = requests.post(req, headers=headers)
        self.assertEqual(rsp.status_code, 201)  # Created
        rspJson = json.loads(rsp.text)
        grp_uuid = rspJson['id']
        
        # add link
        headers = self.getHeaders()
        payload = { "id": grp_uuid }
        req = self.endpoint + "/groups/" + g1_uuid + '/links/new_group'
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 401)  # needs Authorization
        headers = self.getHeaders(user=self.user1)
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 403) # un-authorized
        headers = self.getHeaders(user=self.user2)
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201) # created
        
        # delete link
        headers = self.getHeaders()
        req = self.endpoint + "/groups/" + g1_uuid + '/links/new_group'
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 401)  # needs Authorization
        headers = self.getHeaders(user=self.user1)
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 403) # un-authorized
        headers = self.getHeaders(user=self.user2)
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 200) # OK
               
        # delete group
        headers = self.getHeaders()
        req = self.endpoint + "/groups/" + grp_uuid
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 401)  # needs Authorization
        headers = self.getHeaders(user=self.user1)
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 403)  # un-authorized
        headers = self.getHeaders(user=self.user2)
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)  # OK
        
    def testRoot(self):
        self.domain = 'tall_acl_delete.' + config.get('domain')  
        self.setupAcls()
        
        # read domain resource
        headers = self.getHeaders()
        req = self.endpoint + "/" 
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 401)  # needs Authorization\
        
        headers = self.getHeaders(user=self.user1)
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        
        # delete domain!
        headers = self.getHeaders()
        req = self.endpoint + "/" 
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 401)  # needs Authorization
        
        # try malformed auth string 
        headers['Authorization'] = "Basic " + "xxx123"
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 400)  # bad auth header
        
        # try invalid password
        headers['Authorization'] = helper.getAuthString("test_user1", "notmypassword")
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 401)  # need valid auth header     
        
        headers = self.getHeaders(user=self.user1)
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 403)  # not authorized 
        
        headers = self.getHeaders(user=self.user2)
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)  # OK        
     
        
if __name__ == '__main__':
    unittest.main()
