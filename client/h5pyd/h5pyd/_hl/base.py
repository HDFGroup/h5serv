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

import posixpath
import warnings
import weakref
import os
import sys
import json
import requests
import logging
import logging.handlers
#from .reference import Reference
from collections import (
    Mapping, MutableMapping, MappingView, KeysView, ValuesView, ItemsView
)

import six

class FakeLock():
    def __init__(self):
        pass
    def __enter__(self):
        pass
    def __exit__(self, a, b, c):
        pass
        
_phil = FakeLock()

# Python alias for access from other modules
phil = _phil

def with_phil(func):
    """ Locking decorator """
    """
    For h5yp source code compatiblity - jlr
    """

    import functools

    def wrapper(*args, **kwds):
        with _phil:
            return func(*args, **kwds)

    functools.update_wrapper(wrapper, func, ('__name__', '__doc__'))
    return wrapper
    
    
def guess_dtype(data):
    """ Attempt to guess an appropriate dtype for the object, returning None
    if nothing is appropriate (or if it should be left up the the array
    constructor to figure out)
    """
    """
    #todo
    with phil:
        if isinstance(data, h5r.RegionReference):
            return h5t.special_dtype(ref=h5r.RegionReference)
        if isinstance(data, h5r.Reference):
            return h5t.special_dtype(ref=h5r.Reference)
        if type(data) == bytes:
            return h5t.special_dtype(vlen=bytes)
        if type(data) == six.text_type:
           return h5t.special_dtype(vlen=six.text_type)
    """
    return None
 
class Reference():

    """
        Represents an HDF5 object reference

         
    """
    @property
    def id(self):
        """ Low-level identifier appropriate for this object """
        return self._id
        
    @property
    def objref(self):
        """ Weak reference to object """
        return self._objref  # return weak ref to ref'd object
      
        
    @with_phil
    def __init__(self, bind):
        """ Create a new Datatype object by binding to a low-level TypeID.
        """
        with phil:
            self._id = bind._id
            self._objref = weakref.ref(bind) 
                    
    @with_phil
    def __repr__(self):
        return "<HDF5 object reference>"
        

class CommonStateObject(object):

    """
        Mixin class that allows sharing information between objects which
        reside in the same HDF5 file.  Requires that the host class have
        a ".id" attribute which returns a low-level ObjectID subclass.

        Also implements Unicode operations.
    """

    @property
    def _lapl(self):
        """ Fetch the link access property list appropriate for this object
        """
        return dlapl

    @property
    def _lcpl(self):
        """ Fetch the link creation property list appropriate for this object
        """
        return dlcpl

    def _e(self, name, lcpl=None):
        """ Encode a name according to the current file settings.

        Returns name, or 2-tuple (name, lcpl) if lcpl is True

        - Binary strings are always passed as-is, h5t.CSET_ASCII
        - Unicode strings are encoded utf8, h5t.CSET_UTF8

        If name is None, returns either None or (None, None) appropriately.
        """
        def get_lcpl(coding):
            lcpl = self._lcpl.copy()
            lcpl.set_char_encoding(coding)
            return lcpl

        if name is None:
            return (None, None) if lcpl else None

        if isinstance(name, bytes):
            coding = h5t.CSET_ASCII
        else:
            try:
                name = name.encode('ascii')
                coding = h5t.CSET_ASCII
            except UnicodeEncodeError:
                name = name.encode('utf8')
                coding = h5t.CSET_UTF8

        if lcpl:
            return name, get_lcpl(coding)
        return name

    def _d(self, name):
        """ Decode a name according to the current file settings.

        - Try to decode utf8
        - Failing that, return the byte string

        If name is None, returns None.
        """
        if name is None:
            return None

        try:
            return name.decode('utf8')
        except UnicodeDecodeError:
            pass
        return name


