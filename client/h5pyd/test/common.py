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

from __future__ import absolute_import

import sys
import os
import shutil
import tempfile
import time


from six import unichr

import numpy as np
import h5pyd

if sys.version_info >= (2, 7) or sys.version_info >= (3, 2):
    import unittest as ut
else:
    try:
        import unittest2 as ut
    except ImportError:
        raise ImportError(
            'unittest2 is required to run the test suite with python-%d.%d'
            % (sys.version_info[:2])
            )


# Check if non-ascii filenames are supported
# Evidently this is the most reliable way to check
# See also h5py issue #263 and ipython #466
# To test for this, run the testsuite with LC_ALL=C
try:
    testfile, fname = tempfile.mkstemp(unichr(0x03b7))
except UnicodeError:
    UNICODE_FILENAMES = False
else:
    UNICODE_FILENAMES = True
    os.close(testfile)
    os.unlink(fname)
    del fname
    del testfile


class TestCase(ut.TestCase):

    """
        Base class for unit tests.
    """
    
    @property
    def endpoint(self):
        return "http://127.0.0.1:5000"
        
    @property
    def base_domain(self):
        return  self.test_dir + ".h5pyd_test.hdfgroup.org"
    
    @classmethod
    def setUpClass(cls):
        pass
        #cls.tempdir = tempfile.mkdtemp(prefix='h5py-test_')

    @classmethod
    def tearDownClass(cls):
        pass
        #shutil.rmtree(cls.tempdir)
        
    def setUp(self):
        self.test_dir = str(int(time.time()))
        #self.f = h5py.File(self.mktemp(), 'w')
        
    def tearDown(self):
        try:
            if self.f:
                self.f.close()
        except:
            pass

    if not hasattr(ut.TestCase, 'assertSameElements'):
        # shim until this is ported into unittest2
        def assertSameElements(self, a, b):
            for x in a:
                match = False
                for y in b:
                    if x == y:
                        match = True
                if not match:
                    raise AssertionError("Item '%s' appears in a but not b" % x)

            for x in b:
                match = False
                for y in a:
                    if x == y:
                        match = True
                if not match:
                    raise AssertionError("Item '%s' appears in b but not a" % x)

    def assertArrayEqual(self, dset, arr, message=None, precision=None):
        """ Make sure dset and arr have the same shape, dtype and contents, to
            within the given precision.

            Note that dset may be a NumPy array or an HDF5 dataset.
        """
        if precision is None:
            precision = 1e-5
        if message is None:
            message = ''
        else:
            message = ' (%s)' % message

        if np.isscalar(dset) or np.isscalar(arr):
            self.assert_(
                np.isscalar(dset) and np.isscalar(arr),
                'Scalar/array mismatch ("%r" vs "%r")%s' % (dset, arr, message)
                )
            self.assert_(
                dset - arr < precision,
                "Scalars differ by more than %.3f%s" % (precision, message)
                )
            return

        self.assert_(
            dset.shape == arr.shape,
            "Shape mismatch (%s vs %s)%s" % (dset.shape, arr.shape, message)
            )
        self.assert_(
            dset.dtype == arr.dtype,
            "Dtype mismatch (%s vs %s)%s" % (dset.dtype, arr.dtype, message)
            )
            
        if arr.dtype.names is not None:
            for n in arr.dtype.names:
                message = '[FIELD %s] %s' % (n, message)
                self.assertArrayEqual(dset[n], arr[n], message=message, precision=precision)
        elif arr.dtype.kind in ('i', 'f'):
            self.assert_(
                np.all(np.abs(dset[...] - arr[...]) < precision),
                "Arrays differ by more than %.3f%s" % (precision, message)
                )
        else:
            self.assert_(
                np.all(dset[...] == arr[...]),
                "Arrays are not equal (dtype %s) %s" % (arr.dtype.str, message)
                )

    def assertNumpyBehavior(self, dset, arr, s):
        """ Apply slicing arguments "s" to both dset and arr.
        
        Succeeds if the results of the slicing are identical, or the
        exception raised is of the same type for both.
        
        "arr" must be a Numpy array; "dset" may be a NumPy array or dataset.
        """
        exc = None
        try:
            arr_result = arr[s]
        except Exception as e:
            exc = type(e)
            
        if exc is None:
            self.assertArrayEqual(dset[s], arr_result)
        else:
            with self.assertRaises(exc):
                dset[s]
