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
import unittest
import helper
import json
import logging

class LinkTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(LinkTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))
       
    def testGetHard(self):
        logging.info("LinkTest.testGetHard")
        for domain_name in ('tall', 'tall_ro'):
            g1_uuid = None
            domain = domain_name + '.' + config.get('domain')   
            root_uuid = helper.getRootUUID(domain)     
            req = self.endpoint + "/groups/" + root_uuid + "/links/g1"
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.assertTrue("created" in rspJson)
            self.assertTrue("lastModified" in rspJson)
            self.assertTrue('link' in rspJson)
            target = rspJson['link']
            self.assertTrue(helper.validateId(target['id']))
            self.assertEqual(target['class'], 'H5L_TYPE_HARD')
            self.assertEqual(target['title'], 'g1')
            self.assertEqual(target['collection'], 'groups')
            
    def testGetSoft(self):
        logging.info("LinkTest.testGetSoft")
        for domain_name in ('tall', 'tall_ro'):
            g1_uuid = None
            domain = domain_name + '.' + config.get('domain')   
            root_uuid = helper.getRootUUID(domain)
            g1_uuid = helper.getUUID(domain, root_uuid, 'g1')
            g12_uuid = helper.getUUID(domain, g1_uuid, 'g1.2')
            g121_uuid = helper.getUUID(domain, g12_uuid, 'g1.2.1')
            req = self.endpoint + "/groups/" + g121_uuid + "/links/slink"
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.assertTrue("created" in rspJson)
            self.assertTrue("lastModified" in rspJson)
            target = rspJson['link']
            self.assertEqual(target['h5path'], 'somevalue')
            self.assertEqual(target['class'], 'H5L_TYPE_SOFT')
            self.assertEqual(target['title'], 'slink')
            self.assertTrue('collection' not in target)
            
    def testGetExternal(self):
        logging.info("LinkTest.testGetExternal")
        for domain_name in ('tall', 'tall_ro'):
            g1_uuid = None
            domain = domain_name + '.' + config.get('domain')   
            root_uuid = helper.getRootUUID(domain)
            g1_uuid = helper.getUUID(domain, root_uuid, 'g1')
            g12_uuid = helper.getUUID(domain, g1_uuid, 'g1.2')
            req = self.endpoint + "/groups/" + g12_uuid + "/links/extlink"
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.assertTrue("created" in rspJson)
            self.assertTrue("lastModified" in rspJson)
            target = rspJson['link']
            # self.assertEqual(target, "http://somefile/#h5path(somepath)")
            
            self.assertEqual(target['class'], 'H5L_TYPE_EXTERNAL')
            self.assertEqual(target['h5domain'], 'somefile')
            self.assertEqual(target['h5path'], 'somepath')
            self.assertEqual(target['title'], 'extlink')
            self.assertTrue('collection' not in target)
            
    def testGetUDLink(self):
        logging.info("LinkTest.testGetUDLink")
        domain_name = 'tall_with_udlink'    
        domain = domain_name + '.' + config.get('domain')   
        root_uuid = helper.getRootUUID(domain)
        g2_uuid = helper.getUUID(domain, root_uuid, 'g2')
        req = self.endpoint + "/groups/" + g2_uuid + "/links/udlink"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue("created" in rspJson)
        self.assertTrue("lastModified" in rspJson)
        target = rspJson['link']
        self.assertEqual(target['class'], 'H5L_TYPE_USER_DEFINED')
        self.assertEqual(target['title'], 'udlink')
        
    def testGetLinks(self):
        logging.info("LinkTest.testGetLinks")
        for domain_name in ('tall', 'tall_ro'):
            g1_uuid = None
            domain = domain_name + '.' + config.get('domain')   
            root_uuid = helper.getRootUUID(domain) 
            g1_uuid = helper.getUUID(domain, root_uuid, 'g1')
            g12_uuid = helper.getUUID(domain, g1_uuid, 'g1.2')    
            req = self.endpoint + "/groups/" + g12_uuid + "/links"
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.assertEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.assertTrue("links" in rspJson)
            links = rspJson["links"]
            self.assertEqual(len(links), 2)
            for link in links:
                self.assertTrue("title" in link)
                self.assertTrue("class" in link)
                            
    def testGetBatch(self):
        logging.info("LinkTest.testGetBatch")
        domain = 'group1k.' + config.get('domain')   
        root_uuid = helper.getRootUUID(domain)     
        req = helper.getEndpoint() + "/groups/" + root_uuid + "/links"
        headers = {'host': domain}
        params = {'Limit': 50 }
        names = set()
        # get links in 20 batches of 50 links each
        lastName = None
        for batchno in range(20):
            if lastName:
                params['Marker'] = lastName
            rsp = requests.get(req, headers=headers, params=params)
            self.assertEqual(rsp.status_code, 200)
            if rsp.status_code != 200:
                break
            rspJson = json.loads(rsp.text)
            links = rspJson['links']
            self.assertEqual(len(links) <= 50, True)
            for link in links:
                lastName = link['title']
                names.add(lastName)
            if len(links) == 0:
                break
        self.assertEqual(len(names), 1000)  # should get 1000 unique links
    
    
    #Fix - This needs to be made more efficient - when deleting links, the code now
    # searches all objects to see if the linked target needs to be made anonymous or not.
    # idea: keep back pointers for all links?
    # Tracked as Issue #12 in Github
    """    
    def testMoveLinks(self):
        logging.info("LinkTest.testMoveLinks")
        domain = 'group1k_updated.' + config.get('domain')   
        root_uuid = helper.getRootUUID(domain)  
        
        # create a new subgroup to move others to
        targetGroupId = helper.createGroup(domain)
         
           
        req = helper.getEndpoint() + "/groups/" + root_uuid + "/links"
        headers = {'host': domain}
        params = {'Limit': 100 }
        names = set()
        # get links in batches of 100 links each
        count = 0
        while True:
            print 'count:', count
            rsp = requests.get(req, headers=headers, params=params)
            self.assertEqual(rsp.status_code, 200)
            if rsp.status_code != 200:
                break
            rspJson = json.loads(rsp.text)
            links = rspJson['links']
            
            if len(links) == 0:
                break
            count += len(links)
            for link in links:
                # delete link
                del_req = helper.getEndpoint() + "/groups/" + root_uuid + "/links/" + link['title']
                rsp = requests.delete(del_req, headers=headers)
                self.assertEqual(rsp.status_code, 200)
        self.assertEqual(count, 1000)  # should get 1000 unique links
    """
        
    def testGetBadParam(self):
        logging.info("LinkTest.testGetBatchBadParam")
        domain = 'tall.' + config.get('domain')   
        root_uuid = helper.getRootUUID(domain)     
        req = helper.getEndpoint() + "/groups/" + root_uuid + "/links"
        headers = {'host': domain}
        params = {'Limit': 'abc' }
        rsp = requests.get(req, headers=headers, params=params)
        self.assertEqual(rsp.status_code, 400)
    
        
    def testPut(self):
        logging.info("LinkTest.testPut")
        domain = 'tall_updated.' + config.get('domain') 
        grpId = helper.createGroup(domain)
        rootId = helper.getRootUUID(domain)   
        name = 'g3'
        req = helper.getEndpoint() + "/groups/" + rootId + "/links/" + name 
        payload = {"id": grpId}
        headers = {'host': domain}
        rsp = requests.get(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 404)  # link doesn't exist
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)
        rsp = requests.get(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)  # it's there now!
        # make a request second time (verify idempotent)
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)
        # now try with a different payload
        grpId2 = helper.createGroup(domain)
        payload["id"] = grpId2
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)
        
        
    def testPutNameWithSpaces(self):
        logging.info("LinkTest.testPutNameWithSpaces")
        domain = 'tall_updated.' + config.get('domain') 
        grpId = helper.createGroup(domain)
        rootId = helper.getRootUUID(domain)   
        name = 'name with spaces'
        req = helper.getEndpoint() + "/groups/" + rootId + "/links/" + name 
        payload = {"id": grpId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)
        
    def testPutBadReqId(self):
        logging.info("LinkTest.testPutBadReqId")
        domain = 'tall_updated.' + config.get('domain') 
        grpId = helper.createGroup(domain)
        badReqId  = 'b2771194-347f-11e4-bb67-3c15c2da029e' # doesn't exist in tall.h5
        name = 'g3'
        req = helper.getEndpoint() + "/groups/" + badReqId + "/links/" + name 
        payload = {"id": grpId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 404)
        
    def testPutBadLinkId(self):
        logging.info("LinkTest.testPutBadLinkId")
        domain = 'tall_updated.' + config.get('domain') 
        grpId = helper.createGroup(domain)
        rootId = helper.getRootUUID(domain)  
        badLinkId  = 'b2771194-347f-11e4-bb67-3c15c2da029e' # doesn't exist in tall.h5
        name = 'g3'
        req = helper.getEndpoint() + "/groups/" + rootId + "/links/" + name 
        payload = {"id": badLinkId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 404)
        
    def testPutNoName(self):
        logging.info("LinkTest.testPutNoName")
        domain = 'tall_updated.' + config.get('domain') 
        grpId = helper.createGroup(domain)
        rootId = helper.getRootUUID(domain)   
        req = helper.getEndpoint() + "/groups/" + rootId + "/links/"  
        payload = {"id": grpId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 400)
        
    def testPutBadName(self):
        logging.info("LinkTest.testPutBadName")
        domain = 'tall_updated.' + config.get('domain') 
        grpId = helper.createGroup(domain)
        rootId = helper.getRootUUID(domain)   
        name = 'bad/name'  # forward slash not allowed
        req = helper.getEndpoint() + "/groups/" + rootId + "/links/" + name 
        payload = {"id": grpId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 400)
        
    def testPutSoftLink(self):
        logging.info("LinkTest.testPutSoftLink")
        domain = 'tall_updated.' + config.get('domain') 
        grpId = helper.createGroup(domain)
        rootId = helper.getRootUUID(domain)   
        name = 'softlink'
        req = helper.getEndpoint() + "/groups/" + rootId + "/links/" + name 
        payload = {"h5path": "somewhere"}
        headers = {'host': domain}
        # verify softlink does not exist
        rsp = requests.get(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 404)
        # make request
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)
        # verify link is created
        rsp = requests.get(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)
        # verify idempotent
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)
        
    def testPutExternalLink(self):
        logging.info("LinkTest.testPutExternalLink")
        domain = 'tall_updated.' + config.get('domain') 
        target_domain = 'external_target.' + config.get('domain')  
        target_path = '/dset1'
        grpId = helper.createGroup(domain)
        rootId = helper.getRootUUID(domain)   
        name = 'extlink'
        req = helper.getEndpoint() + "/groups/" + rootId + "/links/" + name 
        payload = {"h5path": target_path, "h5domain": target_domain}
        headers = {'host': domain}
        # verify extlink does not exist
        rsp = requests.get(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 404)
        # make request
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201) 
        # verify link is created
        rsp = requests.get(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 200)
        # verify that it is an external link
        rspJson = json.loads(rsp.text)   
        target = rspJson['link']
              
        self.assertEqual(target['class'], 'H5L_TYPE_EXTERNAL')
        self.assertEqual(target['h5domain'], target_domain)
        self.assertEqual(target['h5path'], target_path)
            
          
    def testPutExternalMissingPath(self):
        logging.info("LinkTest.testPutExternalMissingPath")
        fakeId = "14bfeeb8-68b1-11e4-a69a-3c15c2da029e"
        domain = 'tall_updated.' + config.get('domain') 
        external_domain = 'external_target.' + config.get('domain') 
        grpId = helper.createGroup(domain)
        rootId = helper.getRootUUID(domain)   
        name = 'extlinkid'
        req = helper.getEndpoint() + "/groups/" + rootId + "/links/" + name 
        payload = {"h5domain": external_domain}
        headers = {'host': domain}
        # verify extlink does not exist
        rsp = requests.get(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 404)
        # make request
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 400)     
        
    def testDelete(self):
        logging.info("LinkTest.testDelete")
        domain = 'tall_updated.' + config.get('domain') 
        grpId = helper.createGroup(domain)
        rootId = helper.getRootUUID(domain)   
        name = 'deleteme'
        req = helper.getEndpoint() + "/groups/" + rootId + "/links/" + name 
        payload = {"id": grpId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.assertEqual(rsp.status_code, 201)
        
        # now remove the link
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        
        # get should fail
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 410)   
        
        # Group should still be accessible via uuid
        req = self.endpoint + "/groups/" + grpId
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        
    
       
if __name__ == '__main__':
    unittest.main()
