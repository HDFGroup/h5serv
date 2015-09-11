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

class AclTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(AclTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))
    
            
    def testGetDomainDefaultAcls(self):
        domain = 'tall.' + config.get('domain')   
        req = self.endpoint + "/acls"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        self.failUnlessEqual(rsp.headers['content-type'], 'application/json')
        rspJson = json.loads(rsp.text)
        print "rsp", rspJson
        self.assertTrue('acls' in rspJson)
        
    def testSetRootAcls(self):
        domain = 'tall_acl.' + config.get('domain')  
        readonly_acl = { 'read': True, 'create': False, 'update': False, 
             'delete': False, 'readACL': False, 'updateACL': False }
        readwrite_acl = { 'read': True, 'create': False, 'update': True, 
             'delete': False, 'readACL': False, 'updateACL': False }
        allaccess_acl = { 'read': True, 'create': True, 'update': True, 
             'delete': True, 'readACL': True, 'updateACL': True }
        headers = { 'host': domain }
        
        # set default acl for domain
        payload = { 'perm': readonly_acl }
        req = self.endpoint + "/acls/default"
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        
        # set readwrite acl for test_user1
        payload = { 'perm': readwrite_acl }
        req = self.endpoint + "/acls/test_user1"
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        
        # set allaccess acl for test_user2
        payload = { 'perm': allaccess_acl }
        req = self.endpoint + "/acls/test_user2"
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        
        # read acls
        req = self.endpoint + "/acls"
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('acls' in rspJson)
        acls = rspJson['acls']
        print "acls:", acls
        self.failUnlessEqual(len(acls), 3)
         
        
     
        
if __name__ == '__main__':
    unittest.main()
