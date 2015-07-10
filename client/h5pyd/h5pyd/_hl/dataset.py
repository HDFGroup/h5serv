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

import posixpath as pp
import sys

import six
from six.moves import xrange

import numpy
from h5py.h5t import check_dtype

#from . import base
from .base import HLObject
from .objectid import ObjectID, TypeID, DatasetID
#from . import filters
from . import selections as sel
#from . import selections2 as sel2
from .datatype import Datatype

from ..hdf5db import Hdf5db
from .. import hdf5dtype

_LEGACY_GZIP_COMPRESSION_VALS = frozenset(range(10))

def readtime_dtype(basetype, names):
    """ Make a NumPy dtype appropriate for reading """
    pass
    """
    if len(names) == 0:  # Not compound, or we want all fields
        return basetype

    if basetype.names is None:  # Names provided, but not compound
        raise ValueError("Field names only allowed for compound types")

    for name in names:  # Check all names are legal
        if not name in basetype.names:
            raise ValueError("Field %s does not appear in this type." % name)

    return numpy.dtype([(name, basetype.fields[name][0]) for name in names])
    """

def make_new_dset(parent, shape=None, dtype=None, data=None,
                 chunks=None, compression=None, shuffle=None,
                    fletcher32=None, maxshape=None, compression_opts=None,
                  fillvalue=None, scaleoffset=None, track_times=None):
    """ Return a new low-level dataset identifier

    Only creates anonymous datasets.
    """

     
    # Convert data to a C-contiguous ndarray
    if data is not None:
        from . import base
        data = numpy.asarray(data, order="C", dtype=base.guess_dtype(data))

    # Validate shape
    if shape is None:
        if data is None:
            raise TypeError("Either data or shape must be specified")
        shape = data.shape
    else:
        shape = tuple(shape)
        if data is not None and (numpy.product(shape) != numpy.product(data.shape)):
            raise ValueError("Shape tuple is incompatible with data")

    tmp_shape = maxshape if maxshape is not None else shape
    # Validate chunk shape
    if isinstance(chunks, tuple) and (-numpy.array([ i>=j for i,j in zip(tmp_shape,chunks) if i is not None])).any():
        errmsg = "Chunk shape must not be greater than data shape in any dimension. "\
                 "{} is not compatible with {}".format(chunks, shape)
        raise ValueError(errmsg)

    if isinstance(dtype, Datatype):
        # Named types are used as-is
        tid = dtype.id
        dtype = tid.dtype  # Following code needs this
    else:
        # Validate dtype
        if dtype is None and data is None:
            dtype = numpy.dtype("=f4")
        elif dtype is None and data is not None:
            dtype = data.dtype
        else:
            dtype = numpy.dtype(dtype)
        type_json = hdf5dtype.getTypeItem(dtype)
        #tid = h5t.py_create(dtype, logical=1)

    # Legacy
    if any((compression, shuffle, fletcher32, maxshape,scaleoffset)) and chunks is False:
        raise ValueError("Chunked format required for given storage options")

    # Legacy
    if compression is True:
        if compression_opts is None:
            compression_opts = 4
        compression = 'gzip'

    # Legacy
    if compression in _LEGACY_GZIP_COMPRESSION_VALS:
        if compression_opts is not None:
            raise TypeError("Conflict in compression options")
        compression_opts = compression
        compression = 'gzip'

    # todo
    #dcpl = filters.generate_dcpl(shape, dtype, chunks, compression, compression_opts,
    #              shuffle, fletcher32, maxshape, scaleoffset)
    dcpl = None
    if fillvalue is not None:
        fillvalue = numpy.array(fillvalue)
        #todo
        #dcpl.set_fill_value(fillvalue)
     
    """ 
    if track_times in (True, False):
        dcpl.set_obj_track_times(track_times)
    elif track_times is not None:
        raise TypeError("track_times must be either True or False")
    """ 
    if maxshape is not None:
        maxshape = tuple(m if m is not None else h5s.UNLIMITED for m in maxshape)
    #sid = h5s.create_simple(shape, maxshape)

    
    #dset_id = h5d.create(parent.id, None, tid, sid, dcpl=dcpl)
    req = "/datasets"
    shape_json = {'class': 'H5S_SIMPLE'}
    shape_json['dims'] = shape
    if maxshape is not None:
        shape_sjon['maxdims'] = maxshape
    body = {'type': type_json, 'shape': shape}
    if maxshape:
        body['maxshape'] = maxshape
    rsp = parent.POST(req, body=body)
    body['id'] = rsp['id']
    body['shape'] = shape_json
    dset_id = DatasetID(parent, body)

    if data is not None:
        pass
        # todo
        #dset_id.write(h5s.ALL, h5s.ALL, data)

    return dset_id
   
    

