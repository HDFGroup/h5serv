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
import os
import time
from shutil import copyfile
from tornado.escape import url_escape

class DirTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(DirTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))
        self.user1 = {'username':'test_user1', 'password':'test'}
    
        
    def testGetToc(self):  
        domain = config.get('domain')  
        if domain.startswith('test.'):
            domain = domain[5:]
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.headers['content-type'], 'application/json')
        rspJson = json.loads(rsp.text)
        self.assertTrue('root' in rspJson)
        root_uuid = rspJson['root']
        req = self.endpoint + "/groups/" + root_uuid 
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        # get top-level links
        req = self.endpoint + "/groups/" + root_uuid + "/links"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue("links" in rspJson)
        links = rspJson["links"]
         
        home_dir = config.get("home_dir")
        for item in links:
            if item['title'] == home_dir:
                self.assertTrue(False)  # should not see home dir from root toc

        # get group uuid that maps to "test" sub-directory
        req = self.endpoint + "/groups/" + root_uuid + "/links/test" 
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue("link" in rspJson)
        link = rspJson['link']
        group_uuid = link['id']

        # verify we see "tall" under links
        name = "tall"
        req = self.endpoint + "/groups/" + group_uuid + "/links/" + name 
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue("link" in rspJson)
        link = rspJson['link']
        self.assertEqual(link['class'], 'H5L_TYPE_EXTERNAL')
        self.assertEqual(link['title'], name)
        self.assertEqual(link['h5path'], '/')
        self.assertEqual(link['h5domain'], name + '.test.' + domain)

        # verify that "filename with space" shows up properly url encoded
        name = "filename with space"
        name_escaped = url_escape(name)
        req = self.endpoint + "/groups/" + group_uuid + "/links/" + name 
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue("link" in rspJson)
        link = rspJson['link']
        self.assertEqual(link['class'], 'H5L_TYPE_EXTERNAL')
        self.assertEqual(link['title'], name)
        self.assertEqual(link['h5path'], '/')
        self.assertEqual(link['h5domain'], name_escaped + '.test.' + domain)
         
        # get all the links in the test group
        req = self.endpoint + "/groups/" + group_uuid + "/links"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue("links" in rspJson)
        links = rspJson["links"]
        tall_link = None         # normal link
        file_space_link = None   # link that contains a space  
        file_dot_link = None     # link that contains a dot
        for link in links:
            self.assertTrue("title" in link)
            self.assertTrue("class" in link)
            if link['title'] == "tall":
                tall_link = link
            elif link['title'] == "filename with space":
                file_space_link = link              
            elif link['title'] == "tall.dots.need.to.be.encoded":
                file_dot_link = link

        self.assertTrue(tall_link is not None)
        name = "tall"
        link = tall_link
        self.assertEqual(link['class'], 'H5L_TYPE_EXTERNAL')
        self.assertEqual(link['title'], name)
        self.assertEqual(link['h5path'], '/')
        self.assertEqual(link['h5domain'], name + '.test.' + domain)
        href = "groups/" + group_uuid + "/links/" + name
        self.assertTrue(link['href'].endswith(href))

        self.assertTrue(file_space_link is not None)
        name = "filename with space"
        link = file_space_link
        self.assertEqual(link['class'], 'H5L_TYPE_EXTERNAL')
        self.assertEqual(link['title'], name)
        self.assertEqual(link['h5path'], '/')
        self.assertEqual(link['h5domain'], url_escape(name) + '.test.' + domain)
        href = "groups/" + group_uuid + "/links/" + url_escape(name)
        self.assertTrue(link['href'].endswith(href))

        self.assertTrue(file_dot_link is not None)
        name = "tall.dots.need.to.be.encoded"
        name_encoded = name.replace('.', '%2E')
    
        link = file_dot_link
        self.assertEqual(link['class'], 'H5L_TYPE_EXTERNAL')
        self.assertEqual(link['title'], name)
        self.assertEqual(link['h5path'], '/')
        self.assertEqual(link['h5domain'], name_encoded + '.test.' + domain)
        href = "groups/" + group_uuid + "/links/" + name
        self.assertTrue(link['href'].endswith(href))

         

        
    def testGetUserToc(self):  
        domain = config.get('domain')
        if domain.startswith('test.'):
            domain = domain[5:]  # backup over the test part
      
        home_dir = config.get("home_dir")
        user_domain = self.user1['username'] + '.' + home_dir  + '.' + domain
        req = self.endpoint + "/"
        headers = {'host': user_domain}
        # this should get the users .toc file
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.headers['content-type'], 'application/json')
        rspJson = json.loads(rsp.text)
        self.assertTrue('root' in rspJson)
        root_uuid = rspJson['root']
        req = self.endpoint + "/groups/" + root_uuid 
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        
        if os.name == 'nt':
            return # symbolic links used below are not supported on Windows
            
        # get link to 'public' folder
        req =  self.endpoint + "/groups/" + root_uuid + "/links/public"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        
        rspJson = json.loads(rsp.text)
        self.assertTrue("link" in rspJson)
        link_json = rspJson["link"]
        self.assertEqual(link_json["class"], "H5L_TYPE_EXTERNAL")
        self.assertEqual(link_json["title"], "public")
        self.assertEqual(link_json["h5domain"], domain) 
        self.assertEqual(link_json["h5path"], "/public") 
        
        # get link to 'tall' file
        req =  self.endpoint + "/groups/" + root_uuid + "/links/tall"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        
        rspJson = json.loads(rsp.text)
        self.assertTrue("link" in rspJson)
        link_json = rspJson["link"]
        self.assertEqual(link_json["class"], "H5L_TYPE_EXTERNAL")
        self.assertEqual(link_json["title"], "tall")
        self.assertEqual(link_json["h5domain"], "tall." + user_domain)

        
    def testPutUserDomain(self):  
        domain = config.get('domain')
        home_dir = config.get("home_dir")
        if domain.startswith('test.'):
            domain = domain[5:]  # backup over the test part
      
        user_domain = self.user1['username'] + '.' + home_dir + '.' + domain
        
        # this should get the users .toc file
        headers = {'host': user_domain }
        req = self.endpoint + '/'
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('root' in rspJson)
        toc_root_uuid = rspJson['root']
        req = self.endpoint + "/groups/" + toc_root_uuid 
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
       
        # verify that "myfile" doesn't exist yet
        user_file = "myfile." + user_domain
        req = self.endpoint + "/"
        headers = {'host': user_file}
        #verify that the domain doesn't exist yet
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 404)
        
        # do a put on "myfile"
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201)
        
        # now the domain should exist  
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        
        # go back to users toc and get "/myfile" link
        headers = {'host': user_domain }
        req = self.endpoint + "/groups/" + toc_root_uuid + "/links/myfile"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        link = rspJson['link']
         
        self.assertTrue('class' in link)
        self.assertEqual(link['class'], "H5L_TYPE_EXTERNAL")
        self.assertTrue('h5path' in link)
        self.assertEqual(link['h5path'], "/")
        self.assertTrue('h5domain' in link)
        self.assertEqual(link['h5domain'], "myfile." + user_domain)
                
        
    def testDeleteUserDomain(self):  
        domain = config.get('domain')
        home_dir = config.get("home_dir")
        if domain.startswith('test.'):
            domain = domain[5:]  # backup over the test part
      
        user_domain = self.user1['username'] + '.' + home_dir + '.' + domain
        
        # this should get the users .toc file
        headers = {'host': user_domain }
        req = self.endpoint + '/'
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('root' in rspJson)
        toc_root_uuid = rspJson['root']
        req = self.endpoint + "/groups/" + toc_root_uuid 
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        
        # "tall_deleteme" should be a link
        req = req + "/link/tall_deleteme"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        
        # And we should be able to query directly
        user_file = "tall_deleteme." + user_domain
        req = self.endpoint + "/"
        headers = {'host': user_file}
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        
        # Delete "tall_deleteme"  
        user_file = "tall_deleteme." + user_domain
        req = self.endpoint + "/"
        headers = {'host': user_file}
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        
        # link in user TOC should be removed
        req = self.endpoint + "/groups/" + toc_root_uuid +  "/link/tall_deleteme"
        rsp = requests.get(req, headers=headers)
        self.assertEqual(rsp.status_code, 404)
        
         
        
    def testNoHostHeader(self):
        req = self.endpoint + "/"
        rsp = requests.get(req)
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.headers['content-type'], 'application/json')
        rspJson = json.loads(rsp.text)
        self.assertTrue('root' in rspJson)
                   
    
    def testPutDomain(self): 
        domain_name = "dirtest_putdomain"
        
        # get toc root uuid
        req = self.endpoint + "/"
        rsp = requests.get(req)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('root' in rspJson)
        toc_root_uuid = rspJson['root']
        
        # get toc 'test' group uuid
        req = self.endpoint + "/groups/" + toc_root_uuid 
        rsp = requests.get(req)
        self.assertEqual(rsp.status_code, 200)
        req = self.endpoint + "/groups/" + toc_root_uuid + "/links/test" 
        rsp = requests.get(req)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue("link" in rspJson)
        link = rspJson['link']
        test_group_uuid = link['id']
        
                 
        # verify that the domain name is not present
        req = self.endpoint + "/groups/" + test_group_uuid + "/links/" + domain_name 
        rsp = requests.get(req)
        self.assertTrue(rsp.status_code in (404, 410))
        
        # create a new domain
        domain = domain_name + '.' + config.get('domain')
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.put(req, headers=headers)
        self.assertEqual(rsp.status_code, 201)
        rspJson = json.loads(rsp.text)
         
        # external link should exist now
        req = self.endpoint + "/groups/" + test_group_uuid + "/links/" + domain_name 
         
        rsp = requests.get(req)
       
        self.assertEqual(rsp.status_code, 200)
         
        # delete the domain
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.delete(req, headers=headers)
        self.assertEqual(rsp.status_code, 200)
        
        # external link should be gone
        req = self.endpoint + "/groups/" + test_group_uuid + "/links/" + domain_name 
        rsp = requests.get(req)
        self.assertEqual(rsp.status_code, 410)  
        
    def testWatchdog(self):
        domain_name = "dirtest_watchdogadd"
        
        # get toc root uuid
        req = self.endpoint + "/"
        rsp = requests.get(req)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('root' in rspJson)
        toc_root_uuid = rspJson['root']
        
        # get toc 'test' group uuid
        req = self.endpoint + "/groups/" + toc_root_uuid 
        rsp = requests.get(req)
        self.assertEqual(rsp.status_code, 200)
        req = self.endpoint + "/groups/" + toc_root_uuid + "/links/test" 
        rsp = requests.get(req)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue("link" in rspJson)
        link = rspJson['link']
        test_group_uuid = link['id']
                  
        # verify that the domain name is not present
        req = self.endpoint + "/groups/" + test_group_uuid + "/links/" + domain_name 
        rsp = requests.get(req)
        self.assertTrue(rsp.status_code in (404, 410))
        
        # copy file to target domain
        src_file = "../test_files/tall.h5"
        des_file = "../../data/test/" + domain_name + ".h5"
        copyfile(src_file, des_file)
        
        # sleep to give the watchdog time to update the toc
        time.sleep(2)  
         
        # external link should exist now
        req = self.endpoint + "/groups/" + test_group_uuid + "/links/" + domain_name 
         
        rsp = requests.get(req)
       
        self.assertEqual(rsp.status_code, 200)
              
        # delete the file
        os.remove(des_file)
        # sleep to give the watchdog time to update the toc
        time.sleep(2)
          
        # external link should be gone
        req = self.endpoint + "/groups/" + test_group_uuid + "/links/" + domain_name 
        rsp = requests.get(req)
        self.assertEqual(rsp.status_code, 410)    
          
    def testDeleteToc(self):
        #test DELETE toc
        req = self.endpoint + "/"
        rsp = requests.delete(req)
        self.assertEqual(rsp.status_code, 403)
        
    def testPutToc(self):
        # test PUT toc
        req = self.endpoint + "/"
        rsp = requests.put(req)
        # status code be Forbiden or Conflict based on TOC file
        # existing or not
        self.assertTrue(rsp.status_code in (403, 409))
        
    def testDeleteRoot(self):
        req = self.endpoint + "/"
        rsp = requests.get(req)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('root' in rspJson)
        root_uuid = rspJson['root']
        req = self.endpoint + "/groups/" + root_uuid 
        rsp = requests.delete(req)
        self.assertEqual(rsp.status_code, 403)
        
    def testPutLink(self):
        req = self.endpoint + "/"
        rsp = requests.get(req)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('root' in rspJson)
        root_uuid = rspJson['root']
        name = 'dirtest.testPutLink'
        req = helper.getEndpoint() + "/groups/" + root_uuid + "/links/" + name 
        payload = {"h5path": "somewhere"}
        # verify softlink does not exist
        rsp = requests.get(req, data=json.dumps(payload))
        self.assertEqual(rsp.status_code, 404)
        # make request
        rsp = requests.put(req, data=json.dumps(payload))
        self.assertEqual(rsp.status_code, 403)
        
    def testDeleteLink(self):
        req = self.endpoint + "/"
        rsp = requests.get(req)
        self.assertEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue('root' in rspJson)
        root_uuid = rspJson['root']
        req = self.endpoint + "/groups/" + root_uuid + "/links/test" 
        rsp = requests.get(req)
        self.assertEqual(rsp.status_code, 200)
        rsp = requests.delete(req)  # try to delete the link
        self.assertEqual(rsp.status_code, 403)
        
        
if __name__ == '__main__':
    unittest.main()
