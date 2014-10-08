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

class SearchTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(SearchTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))
       
    def testGet(self):
        logging.info("SearchTest.testGet")
        for domain_name in ('tall',):
            domain = domain_name + '.' + config.get('domain')   
            rootUUID = helper.getRootUUID(domain)     
            req = self.endpoint + "/search/?path=/g1/g1.1/dset1.1.1" 
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            self.failUnlessEqual(rsp.status_code, 200)
 
       
if __name__ == '__main__':
    unittest.main()