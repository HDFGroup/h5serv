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
        filename = "objref_test." + self.base_domain
        print filename
        f = h5py.File(filename, 'w')
        self.assertTrue(f.id.id is not None)
        self.assertTrue('/' in f)      
        r = f['/']
         
        r.create_group('g1')
        self.assertTrue('g1' in r)
        g1 = r['g1']
        print g1.name
        
        g11 = g1.create_group('g1.1')
        
        g11_ref = g11.ref 
        print g11_ref
        
        # todo - fix
        #self.assertTrue(isinstance(g11_ref, h5py.Reference))
         
        #print (f[g1ref] == g1)
      
        
        r.create_group('g2')
        self.assertEqual(len(r), 2)
        g2 = r['g2']
        
        g11ref = g2[g11_ref]
        print g11ref
        print g11ref.name
        
        
        # todo - special_dtype not implemented
        #dt = h5py.special_dtype(ref=h5py.Reference)
        #print dt
        
        dset = g1.create_dataset('ints', (10,), dtype='i8')
        
        #g2.attrs['dataset'] = dset.ref
        
        # todo - references as data will need h5pyd equivalent of h5t module
        # g2.attrs.create('dataset', dset.ref, dtype=dt)
         
         
        f.close()
        
         
        
if __name__ == '__main__':
    ut.main()


     
    
