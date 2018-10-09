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

from h5serv.timeUtil import unixTimeToUTC

import config

class TimeUtilTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TimeUtilTest, self).__init__(*args, **kwargs)
        # main
        
    def testConvertUnixTimetoUTC(self):
        # get test file
        now = time.time()
        utcTime = unixTimeToUTC(now)
        print(utcTime)
        self.assertEqual(len(utcTime), 20)
        self.assertTrue(utcTime.startswith('20'))
        self.assertTrue(utcTime.endswith('Z'))
        
            
             
if __name__ == '__main__':
    #setup test files
    
    unittest.main()
    