class _RegionProxy(object):

    """
        Proxy object which handles region references.

        To create a new region reference (datasets only), use slicing syntax:

            >>> newref = obj.regionref[0:10:2]

        To determine the target dataset shape from an existing reference:

            >>> shape = obj.regionref.shape(existingref)

        where <obj> may be any object in the file. To determine the shape of
        the selection in use on the target dataset:

            >>> selection_shape = obj.regionref.selection(existingref)
    """

    def __init__(self, obj):
        self.id = obj.id
        self._name = None

    def __getitem__(self, args):
        pass
        """
        if not isinstance(self.id, h5d.DatasetID):
            raise TypeError("Region references can only be made to datasets")
        from . import selections
        selection = selections.select(self.id.shape, args, dsid=self.id)
        return h5r.create(self.id, b'.', h5r.DATASET_REGION, selection._id)
        """

    def shape(self, ref):
        pass
        """ Get the shape of the target dataspace referred to by *ref*. """
        """
        with phil:
            sid = h5r.get_region(ref, self.id)
            return sid.shape
        """

    def selection(self, ref):
        """ Get the shape of the target dataspace selection referred to by *ref*
        """
        pass
        """
        with phil:
            from . import selections
            sid = h5r.get_region(ref, self.id)
            return selections.guess_shape(sid)
        """


class HLObject(CommonStateObject):

    """
        Base class for high-level interface objects.
        self._name = name 
            self._id = root_json['root']   
            self._mode = mode
            self._created = root_json['created']
            self._modified = root_json['lastModified']   
            self._endpoint = endpoint   
            
    """

    @property
    def file(self):
        """ Return a File instance associated with this object """
        from . import files
        return files.File(self._id)

    @property
    def name(self):
        """ Return the full name of this object.  None if anonymous. """
        return self._name
        #return self._d(h5i.get_name(self.id))

    @property
    def parent(self):
        """Return the parent group of this object.

        This is always equivalent to obj.file[posixpath.dirname(obj.name)].
        ValueError if this object is anonymous.
        """
        if self.name is None:
            raise ValueError("Parent of an anonymous object is undefined")
        return self.file[posixpath.dirname(self.name)]


    @property
    def id(self):
        """ Low-level identifier appropriate for this object """
        return self._id

    @property
    def ref(self):
        """ An (opaque) HDF5 reference to this object """
        return Reference(self)
        #return h5r.create(self.id, b'.', h5r.OBJECT)

    @property
    def regionref(self):
        """Create a region reference (Datasets only).

        The syntax is regionref[<slices>]. For example, dset.regionref[...]
        creates a region reference in which the whole dataset is selected.

        Can also be used to determine the shape of the referenced dataset
        (via .shape property), or the shape of the selection (via the
        .selection property).
        """
        return "todo"
        #return _RegionProxy(self)

    @property
    def attrs(self):
        """ Attributes attached to this object """
        from . import attrs
        return attrs.AttributeManager(self)
        
        
    def GET(self, req):
        if self.id.endpoint is None:
            raise IOError("object not initialized")
        if self.id.domain is None:
            raise IOError("no domain defined")
         
        # try to do a GET from the domain
        req = self.id.endpoint + req
            
        headers = {'host': self.id.domain}
        self.log.info("GET: " + req)
        rsp = requests.get(req, headers=headers)
        self.log.info("RSP: " + str(rsp.status_code) + ':' + rsp.text)
        if rsp.status_code != 200:
             raise IOError(rsp.reason)
        #print "rsp text", rsp.text    
        rsp_json = json.loads(rsp.text)
         
                
        return rsp_json
        
    def PUT(self, req, body=None):
        if self.id.endpoint is None:
            raise IOError("object not initialized")
        if self.id.domain is None:
            raise IOError("no domain defined")
         
        # try to do a PUT to the domain
        req = self.id.endpoint + req
        
        data = json.dumps(body)
            
        headers = {'host': self.id.domain}
        self.log.info("PUT: " + req)
        rsp = requests.put(req, data=data, headers=headers)
        self.log.info("RSP: " + str(rsp.status_code) + ':' + rsp.text)
        if rsp.status_code not in (200, 201):
            raise IOError(rsp.reason)
        
        if rsp.text:
            rsp_json = json.loads(rsp.text)    
            return rsp_json
        
        
    def POST(self, req, body=None):
        if self.id.endpoint is None:
            raise IOError("object not initialized")
        if self.id.domain is None:
            raise IOError("no domain defined")
         
        # try to do a POST to the domain
        req = self.id.endpoint + req
        
        data = json.dumps(body)
            
        headers = {'host': self.id.domain}
        self.log.info("PST: " + req)
        rsp = requests.post(req, data=data, headers=headers)
        self.log.info("RSP: " + str(rsp.status_code) + ':' + rsp.text)
        if rsp.status_code not in (200, 201):
            raise IOError(rsp.reason)
        
        rsp_json = json.loads(rsp.text)
        return rsp_json
        
    def DELETE(self, req):
        if self.id.endpoint is None:
            raise IOError("object not initialized")
        if self.id.domain is None:
            raise IOError("no domain defined")
         
        # try to do a DELETE of the resource
        req = self.id.endpoint + req
        
        headers = {'host': self.id.domain}
        self.log.info("DEL: " + req)
        rsp = requests.delete(req, headers=headers)
        self.log.info("RSP: " + str(rsp.status_code) + ':' + rsp.text)
        if rsp.status_code != 200:
            raise IOError(rsp.reason)
        rsp_json = json.loads(rsp.text)
        return rsp
        

    def __init__(self, oid):
        """ Setup this object, given its low-level identifier """
        self._id = oid
        self.log = logging.getLogger("h5pyd")
        if not self.log.handlers:
            # setup logging
            self.log.setLevel(logging.INFO)
            fh = logging.FileHandler("h5pyd.log")
            self.log.addHandler(fh)
            
    
    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if hasattr(other, 'id'):
            return self.id == other.id
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __bool__(self):
        with phil:
            return bool(self.id)
    __nonzero__ = __bool__


