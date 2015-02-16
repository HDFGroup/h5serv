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
import errno
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
        
def removeFile(name):
    try:
        os.stat(name)
    except OSError:
        return;   # file does not exist
    os.remove(name)

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
            g1links = db.getLinkItems(g1Uuid)
            self.failUnlessEqual(len(g1links), 2)
            for item in g1links:
                self.failUnlessEqual(len(item['uuid']), config.get('uuidlen'))
          
        # end of with will close file
        # open again and verify we can get obj by name
        with Hdf5db('tall.h5') as db:
            obj = db.getGroupObjByUuid(g1Uuid) 
            g1 = db.getObjByPath('/g1')
            self.failUnlessEqual(obj, g1)
            
    def testGetCounts(self):
        with Hdf5db('tall.h5') as db:
            cnt = db.getNumberOfGroups()
            self.failUnlessEqual(cnt, 6)
            cnt = db.getNumberOfDatasets()
            self.failUnlessEqual(cnt, 4)
            cnt = db.getNumberOfDatatypes()
            self.failUnlessEqual(cnt, 0)
            
               
    def testGroupOperations(self):
        # get test file
        getFile('tall.h5', 'tall_del_g11.h5')
        with Hdf5db('tall_del_g11.h5') as db:
            rootuuid = db.getUUIDByPath('/')
            root = db.getGroupObjByUuid(rootuuid)
            self.failUnlessEqual('/', root.name)
            rootLinks = db.getLinkItems(rootuuid)
            self.failUnlessEqual(len(rootLinks), 2)
            g1uuid = db.getUUIDByPath("/g1")
            self.failUnlessEqual(len(g1uuid), config.get('uuidlen'))
            g1Links = db.getLinkItems(g1uuid)
            self.failUnlessEqual(len(g1Links), 2)
            g11uuid = db.getUUIDByPath("/g1/g1.1")
            db.deleteObjectByUuid("group", g11uuid)
            
    def testCreateGroup(self):
        # get test file
        getFile('tall.h5', 'tall_newgrp.h5')
        with Hdf5db('tall_newgrp.h5') as db:
            rootUuid = db.getUUIDByPath('/')
            numRootChildren = len(db.getLinkItems(rootUuid))
            self.assertEqual(numRootChildren, 2)
            newGrpUuid = db.createGroup()
            newGrp = db.getGroupObjByUuid(newGrpUuid)
            self.assertNotEqual(newGrp, None)
            db.linkObject(rootUuid, newGrpUuid, 'g3')
            numRootChildren = len(db.getLinkItems(rootUuid))
            self.assertEqual(numRootChildren, 3)
            # verify linkObject can be called idempotent-ly 
            db.linkObject(rootUuid, newGrpUuid, 'g3')
            
    def testGetLinkItemsBatch(self):
        # get test file
        getFile('group100.h5')
        marker = None
        count = 0
        with Hdf5db('group100.h5') as db:
            rootUuid = db.getUUIDByPath('/')
            while True:
                # get items 13 at a time
                batch = db.getLinkItems(rootUuid, marker=marker, limit=13) 
                if len(batch) == 0:
                    break   # done!
                count += len(batch)
                lastItem = batch[len(batch) - 1]
                marker = lastItem['title']
        self.assertEqual(count, 100)
        
    def testGetItemHardLink(self):
        with Hdf5db('tall.h5') as db:
            grpUuid = db.getUUIDByPath('/g1/g1.1')
            item = db.getLinkItemByUuid(grpUuid, "dset1.1.1")
            self.assertTrue('uuid' in item)
            self.assertEqual(item['title'], 'dset1.1.1')
            self.assertEqual(item['class'], 'H5L_TYPE_HARD')
            self.assertEqual(item['collection'], 'datasets')
            self.assertTrue('target' not in item)
            self.assertTrue('mtime' in item)
            self.assertTrue('ctime' in item)
        
    def testGetItemSoftLink(self):
        with Hdf5db('tall.h5') as db:
            grpUuid = db.getUUIDByPath('/g1/g1.2/g1.2.1')
            item = db.getLinkItemByUuid(grpUuid, "slink")
            self.assertTrue('uuid' not in item)
            self.assertEqual(item['title'], 'slink')
            self.assertEqual(item['class'], 'H5L_TYPE_SOFT')
            self.assertEqual(item['h5path'], 'somevalue')
            self.assertTrue('mtime' in item)
            self.assertTrue('ctime' in item)
            
    def testGetItemExternalLink(self):
        getFile('tall_with_udlink.h5')
        with Hdf5db('tall_with_udlink.h5') as db:
            grpUuid = db.getUUIDByPath('/g1/g1.2')
            item = db.getLinkItemByUuid(grpUuid, "extlink")
            self.assertTrue('uuid' not in item)
            self.assertEqual(item['title'], 'extlink')
            self.assertEqual(item['class'], 'H5L_TYPE_EXTERNAL')
            self.assertEqual(item['h5path'], 'somepath')
            self.assertEqual(item['file'], 'somefile')
            self.assertTrue('mtime' in item)
            self.assertTrue('ctime' in item)
            
    def testGetItemUDLink(self):
        getFile('tall_with_udlink.h5')
        with Hdf5db('tall_with_udlink.h5') as db:
            grpUuid = db.getUUIDByPath('/g2')
            item = db.getLinkItemByUuid(grpUuid, "udlink")
            self.assertTrue('uuid' not in item)
            self.assertEqual(item['title'], 'udlink')
            self.assertEqual(item['class'], 'H5L_TYPE_USER_DEFINED')
            self.assertTrue('h5path' not in item)
            self.assertTrue('file' not in item)
            self.assertTrue('mtime' in item)
            self.assertTrue('ctime' in item)
            
    def testGetNumLinks(self):
        items = None
        with Hdf5db('tall.h5') as db:
            g1= db.getObjByPath('/g1')
            numLinks = db.getNumLinksToObject(g1)
            self.assertEqual(numLinks, 1)
            
    def testGetLinks(self):
        g12_links = ('extlink', 'g1.2.1')
        hardLink = None
        externalLink = None
        getFile('tall_with_udlink.h5')
        with Hdf5db('tall_with_udlink.h5') as db:
            grpUuid = db.getUUIDByPath('/g1/g1.2')
            items = db.getLinkItems(grpUuid)
            self.assertEqual(len(items), 2)
            for item in items:
                self.assertTrue(item['title'] in g12_links)
                if item['class'] == 'H5L_TYPE_HARD':
                    hardLink = item
                elif item['class'] == 'H5L_TYPE_EXTERNAL':
                    externalLink = item
        self.assertEqual(hardLink['collection'], 'groups')
        self.assertTrue('uuid' in hardLink)
        self.assertTrue('uuid' not in externalLink)
        self.assertEqual(externalLink['h5path'], 'somepath')
        self.assertEqual(externalLink['file'], 'somefile')
        
            
    def testDeleteLink(self): 
        # get test file
        getFile('tall.h5', 'tall_grpdelete.h5')
        with Hdf5db('tall_grpdelete.h5') as db:
            rootUuid = db.getUUIDByPath('/')
            numRootChildren = len(db.getLinkItems(rootUuid))
            self.assertEqual(numRootChildren, 2)
            db.unlinkItem(rootUuid, "g2")
            numRootChildren = len(db.getLinkItems(rootUuid))
            self.assertEqual(numRootChildren, 1) 
            
    def testDeleteUDLink(self): 
        # get test file
        getFile('tall_with_udlink.h5')
        with Hdf5db('tall_with_udlink.h5') as db:
            g2Uuid = db.getUUIDByPath('/g2')
            numG2Children = len(db.getLinkItems(g2Uuid))
            self.assertEqual(numG2Children, 3)
            got_exception = False
            try:
                db.unlinkItem(g2Uuid, "udlink")
            except IOError as ioe:
                got_exception = True
                self.assertEqual(ioe.errno, errno.EPERM)
            self.assertTrue(got_exception)
            numG2Children = len(db.getLinkItems(g2Uuid))
            self.assertEqual(numG2Children, 3)
    
                  
    def testReadOnlyGetUUID(self):
        # get test file
        getFile('tall.h5', 'tall_ro.h5', True)
        # remove db file!
        removeFile('.tall_ro.h5')
        g1Uuid = None
        with Hdf5db('tall_ro.h5') as db:
            g1Uuid = db.getUUIDByPath('/g1')
            self.failUnlessEqual(len(g1Uuid), config.get('uuidlen'))
            obj = db.getObjByPath('/g1')
            self.failUnlessEqual(obj.name, '/g1')
    
        # end of with will close file
        # open again and verify we can get obj by name
        with Hdf5db('tall_ro.h5') as db:
            obj = db.getGroupObjByUuid(g1Uuid) 
            g1 = db.getObjByPath('/g1')
            self.failUnlessEqual(obj, g1)
            g1links = db.getLinkItems(g1Uuid)
            self.failUnlessEqual(len(g1links), 2)
            for item in g1links:
                self.failUnlessEqual(len(item['uuid']), config.get('uuidlen'))
                
    def testReadDataset(self):
         getFile('tall.h5')
         d111_values = None
         d112_values = None
         with Hdf5db('tall.h5') as db:
            d111Uuid = db.getUUIDByPath('/g1/g1.1/dset1.1.1')
            self.failUnlessEqual(len(d111Uuid), config.get('uuidlen'))
            d111_values = db.getDatasetValuesByUuid(d111Uuid)
            
            self.assertEqual(len(d111_values), 10)  
            for i in range(10):
                arr = d111_values[i]
                self.assertEqual(len(arr), 10)
                for j in range(10):
                    self.assertEqual(arr[j], i*j)
            
            d112Uuid = db.getUUIDByPath('/g1/g1.1/dset1.1.2')
            self.failUnlessEqual(len(d112Uuid), config.get('uuidlen'))
            d112_values = db.getDatasetValuesByUuid(d112Uuid) 
            self.assertEqual(len(d112_values), 20)
            for i in range(20):
                self.assertEqual(d112_values[i], i)
                
    def testReadZeroDimDataset(self):
         getFile('zerodim.h5')
         d111_values = None
         d112_values = None
         with Hdf5db('zerodim.h5') as db:
            dsetUuid = db.getUUIDByPath('/dset')
            self.failUnlessEqual(len(dsetUuid), config.get('uuidlen'))
            dset_value = db.getDatasetValuesByUuid(dsetUuid)
            self.assertEqual(dset_value, 42)
            
    def testReadAttribute(self):
        # getAttributeItemByUuid
        item = None
        getFile('tall.h5')
        with Hdf5db('tall.h5') as db:
            rootUuid = db.getUUIDByPath('/')
            self.failUnlessEqual(len(rootUuid), config.get('uuidlen'))
            item = db.getAttributeItem("groups", rootUuid, "attr1")
        
     
             
             
if __name__ == '__main__':
    #setup test files
    
    unittest.main()
    

 



