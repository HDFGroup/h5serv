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
        self.verifiedhrefs = set()
        self.unverifiedhrefs = set()  
        self.headers = {} 
        
    def validateHrefs(self, href):
        self.verifiedhrefs.add(href)
        # convert to local endpoint
        domain = config.get('domain')
        npos = href.find(domain)
        if npos > 0:
            req = self.endpoint + href[(npos+len(domain)):]
        else:
            req = href
        
        rsp = requests.get(req, headers=self.headers)
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.headers['content-type'], 'application/json')
        rspJson = json.loads(rsp.text)
        self.assertTrue("hrefs" in rspJson)
        hrefs = rspJson["hrefs"]
        self.assertTrue(len(hrefs) > 0)
        links = {}
        for link in hrefs:
            self.assertTrue('href' in link)
            self.assertTrue('rel' in link)
            rel = link['rel']
            url = link['href']
            self.assertTrue(rel not in links)
            links[rel] = url
            if url in self.verifiedhrefs:
                continue
            self.unverifiedhrefs.add(url)
        self.assertTrue('self' in links)
        self.assertTrue('root' in links)
        
        while len(self.unverifiedhrefs) > 0:
            link = self.unverifiedhrefs.pop()
            self.validateHrefs(link)     
        
       
    def testHateoas(self):
        domains = ('tall', 'tall_ro', 'group1k')
        for name in domains:     
            domain = name + '.' + config.get('domain') 
            self.verifiedhrefs.clear()
            self.unverifiedhrefs.clear()
            req = self.endpoint + "/"
            self.headers = {'host': domain}
            self.validateHrefs(self.endpoint + "/")
         
        
        
if __name__ == '__main__':
    unittest.main()