# --- Dictionary-style interface ----------------------------------------------

# To implement the dictionary-style interface from groups and attributes,
# we inherit from the appropriate abstract base classes in collections.
#
# All locking is taken care of by the subclasses.
# We have to override ValuesView and ItemsView here because Group and
# AttributeManager can only test for key names.


class ValuesViewHDF5(ValuesView):

    """
        Wraps e.g. a Group or AttributeManager to provide a value view.
        
        Note that __contains__ will have poor performance as it has
        to scan all the links or attributes.
    """
    
    def __contains__(self, value):
        with phil:
            for key in self._mapping:
                if value == self._mapping.get(key):
                    return True
            return False

    def __iter__(self):
        with phil:
            for key in self._mapping:
                yield self._mapping.get(key)


class ItemsViewHDF5(ItemsView):

    """
        Wraps e.g. a Group or AttributeManager to provide an items view.
    """
        
    def __contains__(self, item):
        with phil:
            key, val = item
            if key in self._mapping:
                return val == self._mapping.get(key)
            return False

    def __iter__(self):
        with phil:
            for key in self._mapping:
                yield (key, self._mapping.get(key))


class MappingHDF5(Mapping):

    """
        Wraps a Group, AttributeManager or DimensionManager object to provide
        an immutable mapping interface.
        
        We don't inherit directly from MutableMapping because certain
        subclasses, for example DimensionManager, are read-only.
    """
    
    if six.PY3:
        def keys(self):
            """ Get a view object on member names """
            return KeysView(self)

        def values(self):
            """ Get a view object on member objects """
            return ValuesViewHDF5(self)

        def items(self):
            """ Get a view object on member items """
            return ItemsViewHDF5(self)

    else:
        def keys(self):
            """ Get a list containing member names """
            with phil:
                return list(self)

        def values(self):
            """ Get a list containing member objects """
            with phil:
                return [self.get(x) for x in self]

        def itervalues(self):
            """ Get an iterator over member objects """
            for x in self:
                yield self.get(x)

        def items(self):
            """ Get a list of tuples containing (name, object) pairs """
            with phil:
                return [(x, self.get(x)) for x in self]

        def iteritems(self):
            """ Get an iterator over (name, object) pairs """
            for x in self:
                yield (x, self.get(x))
                

class MutableMappingHDF5(MappingHDF5, MutableMapping):

    """
        Wraps a Group or AttributeManager object to provide a mutable
        mapping interface, in contrast to the read-only mapping of
        MappingHDF5.
    """

    pass
    

