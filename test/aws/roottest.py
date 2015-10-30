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
import json
import base64

class RootTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(RootTest, self).__init__(*args, **kwargs)
        self.endpoint = 'https://' + config.get('server') + ':' + str(config.get('port'))
        #self.endpoint = "https://data.hdfgroup.org:7258"
    
    def testGetInfo(self):
    
        req = self.endpoint + "/info"
        rsp = requests.get(req, verify=False)
        self.failUnlessEqual(rsp.status_code, 200)
        self.failUnlessEqual(rsp.headers['content-type'], 'application/json')
        rspJson = json.loads(rsp.text)
        self.assertTrue('h5serv_version' in rspJson)
            
    def testGetDomain(self):
        domain = 'tall.' + config.get('domain')  
        
        req = self.endpoint + "/"
        headers = {'host': domain}
        rsp = requests.get(req, headers=headers, verify=False)
        self.failUnlessEqual(rsp.status_code, 200)
        self.failUnlessEqual(rsp.headers['content-type'], 'application/json')
        rspJson = json.loads(rsp.text)
         
        
        
if __name__ == '__main__':
    unittest.main()
