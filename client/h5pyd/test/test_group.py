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
import h5pyd as h5py
from common import ut, TestCase

        
class TestGroup(TestCase):
    
        
    def test_create(self):
        filename = "new_group." + self.base_domain
        f = h5py.File(filename, 'w')
        self.assertTrue(f.id.id is not None)
        self.assertTrue('/' in f)      
        r = f['/']
        
        self.assertEqual(len(r), 0)
        self.assertTrue(isinstance(r, h5py.Group))
        self.assertTrue(r.name, '/')
        self.assertEqual(len(r.attrs.keys()), 0)
        
        self.assertFalse('g1' in r)
         
        r.create_group('g1')
        self.assertTrue('g1' in r)
        r.create_group('g2')
        self.assertEqual(len(r), 2)
        keys = []
        # iterate through keys
        for k in r:
            keys.append(k)
            
        self.assertEqual(len(keys), 2)
        self.assertTrue('g1' in keys)
        self.assertTrue('g2' in keys)
        
        self.assertTrue('g1' in r)
        self.assertTrue('/g1' in r)
        g1 = r.get('/g1')
        self.assertTrue(g1.id.id)
        self.assertEqual(g1.name, '/g1')
        
        g1_class = r.get('g1', getclass=True)
        self.assertEqual(g1_class, h5py.Group)
        
        # try creating a group that already exists
        try:
            r.create_group('g1')
            self.assertTrue(False)
        except ValueError:
            pass # expected
            
        r.create_group('g3')
        self.assertEqual(len(r), 3)
        del r['g3']
        self.assertEqual(len(r), 2)
        
        r.require_group('g4')
        self.assertEqual(len(r), 3)
        r.require_group('g2') 
        self.assertEqual(len(r), 3)
        
        g1_1 = r.create_group("g1/g1.1")
        self.assertEqual(len(r), 3)
        self.assertEqual(len(g1), 1)
        self.assertEqual(len(g1_1), 0)    
        
        # create a hardlink
        r['g1.1'] = g1_1
        self.assertEqual(len(r), 4)
        
        # create a softlink
        r['mysoftlink'] = h5py.SoftLink('/g1/g1.1')
        self.assertEqual(len(r), 5)
        #print r.get_link_json("/mysoftlink")
        slink = r['mysoftlink']
        self.assertEqual(slink.id, g1_1.id)
        
        
        # create a external hardlink
        r['myexternallink'] = h5py.ExternalLink("somefile", "somepath")
        
        # test getclass
        g1_class = r.get('g1', getclass=True)
        self.assertEqual(g1_class, h5py.Group)
        linkee_class = r.get('mysoftlink', getclass=True)
        self.assertEqual(linkee_class, h5py.Group)
        link_class = r.get('mysoftlink', getclass=True, getlink=True)
        self.assertEqual(link_class, h5py.SoftLink)
        softlink = r.get('mysoftlink', getlink=True)
        self.assertEqual(softlink.path, '/g1/g1.1')
        
        try:
            linkee_class = r.get('myexternallink', getclass=True)
            self.assertTrue(False)
        except IOError:
            pass # expected - not implemented
        
        link_class = r.get('myexternallink', getclass=True, getlink=True)
        self.assertEqual(link_class, h5py.ExternalLink)
        external_link = r.get('myexternallink', getlink=True)
        self.assertEqual(external_link.path, 'somepath')
        
        del r['mysoftlink']
        self.assertEqual(len(r), 5)
        
        del r['myexternallink']
        self.assertEqual(len(r), 4)
        
        f.close()
        self.assertEqual(f.id.id, 0)
        
        
         
        
if __name__ == '__main__':
    ut.main()


     
    