class AstypeContext(object):
    def __init__(self, dset, dtype):
        self._dset = dset
        self._dtype = numpy.dtype(dtype)

    def __enter__(self):
        self._dset._local.astype = self._dtype

    def __exit__(self, *args):
        self._dset._local.astype = None
  

class Dataset(HLObject):

    """
        Represents an HDF5 dataset
    """
        
    def astype(self, dtype):
        """ Get a context manager allowing you to perform reads to a
        different destination type, e.g.:

        >>> with dataset.astype('f8'):
        ...     double_precision = dataset[0:100:2]
        """
        pass
        #return AstypeContext(self, dtype)

    @property
    def dims(self):
        pass
        #from . dims import DimensionManager
        #return DimensionManager(self)

    @property
    def shape(self):
        """Numpy-style shape tuple giving dataset dimensions"""
        shape_json = self.id.shape_json
        if shape_json['class'] in ('H5S_NULL', 'H5S_SCALAR'):
            return ()  # return empty 
        
        if 'maxdims' not in shape_json:
            # not resizable, just return dims
            dims = shape_json['dims']
        else:
            # resizable, retrieve current shape        
            req = '/datasets/' + self.id.uuid + '/shape'
            rsp = self.GET(req)
            shape_json = rsp['shape']
            dims = shape_json['dims']
         
        return dims
        
    @shape.setter
    def shape(self, shape):
        self.resize(shape)

    @property
    def size(self):
        """Numpy-style attribute giving the total dataset size"""
        return numpy.prod(self.shape)

    @property
    def dtype(self):
        """Numpy dtype representing the datatype"""
        return self._dtype

    @property
    def value(self):
        """  Alias for dataset[()] """
        DeprecationWarning("dataset.value has been deprecated. "
            "Use dataset[()] instead.")
        return self[()]

    @property
    def chunks(self):
        """Dataset chunks (or None)"""
        """
        dcpl = self._dcpl
        if dcpl.get_layout() == h5d.CHUNKED:
            return dcpl.get_chunk()
        """
        return None

    @property
    def compression(self):
        """Compression strategy (or None)"""
        for x in ('gzip','lzf','szip'):
            if x in self._filters:
                return x
        return None

    @property
    def compression_opts(self):
        """ Compression setting.  Int(0-9) for gzip, 2-tuple for szip. """
        return self._filters.get(self.compression, None)

    @property
    def shuffle(self):
        """Shuffle filter present (T/F)"""
        return 'shuffle' in self._filters

    @property
    def fletcher32(self):
        """Fletcher32 filter is present (T/F)"""
        return 'fletcher32' in self._filters

    @property
    def scaleoffset(self):
        """Scale/offset filter settings. For integer data types, this is
        the number of bits stored, or 0 for auto-detected. For floating
        point data types, this is the number of decimal places retained.
        If the scale/offset filter is not in use, this is None."""
        try:
            return self._filters['scaleoffset'][1]
        except KeyError:
            return None

    @property
    def maxshape(self):
        """Shape up to which this dataset can be resized.  Axes with value
        None have no resize limit. """
        
        shape_json = self.id.shape_json
        if 'maxdims' not in shape_json:
            # not resizable, just return dims
            dims = shape_json['dims']
        else:
            dims = shape_json['maxdims']
            
        return tuple(x if x != 0 else None for x in dims)
        #dims = space.get_simple_extent_dims(True)
        #return tuple(x if x != h5s.UNLIMITED else None for x in dims)

    @property
    def fillvalue(self):
        """Fill value for this dataset (0 by default)"""
        arr = numpy.ndarray((1,), dtype=self.dtype)
        dcpl = self._dcpl.get_fill_value(arr)
        return arr[0]

    def __init__(self, bind):
        """ Create a new Dataset object by binding to a low-level DatasetID.
        """
        from threading import local

        if not isinstance(bind, DatasetID):
            raise ValueError("%s is not a DatasetID" % bind)
        HLObject.__init__(self, bind)

        self._dcpl = None  #self.id.get_create_plist()
        self._filters = [] # filters.get_filters(self._dcpl)
        self._local = None #local()
        # make a numpy dtype out of the type json
        self._dtype = hdf5dtype.createDataType(self.id.type_json)
        self._shape = self.id.shape_json['dims']
        # self._local.astype = None #todo

    def resize(self, size, axis=None):
        """ Resize the dataset, or the specified axis.

        The dataset must be stored in chunked format; it can be resized up to
        the "maximum shape" (keyword maxshape) specified at creation time.
        The rank of the dataset cannot be changed.

        "Size" should be a shape tuple, or if an axis is specified, an integer.

        BEWARE: This functions differently than the NumPy resize() method!
        The data is not "reshuffled" to fit in the new shape; each axis is
        grown or shrunk independently.  The coordinates of existing data are
        fixed.
        """
        with phil:
            if self.chunks is None:
                raise TypeError("Only chunked datasets can be resized")

            if axis is not None:
                if not (axis >=0 and axis < self.id.rank):
                    raise ValueError("Invalid axis (0 to %s allowed)" % (self.id.rank-1))
                try:
                    newlen = int(size)
                except TypeError:
                    raise TypeError("Argument must be a single int if axis is specified")
                size = list(self.shape)
                size[axis] = newlen

            size = tuple(size)
            self.id.set_extent(size)
            #h5f.flush(self.id)  # THG recommends

    def __len__(self):
        """ The size of the first axis.  TypeError if scalar.

        Limited to 2**32 on 32-bit systems; Dataset.len() is preferred.
        """
        size = self.len()
        if size > sys.maxsize:
            raise OverflowError("Value too big for Python's __len__; use Dataset.len() instead.")
        return size

    def len(self):
        """ The size of the first axis.  TypeError if scalar.

        Use of this method is preferred to len(dset), as Python's built-in
        len() cannot handle values greater then 2**32 on 32-bit systems.
        """
        with phil:
            shape = self.shape
            if len(shape) == 0:
                raise TypeError("Attempt to take len() of scalar dataset")
            return shape[0]

    def __iter__(self):
        """ Iterate over the first axis.  TypeError if scalar.

        BEWARE: Modifications to the yielded data are *NOT* written to file.
        """
        shape = self.shape
        if len(shape) == 0:
            raise TypeError("Can't iterate over a scalar dataset")
        for i in xrange(shape[0]):
            yield self[i]


    def __getitem__(self, args):
        """ Read a slice from the HDF5 dataset.

        Takes slices and recarray-style field names (more than one is
        allowed!) in any order.  Obeys basic NumPy rules, including
        broadcasting.

        Also supports:

        * Boolean "mask" array indexing
        """
         
        args = args if isinstance(args, tuple) else (args,)

        # Sort field indices from the rest of the args.
        names = tuple(x for x in args if isinstance(x, six.string_types))
        args = tuple(x for x in args if not isinstance(x, six.string_types))
        if not six.PY3:
            names = tuple(x.encode('utf-8') if isinstance(x, six.text_type) else x for x in names)

        def readtime_dtype(basetype, names):
            """ Make a NumPy dtype appropriate for reading """

            if len(names) == 0:  # Not compound, or we want all fields
                return basetype

            if basetype.names is None:  # Names provided, but not compound
                raise ValueError("Field names only allowed for compound types")

            for name in names:  # Check all names are legal
                if not name in basetype.names:
                    raise ValueError("Field %s does not appear in this type." % name)

            return numpy.dtype([(name, basetype.fields[name][0]) for name in names])

        new_dtype = getattr(self._local, 'astype', None)
        if new_dtype is not None:
            new_dtype = readtime_dtype(new_dtype, names)
        else:
            # This is necessary because in the case of array types, NumPy
            # discards the array information at the top level.
            new_dtype = readtime_dtype(self.dtype, names)
        # todo - will need the following once we have binary transfers
        # mtype = h5t.py_create(new_dtype)
        mtype = new_dtype

        # === Special-case region references ====
        """
        TODO
        if len(args) == 1 and isinstance(args[0], h5r.RegionReference):

            obj = h5r.dereference(args[0], self.id)
            if obj != self.id:
                raise ValueError("Region reference must point to this dataset")

            sid = h5r.get_region(args[0], self.id)
            mshape = sel.guess_shape(sid)
            if mshape is None:
                return numpy.array((0,), dtype=new_dtype)
            if numpy.product(mshape) == 0:
                return numpy.array(mshape, dtype=new_dtype)
            out = numpy.empty(mshape, dtype=new_dtype)
            sid_out = h5s.create_simple(mshape)
            sid_out.select_all()
            self.id.read(sid_out, sid, out, mtype)
            return out
        """

        # === Check for zero-sized datasets =====

        if numpy.product(self.shape) == 0:
            # These are the only access methods NumPy allows for such objects
            if args == (Ellipsis,) or args == tuple():
                return numpy.empty(self.shape, dtype=new_dtype)
            
        # === Scalar dataspaces =================

        if self.shape == ():
            fspace = self.id.get_space()
            selection = sel2.select_read(fspace, args)
            arr = numpy.ndarray(selection.mshape, dtype=new_dtype)
            for mspace, fspace in selection:
                self.id.read(mspace, fspace, arr, mtype)
            if len(names) == 1:
                arr = arr[names[0]]
            if selection.mshape is None:
                return arr[()]
            return arr

        # === Everything else ===================

        # Perform the dataspace selection
        #print "args:", args
        selection = sel.select(self.shape, args, dsid=self.id)
        #print "start:", selection.start
        #print "count:", selection.count
        rank = len(selection.start)

        if selection.nselect == 0:
            return numpy.ndarray(selection.mshape, dtype=new_dtype)

        # Up-converting to (1,) so that numpy.ndarray correctly creates
        # np.void rows in case of multi-field dtype. (issue 135)
        single_element = selection.mshape == ()
        mshape = (1,) if single_element else selection.mshape
        #arr = numpy.ndarray(mshape, new_dtype, order='C')

        # HDF5 has a bug where if the memory shape has a different rank
        # than the dataset, the read is very slow
        if len(mshape) < len(self.shape):
            # pad with ones
            mshape = (1,)*(len(self.shape)-len(mshape)) + mshape

        # Perfom the actual read
        req = "/datasets/" + self.id.uuid + "/value"
        sel_query = selection.getQueryParam()
        if sel_query:
            req += "?" + sel_query
        rsp = self.GET(req)
        #print "value:", rsp['value']
        #print "new_dtype:", new_dtype
        
        # need some special conversion for compound types --
        # each element must be a tuple, but the JSON decoder
        # gives us a list instead.
        data = rsp['value']
        if len(mtype) > 1 and type(data) in (list, tuple):
            converted_data = []
            for i in range(len(data)):
                converted_data.append(self.toTuple(data[i]))
            data = converted_data
            
        arr = numpy.empty(mshape, dtype=mtype)
        arr[...] = data
        
        """    
        if self.id.type_json['class'] == 'H5T_COMPOUND':
            arr = numpy.empty(mshape, dtype=new_dtype)
        else:
            arr = numpy.array(rsp['value'], dtype=new_dtype)
        """
        """
        #todo
        mspace = h5s.create_simple(mshape)
        fspace = selection._id
        self.id.read(mspace, fspace, arr, mtype)
        """

        # Patch up the output for NumPy
        if len(names) == 1:
            arr = arr[names[0]]     # Single-field recarray convention
        if arr.shape == ():
            arr = numpy.asscalar(arr)
        if single_element:
            arr = arr[0]
        return arr
        
    def read_where(self, condition, condvars=None, field=None, start=None, stop=None, step=None):
        """Read rows from compound type dataset using pytable-style condition
        """
        names = ()  # todo
        def readtime_dtype(basetype, names):
            """ Make a NumPy dtype appropriate for reading """

            if len(names) == 0:  # Not compound, or we want all fields
                return basetype

            if basetype.names is None:  # Names provided, but not compound
                raise ValueError("Field names only allowed for compound types")

            for name in names:  # Check all names are legal
                if not name in basetype.names:
                    raise ValueError("Field %s does not appear in this type." % name)

            return numpy.dtype([(name, basetype.fields[name][0]) for name in names])

        new_dtype = getattr(self._local, 'astype', None)
        if new_dtype is not None:
            new_dtype = readtime_dtype(new_dtype, names)
        else:
            # This is necessary because in the case of array types, NumPy
            # discards the array information at the top level.
            new_dtype = readtime_dtype(self.dtype, names)
        # todo - will need the following once we have binary transfers
        # mtype = h5t.py_create(new_dtype)
        if len(new_dtype) < 2:
            raise ValueError("Where method can only be used with compound datatypes")
        mtype = new_dtype

        # === Check for zero-sized datasets =====

        if numpy.product(self.shape) == 0 or self.shape == ():
            raise TypeError("Scalar datasets can not be used with where method")
        if len(self.shape) > 1:
            raise TypeError("Multi-dimensional datasets can not be used with where method")
             

        # === Everything else ===================

        # Perform the dataspace selection
        #print "args:", args
        if start or stop:
            if not start:
                start = 0
            if not stop:
                stop = self.shape[0] 
        else:
            start = 0
            stop = self.shape[0]
         
        selection_arg = slice(start, stop) 
        selection = sel.select(self.shape, selection_arg, dsid=self.id)
        #print "start:", selection.start
        #print "count:", selection.count
        rank = len(selection.start)

        if selection.nselect == 0:
            return numpy.ndarray(selection.mshape, dtype=new_dtype)

         
        # Perfom the actual read
        req = "/datasets/" + self.id.uuid + "/value"
        req += "?query=" + condition
        start_stop = selection.getQueryParam()
        if start_stop:
            req += "&" + start_stop
        
        rsp = self.GET(req)
        #print "value:", rsp['value']
        #print "new_dtype:", new_dtype
        
        # need some special conversion for compound types --
        # each element must be a tuple, but the JSON decoder
        # gives us a list instead.
        data = rsp['value']
        
        mshape = (len(data),)
        if len(mtype) > 1 and type(data) in (list, tuple):
            converted_data = []
            for i in range(len(data)):
                converted_data.append(self.toTuple(data[i]))
            data = converted_data
         
        arr = numpy.empty(mshape, dtype=mtype)
        arr[...] = data

        # Patch up the output for NumPy
        if len(names) == 1:
            arr = arr[names[0]]     # Single-field recarray convention
        if arr.shape == ():
            arr = numpy.asscalar(arr)
         
        return arr


    def __setitem__(self, args, val):
        """ Write to the HDF5 dataset from a Numpy array.

        NumPy's broadcasting rules are honored, for "simple" indexing
        (slices and integers).  For advanced indexing, the shapes must
        match.
        """
        
        args = args if isinstance(args, tuple) else (args,)

        # Sort field indices from the slicing
        names = tuple(x for x in args if isinstance(x, six.string_types))
        args = tuple(x for x in args if not isinstance(x, six.string_types))
        if not six.PY3:
            names = tuple(x.encode('utf-8') if isinstance(x, six.text_type) else x for x in names)

        # Generally we try to avoid converting the arrays on the Python
        # side.  However, for compound literals this is unavoidable.
       
        vlen = check_dtype(vlen=self.dtype)
        if vlen is not None and vlen not in (bytes, six.text_type):
            try:
                val = numpy.asarray(val, dtype=vlen)
            except ValueError:
                try:
                    val = numpy.array([numpy.array(x, dtype=vlen)
                                       for x in val], dtype=self.dtype)
                except ValueError:
                    pass
            if vlen == val.dtype:
                if val.ndim > 1:
                    tmp = numpy.empty(shape=val.shape[:-1], dtype=object)
                    tmp.ravel()[:] = [i for i in val.reshape(
                        (numpy.product(val.shape[:-1]), val.shape[-1]))]
                else:
                    tmp = numpy.array([None], dtype=object)
                    tmp[0] = val
                val = tmp
        elif self.dtype.kind == "O" or \
          (self.dtype.kind == 'V' and \
          (not isinstance(val, numpy.ndarray) or val.dtype.kind != 'V') and \
          (self.dtype.subdtype == None)):
            if len(names) == 1 and self.dtype.fields is not None:
                # Single field selected for write, from a non-array source
                if not names[0] in self.dtype.fields:
                    raise ValueError("No such field for indexing: %s" % names[0])
                dtype = self.dtype.fields[names[0]][0]
                cast_compound = True
            else:
                dtype = self.dtype
                cast_compound = False

            val = numpy.asarray(val, dtype=dtype, order='C')
            if cast_compound:
                val = val.astype(numpy.dtype([(names[0], dtype)]))
        else:
            val = numpy.asarray(val, order='C')

        # Check for array dtype compatibility and convert
        if self.dtype.subdtype is not None:
            shp = self.dtype.subdtype[1]
            valshp = val.shape[-len(shp):]
            if valshp != shp:  # Last dimension has to match
                raise TypeError("When writing to array types, last N dimensions have to match (got %s, but should be %s)" % (valshp, shp,))
            mtype = h5t.py_create(numpy.dtype((val.dtype, shp)))
            mshape = val.shape[0:len(val.shape)-len(shp)]

        # Make a compound memory type if field-name slicing is required
        elif len(names) != 0:

            mshape = val.shape

            # Catch common errors
            if self.dtype.fields is None:
                raise TypeError("Illegal slicing argument (not a compound dataset)")
            mismatch = [x for x in names if x not in self.dtype.fields]
            if len(mismatch) != 0:
                mismatch = ", ".join('"%s"'%x for x in mismatch)
                raise ValueError("Illegal slicing argument (fields %s not in dataset type)" % mismatch)
        
            # Write non-compound source into a single dataset field
            if len(names) == 1 and val.dtype.fields is None:
                subtype = h5y.py_create(val.dtype)
                mtype = h5t.create(h5t.COMPOUND, subtype.get_size())
                mtype.insert(self._e(names[0]), 0, subtype)

            # Make a new source type keeping only the requested fields
            else:
                fieldnames = [x for x in val.dtype.names if x in names] # Keep source order
                mtype = h5t.create(h5t.COMPOUND, val.dtype.itemsize)
                for fieldname in fieldnames:
                    subtype = h5t.py_create(val.dtype.fields[fieldname][0])
                    offset = val.dtype.fields[fieldname][1]
                    mtype.insert(self._e(fieldname), offset, subtype)

        # Use mtype derived from array (let DatasetID.write figure it out)
        else:
            mshape = val.shape
            mtype = None

        # Perform the dataspace selection
        selection = sel.select(self.shape, args, dsid=self.id)

        if selection.nselect == 0:
            return

        # Broadcast scalars if necessary.
        if (mshape == () and selection.mshape != ()):
            if self.dtype.subdtype is not None:
                raise TypeError("Scalar broadcasting is not supported for array dtypes")
            val2 = numpy.empty(selection.mshape[-1], dtype=val.dtype)
            val2[...] = val
            val = val2
            mshape = val.shape

        # Perform the write, with broadcasting
        # Be careful to pad memory shape with ones to avoid HDF5 chunking
        # glitch, which kicks in for mismatched memory/file selections
        if(len(mshape) < len(self.shape)):
            mshape_pad = (1,)*(len(self.shape)-len(mshape)) + mshape
        else:
            mshape_pad = mshape
        req = "/datasets/" + self.id.uuid + "/value"
        
        body = {}
        if selection.start:
            body['start'] = list(selection.start)
            stop = list(selection.start)
            for i in range(len(stop)):
                stop[i] += selection.count[i]
            body['stop'] = stop
            if selection.step:
                body['step'] = list(selection.step)
        
            
        body['value'] = val.tolist()
        self.PUT(req, body=body)
        """
        mspace = h5s.create_simple(mshape_pad, (h5s.UNLIMITED,)*len(mshape_pad))
        for fspace in selection.broadcast(mshape):
            self.id.write(mspace, fspace, val, mtype)
        """
        

    def read_direct(self, dest, source_sel=None, dest_sel=None):
        """ Read data directly from HDF5 into an existing NumPy array.

        The destination array must be C-contiguous and writable.
        Selections must be the output of numpy.s_[<args>].

        Broadcasting is supported for simple indexing.
        """
        
        """
        #todo
        with phil:
            if source_sel is None:
                source_sel = sel.SimpleSelection(self.shape)
            else:
                source_sel = sel.select(self.shape, source_sel, self.id)  # for numpy.s_
            fspace = source_sel._id

            if dest_sel is None:
                dest_sel = sel.SimpleSelection(dest.shape)
            else:
                dest_sel = sel.select(dest.shape, dest_sel, self.id)

            for mspace in dest_sel.broadcast(source_sel.mshape):
                self.id.read(mspace, fspace, dest)
        """

    def write_direct(self, source, source_sel=None, dest_sel=None):
        """ Write data directly to HDF5 from a NumPy array.

        The source array must be C-contiguous.  Selections must be
        the output of numpy.s_[<args>].

        Broadcasting is supported for simple indexing.
        """
        
        """
        #todo
        with phil:
            if source_sel is None:
                source_sel = sel.SimpleSelection(source.shape)
            else:
                source_sel = sel.select(source.shape, source_sel, self.id)  # for numpy.s_
            mspace = source_sel._id

            if dest_sel is None:
                dest_sel = sel.SimpleSelection(self.shape)
            else:
                dest_sel = sel.select(self.shape, dest_sel, self.id)

            for fspace in dest_sel.broadcast(source_sel.mshape):
                self.id.write(mspace, fspace, source)
        """

    def __array__(self, dtype=None):
        """ Create a Numpy array containing the whole dataset.  DON'T THINK
        THIS MEANS DATASETS ARE INTERCHANGABLE WITH ARRAYS.  For one thing,
        you have to read the whole dataset everytime this method is called.
        """
        arr = numpy.empty(self.shape, dtype=self.dtype if dtype is None else dtype)

        # Special case for (0,)*-shape datasets
        if numpy.product(self.shape) == 0:
            return arr

        # todo
        #self.read_direct(arr)
        return arr

    def __repr__(self):
        if not self:
            r = six.u('<Closed HDF5 dataset>')
        else:
            if self.name is None:
                namestr = six.u('("anonymous")')
            else:
                name = pp.basename(pp.normpath(self.name))
                namestr = six.u('"%s"') % (
                    name if name != six.u('') else six.u('/'))
            r = six.u('<HDF5 dataset %s: shape %s, type "%s">') % \
                (namestr, self.shape, self.dtype.str)
        if six.PY3:
            return r
        return r.encode('utf8')
       
    def refresh(self):
        """ Refresh the dataset metadata by reloading from the file.
            
        This is part of the SWMR features and only exist when the HDF5
        librarary version >=1.9.178
        """
        pass # todo
                
    def flush(self):
       """ Flush the dataset data and metadata to the file.
       If the dataset is chunked, raw data chunks are written to the file.
            
       This is part of the SWMR features and only exist when the HDF5 
       librarary version >=1.9.178
       """
       pass # todo
            
            
    """
      Convert a list to a tuple, recursively.
      Example. [[1,2],[3,4]] -> ((1,2),(3,4))
    """
    def toTuple(self, data):
        if type(data) in (list, tuple):
            return tuple(self.toTuple(x) for x in data)
        else:
            return data

