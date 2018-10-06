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
import os
from tornado.web import HTTPError

from h5serv.fileUtil import getFilePath, getDomain, posixpath, join

import config

class FileUtilTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(FileUtilTest, self).__init__(*args, **kwargs)
        # main
    
    def testPosixPath(self):
        path1 = "dir1\\dir2"
        pp = posixpath(path1)
        if os.name == 'nt':
            self.assertEqual(pp, "dir1/dir2")
        else:
            self.assertEqual(pp, path1)  # no conversion on unix
            
    def testJoin(self):
        path1 = "dir1\\dir2"
        path2 = "myfile.h5"
        pp = join(path1, path2)
        if os.name == 'nt':
            self.assertEqual(pp, "dir1/dir2/myfile.h5")
        else:
            self.assertEqual(pp, "dir1\\dir2/myfile.h5")  # no conversion on unix
           
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
        filePath = "subdir/tall.h5"
        domain = getDomain(filePath)
        self.assertEqual(domain, 'tall.subdir.' + config.get('domain'))
        
        filePath = os.path.join(config.get('datapath'), 'subdir/tall.h5')
        
        domain = getDomain(filePath)
        self.assertEqual(domain, 'tall.subdir.' + config.get('domain'))
        
        filePath = os.path.join(config.get('datapath'), 'subdir/tall.h5')
        filePath = os.path.abspath(filePath)
        domain = getDomain(filePath)
        self.assertEqual(domain, 'tall.subdir.' + config.get('domain'))
        
        filePath = os.path.join(config.get('datapath'), 'home/test_user1/tall.h5')
        domain = getDomain(filePath)
        self.assertEqual(domain, 'tall.test_user1.home.' + config.get('domain'))
        
        filePath = '../data/home/test_user1/tall.h5'
        domain = getDomain(filePath)
        self.assertEqual(domain, 'tall.test_user1.home.' + config.get('domain'))
        
        #domainpath = fileUtil.getDomain(grppath, base_domain=base_domain)
        
        filePath = "../data"
        domain = getDomain(filePath)
        self.assertEqual(domain, config.get('domain'))
        
        # verify backslashes are ok for windows...
        if os.name == 'nt':
            filePath = "subdir\\subsubdir\\tall.h5"
            domain = getDomain(filePath)
            self.assertEqual(domain, 'tall.subsubdir.subdir.' + config.get('domain'))          
             
if __name__ == '__main__':
    #setup test files
    
    unittest.main()
    
