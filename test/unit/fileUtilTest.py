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
import unittest
import time
import sys
from tornado.web import HTTPError
 

sys.path.append('../../server')
from fileUtil import getFilePath, getDomain
import config


class FileUtilTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(FileUtilTest, self).__init__(*args, **kwargs)
        # main
        
    def testDomaintoFilePath(self):
        domain = 'tall.' + config.get('domain')  
        filePath = getFilePath(domain)
        self.assertEqual(filePath, "../data/tall.h5")
        # dot in front
        domain = '.tall.' + config.get('domain')  
        self.assertRaises(HTTPError, getFilePath, domain)
        # two dots
        domain = 'two..dots.' + config.get('domain')  
        self.assertRaises(HTTPError, getFilePath, domain)
        # no dot before domain
        domain = 'nodot' + config.get('domain')  
        self.assertRaises(HTTPError, getFilePath, domain)
        
    def testGetDomain(self):
        filePath = "tall.h5"
        domain = getDomain(filePath)
        self.assertEqual(domain, 'tall.' + config.get('domain'))
        filePath = "somevalue"
        domain = getDomain(filePath)
        self.assertEqual(domain, 'somevalue.' + config.get('domain'))
       
        
            
             
if __name__ == '__main__':
    #setup test files
    
    unittest.main()
    
