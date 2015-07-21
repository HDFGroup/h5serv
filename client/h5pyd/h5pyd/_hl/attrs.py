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

"""
    Implements high-level operations for attributes.
    
    Provides the AttributeManager class, available on high-level objects
    as <obj>.attrs.
"""

from __future__ import absolute_import

import numpy
import sys 
 
from . import base
from .base import phil, with_phil
from .dataset import readtime_dtype
from .datatype import Datatype
from .objectid import GroupID, DatasetID, TypeID

#from hdf5db import Hdf5db
from .. import hdf5dtype

class AttributeManager(base.MutableMappingHDF5, base.CommonStateObject):

    """
        Allows dictionary-style access to an HDF5 object's attributes.

        These are created exclusively by the library and are available as
        a Python attribute at <object>.attrs

        Like Group objects, attributes provide a minimal dictionary-
        style interface.  Anything which can be reasonably converted to a
        Numpy array or Numpy scalar can be stored.

        Attributes are automatically created on assignment with the
        syntax <obj>.attrs[name] = value, with the HDF5 type automatically
        deduced from the value.  Existing attributes are overwritten.

        To modify an existing attribute while preserving its type, use the
        method modify().  To specify an attribute of a particular type and
        shape, use create().
    """

    def __init__(self, parent):
        """ Private constructor.
        """
        self._parent = parent
       
        if isinstance(parent.id, GroupID):
            self._req_prefix = "/groups/" + parent.id.uuid + "/attributes/"
        elif isinstance(parent.id, TypeID):
            self._req_prefix = "/datatypes/" + parent.id.uuid + "/attributes/"
        elif isinstance(parent.id, DatasetID):
            self._req_prefix = "/datasets/" + parent.id.uuid + "/attributes/"
        else:
            print "unknown id"
            self._req_prefix = "<unknown>"
            

    @with_phil
    def __getitem__(self, name):
        """ Read the value of an attribute.
        """
        #attr = h5a.open(self._id, self._e(name))
        req = self._req_prefix + name
        attr_json = self._parent.GET(req)
        shape_json = attr_json['shape']
        type_json = attr_json['type']
        #if attr.get_space().get_simple_extent_type() == h5s.NULL:
        if shape_json['class'] == 'H5S_NULL':
            raise IOError("Empty attributes cannot be read")
        value_json = attr_json['value']

        #dtype = readtime_dtype(attr.dtype, [])
        dtype = hdf5dtype.createDataType(type_json)
        
        #shape = attr.shape
        if 'dims' in shape_json:
            shape = shape_json['dims']
        else:
            shape = ()
        
        # Do this first, as we'll be fiddling with the dtype for top-level
        # array types
        #htype = h5t.py_create(dtype)
        htype = dtype

        # NumPy doesn't support top-level array types, so we have to "fake"
        # the correct type and shape for the array.  For example, consider
        # attr.shape == (5,) and attr.dtype == '(3,)f'. Then:
        if dtype.subdtype is not None:
            subdtype, subshape = dtype.subdtype
            shape = attr.shape + subshape   # (5, 3)
            dtype = subdtype                # 'f'
            
        #arr = numpy.ndarray(shape, dtype=dtype, order='C')
        #attr.read(arr, mtype=htype)
         
        #print "value:", rsp['value']
        #print "new_dtype:", new_dtype
        arr = numpy.array(value_json, dtype=htype)

        if len(arr.shape) == 0:
            return arr[()]
        return arr

    @with_phil
    def __setitem__(self, name, value):
        """ Set a new attribute, overwriting any existing attribute.

        The type and shape of the attribute are determined from the data.  To
        use a specific type or shape, or to preserve the type of an attribute,
        use the methods create() and modify().
        """
        self.create(name, data=value, dtype=base.guess_dtype(value))

    @with_phil
    def __delitem__(self, name):
        """ Delete an attribute (which must already exist). """
        req = self._req_prefix + name
        self._parent.DELETE(req)
        #h5a.delete(self._id, self._e(name))

    def create(self, name, data, shape=None, dtype=None):
        """ Create a new attribute, overwriting any existing attribute.

        name
            Name of the new attribute (required)
        data
            An array to initialize the attribute (required)
        shape
            Shape of the attribute.  Overrides data.shape if both are
            given, in which case the total number of points must be unchanged.
        dtype
            Data type of the attribute.  Overrides data.dtype if both
            are given.
        """

        
        with phil:
                
            # First, make sure we have a NumPy array.  We leave the data
            # type conversion for HDF5 to perform.
            data = numpy.asarray(data, order='C')
    
            if shape is None:
                shape = data.shape
                
            use_htype = None    # If a committed type is given, we must use it
                                # in the call to h5a.create.
                                            
            if isinstance(dtype, Datatype):
                use_htype = dtype.id
                dtype = dtype.dtype
            elif dtype is None:
                dtype = data.dtype
            else:
                dtype = numpy.dtype(dtype) # In case a string, e.g. 'i8' is passed
 
            original_dtype = dtype  # We'll need this for top-level array types

            # Where a top-level array type is requested, we have to do some
            # fiddling around to present the data as a smaller array of
            # subarrays. 
            if dtype.subdtype is not None:
            
                subdtype, subshape = dtype.subdtype
                
                # Make sure the subshape matches the last N axes' sizes.
                if shape[-len(subshape):] != subshape:
                    raise ValueError("Array dtype shape %s is incompatible with data shape %s" % (subshape, shape))

                # New "advertised" shape and dtype
                shape = shape[0:len(shape)-len(subshape)]
                dtype = subdtype
                
            # Not an array type; make sure to check the number of elements
            # is compatible, and reshape if needed.
            else:
               
                if numpy.product(shape) != numpy.product(data.shape):
                    raise ValueError("Shape of new attribute conflicts with shape of data")

                if shape != data.shape:
                    data = data.reshape(shape)

            # We need this to handle special string types.
            data = numpy.asarray(data, dtype=dtype)
    
            # Make HDF5 datatype and dataspace for the H5A calls
            if use_htype is None:
                type_json = hdf5dtype.getTypeItem(dtype)
                #htype = h5t.py_create(original_dtype, logical=True)
                #htype2 = h5t.py_create(original_dtype)  # Must be bit-for-bit representation rather than logical
            else:
                htype = use_htype
                htype2 = None
                
            #space = h5s.create_simple(shape)

            # This mess exists because you can't overwrite attributes in HDF5.
            # So we write to a temporary attribute first, and then rename.
            
            #tempname = uuid.uuid4().hex
            
            req = self._req_prefix + name
            body = {}
            body['type'] = type_json
            body['shape'] = shape
            body['value'] = data.tolist()
            
            self._parent.PUT(req, body=body)
            
            """
            try:
                attr = h5a.create(self._id, self._e(tempname), htype, space)
            except:
                raise
            else:
                try:
                    attr.write(data, mtype=htype2)
                except:
                    attr.close()
                    h5a.delete(self._id, self._e(tempname))
                    raise
                else:
                    try:
                        # No atomic rename in HDF5 :(
                        if h5a.exists(self._id, self._e(name)):
                            h5a.delete(self._id, self._e(name))
                        h5a.rename(self._id, self._e(tempname), self._e(name))
                    except:
                        attr.close()
                        h5a.delete(self._id, self._e(tempname))
                        raise
            """
                        
    def modify(self, name, value):
        """ Change the value of an attribute while preserving its type.

        Differs from __setitem__ in that if the attribute already exists, its
        type is preserved.  This can be very useful for interacting with
        externally generated files.

        If the attribute doesn't exist, it will be automatically created.
        """
        with phil:
            if not name in self:
                self[name] = value
            else:
                value = numpy.asarray(value, order='C')

                attr = h5a.open(self._id, self._e(name))

                if attr.get_space().get_simple_extent_type() == h5s.NULL:
                    raise IOError("Empty attributes can't be modified")

                # Allow the case of () <-> (1,)
                if (value.shape != attr.shape) and not \
                   (numpy.product(value.shape) == 1 and numpy.product(attr.shape) == 1):
                    raise TypeError("Shape of data is incompatible with existing attribute")
                attr.write(value)

    @with_phil
    def __len__(self):
        """ Number of attributes attached to the object. """
        # I expect we will not have more than 2**32 attributes
        req = self._req_prefix
       
        # backup over the '/attributes/' part of the req
        req = req[:-(len('/attributes/'))]
        rsp = self._parent.GET(req)  # get parent obj
        count = rsp['attributeCount']
        # return h5a.get_num_attrs(self._id)
        return count

    def __iter__(self):
        """ Iterate over the names of attributes. """
        req = self._req_prefix
        # backup over the trailing slash in req
        req = req[:-1]
        rsp = self._parent.GET(req)
        attributes = rsp['attributes']
        with phil:
        
            attrlist = []
            for attr in attributes:
                attrlist.append(attr['name'])
            """
            def iter_cb(name, *args):
                #Callback to gather attribute names 
                attrlist.append(self._d(name))

            h5a.iterate(self._id, iter_cb)
            """
            

        for name in attrlist:
            yield name

    @with_phil
    def __contains__(self, name):
        """ Determine if an attribute exists, by name. """
        exists = True
        req = self._req_prefix + name
        try:
            self._parent.GET(req)
        except IOError:
            #todo - verify this is a 404 response
            exists = False
        return exists
            
        #return h5a.exists(self._id, self._e(name))

    @with_phil
    def __repr__(self):
        if not self._parent.id.id:
            return "<Attributes of closed HDF5 object>"
        return "<Attributes of HDF5 object at %s>" % id(self._parent.id)
