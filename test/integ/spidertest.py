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

class SpiderTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(SpiderTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))
        self.verifiedLinks = set()
        self.unverifiedLinks = set()  
        self.headers = {} 
        
    def validateLinks(self, href):
        print 'validate:', href
        self.verifiedLinks.add(href)
        # convert to local endpoint
        domain = config.get('domain')
        npos = href.find(domain)
        if npos > 0:
            req = self.endpoint + href[(npos+len(domain)):]
        else:
            req = href
        
        print 'sending request:', req
        rsp = requests.get(req, headers=self.headers)
        self.failUnlessEqual(rsp.status_code, 200)
        rspJson = json.loads(rsp.text)
        self.assertTrue("links" in rspJson)
        links = rspJson["links"]
        self.assertTrue(len(links) > 0)
        for link in links:
            self.assertTrue('href' in link)
            url = link['href']
            if url in self.verifiedLinks:
                continue
            print 'adding link:', url
            self.unverifiedLinks.add(url)
            
        while len(self.unverifiedLinks) > 0:
            link = self.unverifiedLinks.pop()
            self.validateLinks(link)     
        
       
    def testHateoas(self):
        domains = ('tall', 'tall_ro', 'group1k')
        for name in domains:     
            domain = name + '.' + config.get('domain') 
            self.verifiedLinks.clear()
            self.unverifiedLinks.clear()
            req = self.endpoint + "/"
            self.headers = {'host': domain}
            self.validateLinks(self.endpoint + "/")
         
        
     
    
        
if __name__ == '__main__':
    unittest.main()