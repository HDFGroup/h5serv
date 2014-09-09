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
import sys
import os
import os.path as op
import stat
import logging
import shutil

sys.path.append('../../server')
from hdf5db import Hdf5db
import config


def getFile(name, tgt=None, ro=False):
    src = config.get('testfiledir') + name
    logging.info("copying file to this directory: " + src)
    if not tgt:
        tgt = name
    if op.isfile(tgt):
        # make sure it's writable, before we copy over it
        os.chmod(tgt, stat.S_IWRITE|stat.S_IREAD)
    shutil.copyfile(src, tgt)
    if ro:
        logging.info('make read-only')
        os.chmod(tgt, stat.S_IREAD)

class Hdf5dbTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Hdf5dbTest, self).__init__(*args, **kwargs)
        # main
        logging.info('init!')
        getFile('tall.h5')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
    
    def testGetUUIDByPath(self):
        # get test file
        g1Uuid = None
        with Hdf5db('tall.h5') as db:
            g1Uuid = db.getUUIDByPath('/g1')
            self.failUnlessEqual(len(g1Uuid), config.get('uuidlen'))
            obj = db.getObjByPath('/g1')
            self.failUnlessEqual(obj.name, '/g1')
            for name in obj:
                g = obj[name]
            g1links = db.getItems(g1Uuid)
            self.failUnlessEqual(len(g1links), 2)
            for item in g1links:
                self.failUnlessEqual(len(item['uuid']), config.get('uuidlen'))
          
        # end of with will close file
        # open again and verify we can get obj by name
        with Hdf5db('tall.h5') as db:
            obj = db.getGroupObjectByUuid(g1Uuid) 
            g1 = db.getObjByPath('/g1')
            self.failUnlessEqual(obj, g1)
               
    def testGroupOperations(self):
        # get test file
        with Hdf5db('tall.h5') as db:
            rootuuid = db.getUUIDByPath('/')
            root = db.getGroupObjectByUuid(rootuuid)
            self.failUnlessEqual('/', root.name)
            rootLinks = db.getItems(rootuuid)
            self.failUnlessEqual(len(rootLinks), 2)
            g1uuid = db.getUUIDByPath("/g1")
            self.failUnlessEqual(len(g1uuid), config.get('uuidlen'))
            g1Links = db.getItems(g1uuid)
            self.failUnlessEqual(len(g1Links), 2)
            
            g11uuid = db.getUUIDByPath("/g1/g1.1")
            db.deleteObjectByUuid(g11uuid)
            
    def testCreateGroup(self):
        # get test file
        getFile('tall.h5', 'tall_newgrp.h5')
        with Hdf5db('tall_newgrp.h5') as db:
            rootUuid = db.getUUIDByPath('/')
            numRootChildren = len(db.getItems(rootUuid))
            self.assertEqual(numRootChildren, 2)
            newGrpUuid = db.createGroup()
            newGrp = db.getGroupObjectByUuid(newGrpUuid)
            self.assertNotEqual(newGrp, None)
            db.linkObject(rootUuid, newGrpUuid, 'g3')
            numRootChildren = len(db.getItems(rootUuid))
            self.assertEqual(numRootChildren, 3)
            # verify linkObject can be called idempotent-ly 
            db.linkObject(rootUuid, newGrpUuid, 'g3')
            
    def testGetItemsBatch(self):
        # get test file
        getFile('group100.h5')
        marker = None
        count = 0
        with Hdf5db('group100.h5') as db:
            rootUuid = db.getUUIDByPath('/')
            while True:
                # get items 13 at a time
                batch = db.getItems(rootUuid, None, marker, 13) 
                if len(batch) == 0:
                    break   # done!
                count += len(batch)
                lastItem = batch[len(batch) - 1]
                marker = lastItem['name']
        self.assertEqual(count, 100)
        
    def testGetItemsSoftlink(self):
        items = None
        with Hdf5db('tall.h5') as db:
            grpUuid = db.getUUIDByPath('/g1/g1.2/g1.2.1')
            items = db.getItems(grpUuid)
            self.assertEqual(len(items), 1)
            item = items[0]
            self.assertTrue('uuid' not in item)
            self.assertEqual(item['name'], 'slink')
            self.assertEqual(item['class'], 'SoftLink')
            self.assertEqual(item['path'], 'somevalue')
    
             
            
    def testDeleteLink(self): 
        # get test file
        getFile('tall.h5', 'tall_grpdelete.h5')
        with Hdf5db('tall_grpdelete.h5') as db:
            rootUuid = db.getUUIDByPath('/')
            numRootChildren = len(db.getItems(rootUuid))
            self.assertEqual(numRootChildren, 2)
            db.unlinkItem(rootUuid, "g2")
            numRootChildren = len(db.getItems(rootUuid))
            self.assertEqual(numRootChildren, 1)   
    
                  
    def testReadOnlyGetUUID(self):
        # get test file
        getFile('tall.h5', 'tall_ro.h5', True)
        g1Uuid = None
        with Hdf5db('tall_ro.h5') as db:
            g1Uuid = db.getUUIDByPath('/g1')
            self.failUnlessEqual(len(g1Uuid), config.get('uuidlen'))
            obj = db.getObjByPath('/g1')
            self.failUnlessEqual(obj.name, '/g1')
    
        # end of with will close file
        # open again and verify we can get obj by name
        with Hdf5db('tall_ro.h5') as db:
            obj = db.getGroupObjectByUuid(g1Uuid) 
            g1 = db.getObjByPath('/g1')
            self.failUnlessEqual(obj, g1)
            g1links = db.getItems(g1Uuid)
            self.failUnlessEqual(len(g1links), 2)
            for item in g1links:
                self.failUnlessEqual(len(item['uuid']), config.get('uuidlen'))
    
if __name__ == '__main__':
    #setup test files
    
    unittest.main()
    

 



