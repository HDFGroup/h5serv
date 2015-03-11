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
This class is used to manage UUID lookup tables for primary HDF objects (Groups, Datasets,
 and Datatypes).  For HDF5 files that are read/write, this information is managed within 
 the file itself in the "__db__" group.  For read-only files, the data is managed in 
 an external file (domain filename with ".db" extension).
 
 "___db__"  ("root" for read-only case) 
    description: Group object (member of root group). Only objects below this group are used 
            for UUID data
    members: "{groups}", "{datasets}", "{datatypes}", "{objects}", "{paths}"
    attrs: 'rootUUID': UUID of the root group
    
"{groups}"  
    description: contains map of UUID->group objects  
    members: hard link to each anonymous group (i.e. groups which are not
        linked to by anywhere else).  Link name is the UUID
    attrs: group reference (or path for read-only files) to the group (for non-
        anonymous groups).
    
"{datasets}"  
    description: contains map of UUID->dataset objects  
    members: hard link to each anonymous dataset (i.e. datasets which are not
        linked to by anywhere else).  Link name is the UUID
    attrs: dataset reference (or path for read-only files) to the group (for non-
        anonymous datasets).
    
"{datatypes}"  
    description: contains map of UUID->datatyped objects
    members: hard link to each anonymous datatype (i.e. datatypes which are not
        linked to by anywhere else).  Link name is the UUID
    attrs: datatype reference (or path for read-only files) to the datatype (for non-
        anonymous datatypes).

"{addr}"
    description: contains map of file offset to UUID.
    members: none
    attrs: map of file offset to UUID
        
    
    
 
"""
import errno
import time
import h5py
import numpy as np
import uuid
import os.path as op
import os
import logging

import hdf5dtype


# global dictionary to direct back to the Hdf5db instance by filename
# (needed for visititems callback)
# Will break in multi-threaded context
_db = { }

UUID_LEN = 36  # length for uuid strings

def visitObj(path, obj):   
    hdf5db = _db[obj.file.filename]
    hdf5db.visit(path, obj)
    
    
class Hdf5db:
        
    @staticmethod
    def createHDF5File(filePath):
        # create an "empty" hdf5 file
        if op.isfile(filePath):
            raise IOError(errno.EEXIST, "Resource already exists")
        
        f = h5py.File(filePath, 'w')
        f.close()
            
           
        
    def __init__(self, filePath, dbFilePath=None, readonly=False, app_logger=None, root_uuid=None):
        if app_logger:
            self.log = app_logger
        else:
            self.log = logging.getLogger()
        mode = 'r'
        if readonly:
            self.readonly = True
        else:
            if os.access(filePath, os.W_OK):         
                mode = 'r+'
                self.readonly = False
            else:
                self.readonly = True
        self.log.info("init -- filePath: " + filePath + " mode: " + mode)
        
        self.f = h5py.File(filePath, mode)
        
        self.root_uuid=root_uuid
        
        if self.readonly:     
            # for read-only files, add a dot in front of the name to be used as the 
            # db file.  This won't collide with actual data files, since "." is not 
            # allowed as the first character in a domain name.
            if not dbFilePath:
                dirname = op.dirname(self.f.filename)
                basename = op.basename(self.f.filename)
                if len(dirname) > 0: 
                    dbFilePath = dirname + '/.' + basename
                else:
                    dbFilePath = '.' + basename
            dbMode = 'r+'
            if not op.isfile(dbFilePath):
                dbMode = 'w'
            self.log.info("dbFilePath: " + dbFilePath + " mode: " + dbMode)
            self.dbf = h5py.File(dbFilePath, dbMode)
        else:
            self.dbf = None # for read only
        # create a global reference to this class
        # so visitObj can call back
        _db[filePath] = self 
        
    
    def __enter__(self):
        self.log.info('Hdf5db __enter')
        return self

    def __exit__(self, type, value, traceback):
        self.log.info('Hdf5db __exit')
        filename = self.f.filename
        self.f.flush()
        self.f.close()
        if self.dbf:
            self.dbf.flush()
            self.dbf.close()
        del _db[filename]
        
        
    def getTimeStampName(self, uuid, objType="object", name=None):
        ts_name = uuid
        if objType != "object":
            if len(name) == 0:
                self.log.error("empty name passed to setCreateTime")
                raise Exception("bad setCreateTimeParameter")
            if objType == "attribute":
                ts_name += "_attr:["
                ts_name += name
                ts_name += "]"
            elif objType == "link":
                ts_name += "_link:["
                ts_name += name
                ts_name += "]"
            else:   
                msg = "Bad objType passed to setCreateTime"
                self.log.error(msg)
                raise IOError(errno.EIO, msg)
        return ts_name
        
     
    """
      setCreateTime - sets the create time timestamp for the
            given object.
        uuid - id of object
        objtype - one of "object", "link", "attribute"
        name - name (for attributes, links... ignored for objects)   
        timestamp - time (otherwise current time will be used)
       
       returns - nothing 
       
       Note - should only be called once per object
    """    
    def setCreateTime(self, uuid, objType="object", name=None, timestamp=None):
        ctime_grp = self.dbGrp["{ctime}"]
        ts_name = self.getTimeStampName(uuid, objType, name) 
        if timestamp == None:
            timestamp = time.time()
        if ts_name in ctime_grp.attrs:
            self.log.warn("modifying create time for object: " + ts_name)
        ctime_grp.attrs.create(ts_name, timestamp, dtype='int64')
    
    """
      getCreateTime - gets the create time timestamp for the
            given object.
        uuid - id of object
        objtype - one of "object", "link", "attribute"
        name - name (for attributes, links... ignored for objects) 
        useRoot - if true, use the time value for root object as default  
       
       returns - create time for object, or create time for root if not set 
    """    
    def getCreateTime(self, uuid, objType="object", name=None, useRoot=True):
        ctime_grp = self.dbGrp["{ctime}"]
        ts_name = self.getTimeStampName(uuid, objType, name) 
        timestamp = None
        if ts_name in ctime_grp.attrs:
            timestamp = ctime_grp.attrs[ts_name]
        elif useRoot:
            # return root timestamp
            root_uuid = self.dbGrp.attrs["rootUUID"] 
            timestamp = ctime_grp.attrs[root_uuid]
        return timestamp
     
    """
      setModifiedTime - sets the modified time timestamp for the
            given object.
        uuid - id of object
        objtype - one of "object", "link", "attribute"
        name - name (for attributes, links... ignored for objects)   
        timestamp - time (otherwise current time will be used)
       
       returns - nothing 
       
    """         
    def setModifiedTime(self, uuid, objType="object", name=None, timestamp=None):
        mtime_grp = self.dbGrp["{mtime}"]
        ts_name = self.getTimeStampName(uuid, objType, name) 
        if timestamp == None:
            timestamp = time.time()
        mtime_grp.attrs.create(ts_name, timestamp, dtype='int64')
     
    """
      getModifiedTime - gets the modified time timestamp for the
            given object.
        uuid - id of object
        objtype - one of "object", "link", "attribute"
        name - name (for attributes, links... ignored for objects) 
        useRoot - if true, use the time value for root object as default   
       
       returns - create time for object, or create time for root if not set 
    """     
    def getModifiedTime(self, uuid, objType="object", name=None, useRoot=True):
        mtime_grp = self.dbGrp["{mtime}"]
        ts_name = self.getTimeStampName(uuid, objType, name) 
        timestamp = None
        if ts_name in mtime_grp.attrs:
            timestamp = mtime_grp.attrs[ts_name]
        else:
            # return create time if no modified time has been set
            ctime_grp = self.dbGrp["{ctime}"]
            if ts_name in ctime_grp.attrs:
                timestamp = ctime_grp.attrs[ts_name]
            elif useRoot:
                # return root timestamp
                root_uuid = self.dbGrp.attrs["rootUUID"] 
                timestamp = mtime_grp.attrs[root_uuid]
        return timestamp
        
    def initFile(self):
        # self.log.info("initFile")
        if self.readonly:
            self.dbGrp = self.dbf
            if "{groups}" in self.dbf:
                # file already initialized
                self.root_uuid = self.dbGrp.attrs["rootUUID"]
                return
            
        else:
            if "__db__" in self.f:
                # file already initialized
                self.dbGrp = self.f["__db__"]
                self.root_uuid = self.dbGrp.attrs["rootUUID"]
                return;  # already initialized 
            self.dbGrp = self.f.create_group("__db__")
           
        self.log.info("initializing file") 
        if not self.root_uuid:
            self.root_uuid = str(uuid.uuid1())
        self.dbGrp.attrs["rootUUID"] = self.root_uuid
        self.dbGrp.create_group("{groups}")
        self.dbGrp.create_group("{datasets}")
        self.dbGrp.create_group("{datatypes}")
        self.dbGrp.create_group("{addr}") # store object address
        self.dbGrp.create_group("{ctime}") # stores create timestamps
        self.dbGrp.create_group("{mtime}") # store modified timestamps
        
        mtime = op.getmtime(self.f.filename)
        ctime = mtime
        self.setCreateTime(self.root_uuid, timestamp=ctime)
        self.setModifiedTime(self.root_uuid, timestamp=mtime)
            
        self.f.visititems(visitObj)
        
    def visit(self, path, obj):
        name = obj.__class__.__name__
        if len(path) >= 6 and path[:6] == '__db__':
            return  # don't include the db objects
        self.log.info('visit: ' + path +' name: ' + name)
        col = None 
        if name == 'Group':
            col = self.dbGrp["{groups}"].attrs
        elif name == 'Dataset':
            col = self.dbGrp["{datasets}"].attrs
        elif name == 'Datatype':
            col = self.dbGrp["{datatypes}"].attrs
        else:
            msg = "Unknown object type: " + __name__ + " found during scan of HDF5 file"
            self.log.error(msg)
            raise IOError(errno.EIO, msg)
        uuid1 = uuid.uuid1()  # create uuid
        id = str(uuid1)
        addrGrp = self.dbGrp["{addr}"]
        if not self.readonly:
            # storing db in the file itself, so we can link to the object directly
            col[id] = obj.ref  # save attribute ref to object
        else:
            #store path to object
            col[id] = obj.name
        addr = h5py.h5o.get_info(obj.id).addr
        # store reverse map as an attribute
        addrGrp.attrs[str(addr)] = id       
        
    def getUUIDByAddress(self, addr):
        if "{addr}" not in self.dbGrp:
            self.log.error("expected to find {addr} group") 
            return None
        addrGrp = self.dbGrp["{addr}"]
        obj_uuid = None
        if str(addr) in addrGrp.attrs:
            obj_uuid = addrGrp.attrs[str(addr)] 
        return obj_uuid
    
        
    """
     Get the number of links in a group to an object
    """
    def getNumLinksToObjectInGroup(self, grp, obj):
        objAddr = h5py.h5o.get_info(obj.id).addr
        numLinks = 0
        for name in grp:
            try:
                child = grp[name]
            except KeyError:
                # UDLink? Ignore for now
                self.log.info("ignoring link (UDLink?): " + name)
                continue
                
            addr = h5py.h5o.get_info(child.id).addr
            if addr == objAddr:
                numLinks = numLinks + 1
            
        return numLinks  
            
    """
     Get the number of links to the given object
    """
    def getNumLinksToObject(self, obj):
        self.initFile()
        groups = self.dbGrp["{groups}"]
        numLinks = 0
        # iterate through each group in the file and unlink tgt if it is linked
        # by the group
        for uuidName in groups:
            # iterate through anonymous groups
            grp = groups[uuidName]
            nLinks = self.getNumLinksToObjectInGroup(grp, obj)
            if nLinks > 0:
                numLinks += nLinks
        for uuidName in groups.attrs:
            # now non anonymous groups
            grpRef = groups.attrs[uuidName]
            grp = self.f[grpRef]  # dereference
            nLinks = self.getNumLinksToObjectInGroup(grp, obj)
            if nLinks > 0:
                numLinks += nLinks
        # finally, check the root group
        root = self.getObjByPath("/")
        nLinks = self.getNumLinksToObjectInGroup(root, obj)
        numLinks += nLinks
            
        return numLinks   
        
    def getUUIDByPath(self, path):
        self.initFile()
        self.log.info("getUUIDByPath: [" + path + "]")
        if len(path) >= 6 and path[:6] == '__db__':
            msg = "getUUIDByPath called with invalid path: [" + path + "]"
            self.log.error(msg)
            raise IOError(errno.EIO, msg)
        if path == '/':
            # just return the root UUID
            return self.dbGrp.attrs["rootUUID"]
            
        obj = self.f[path]  # will throw KeyError if object doesn't exist
        addr = h5py.h5o.get_info(obj.id).addr
        obj_uuid = self.getUUIDByAddress(addr)
        return obj_uuid
                     
    def getObjByPath(self, path):
        if len(path) >= 6 and path[:6] == '__db__':
            return None # don't include the db objects
        obj = self.f[path]  # will throw KeyError if object doesn't exist
        return obj
        
    
    def getObjectByUuid(self, col_type, obj_uuid):
        #col_type should be either "datasets", "groups", or "datatypes"
        if col_type not in ("datasets", "groups", "datatypes"):
            msg = "Unexpectd error, invalid col_type: [" + col_type + "]"
            self.log.error(msg)
            raise IOError(errno.EIO, msg)
        if col_type == "groups" and obj_uuid == self.dbGrp.attrs["rootUUID"]:
            return self.f['/']  # returns root group
            
        obj = None  # Group, Dataset, or Datatype
        col_name = '{' + col_type + '}'
        # get the collection group for this collection type
        col = self.dbGrp[col_name]
        if obj_uuid in col.attrs:
            ref = col.attrs[obj_uuid]
            obj = self.f[ref]  # this works for read-only as well
        elif obj_uuid in col: 
            # anonymous object
            obj = col[obj_uuid]
                
        return obj
        
    def getDatasetObjByUuid(self, obj_uuid):
        self.initFile()
        self.log.info("getDatasetObjByUuid(" + obj_uuid + ")")
        
        obj = self.getObjectByUuid("datasets", obj_uuid)
                                 
        return obj
        
    def getGroupObjByUuid(self, obj_uuid):
        self.initFile()
        self.log.info("getGroupObjByUuid(" + obj_uuid + ")")
        
        obj = self.getObjectByUuid("groups", obj_uuid)
         
        return obj
    
    def getDatasetTypeItemByUuid(self, obj_uuid):
        dset = self.getDatasetObjByUuid(obj_uuid)  # throws exception if not found
        item = { 'id': obj_uuid }
        item['type'] = hdf5dtype.getTypeItem(dset.dtype)
        item['ctime'] = self.getCreateTime(obj_uuid)
        item['mtime'] = self.getModifiedTime(obj_uuid)      
        
        return item    

    """
    getNullReference - return a null object reference
    """
    def getNullReference(self):
         tmpGrp = None
         if "{tmp}" not in self.dbGrp:
             tmpGrp = self.dbGrp.create_group("{tmp}")
         else:
             tmpGrp = self.dbGrp["{tmp}"]
         if 'nullref' not in tmpGrp:
             dt = h5py.special_dtype(ref=h5py.Reference)
             tmpGrp.create_dataset('nullref', (1,), dtype=dt)
         nullref_dset = tmpGrp['nullref']
         return nullref_dset[0]
        
    def getShapeItemByDsetObj(self, obj):
        item = {}
        if len(obj.shape) == 0:
            # check to see if this is a null space vs a scalar dataset
            # we'll do this by seeing if an exception is raised when reading the dataset
            # h5py issue https://github.com/h5py/h5py/issues/279 will provide a better
            # way to determine null spaces
            try: 
                val = obj[...]
                if not val:
                    self.log.warning("no value returned for scalar dataset")
                item['class'] = 'H5S_SCALAR'
            except IOError:
                item['class'] = 'H5S_NULL'
        else:
            item['class'] = 'H5S_SIMPLE'
            item['dims'] = obj.shape
            maxshape = []
            include_maxdims = False
            for i in range(len(obj.shape)):
                extent = 0
                if len(obj.maxshape) > i:
                    extent = obj.maxshape[i]
                    if extent == None:
                        extent = 0
                    if extent > obj.shape[i] or extent == 0:
                        include_maxdims = True
                maxshape.append(extent)
            if include_maxdims:
                item['maxdims'] = maxshape
        return item
        
    def getShapeItemByAttrObj(self, obj):
        item = {}
        if obj.get_storage_size() == 0:
            # If storage size is 0, assume this is a null space obj
            # See: h5py issue https://github.com/h5py/h5py/issues/279  
            item['class'] = 'H5S_NULL'
        else:
            if obj.shape:
                item['class'] = 'H5S_SIMPLE'
                item['dims'] = obj.shape
            else:
                item['class'] = 'H5S_SCALAR'
        return item
        
    def getDatasetItemByUuid(self, obj_uuid):
        dset = self.getDatasetObjByUuid(obj_uuid)  
        if dset is None:
            if self.getModifiedTime(obj_uuid, useRoot=False):
                msg = "Dataset with uuid: " + obj_uuid + " has been previously deleted"
                self.log.info(msg)
                raise IOError(errno.ENOENT, msg)
            else:
                msg = "Dataset with uuid: " + obj_uuid + " was not found"
                self.log.info(msg)
                raise IOError(errno.ENXIO, msg)
        
        #file in the item info for the dataset
        item = { 'id': obj_uuid }
        
        alias = []
        if dset.name:
            alias.append(dset.name)   # just use the default h5py path for now
        item['alias'] = alias
        
        item['attributeCount'] = len(dset.attrs)
        
        # check if the dataset is using a committed type
        typeid = h5py.h5d.DatasetID.get_type(dset.id)
        typeItem = None
        if h5py.h5t.TypeID.committed(typeid):
            type_uuid = None
            addr = h5py.h5o.get_info(typeid).addr
            type_uuid = self.getUUIDByAddress(addr)
            committedType = self.getCommittedTypeItemByUuid(type_uuid)
            typeItem = committedType['type']
            typeItem['uuid'] = type_uuid
        else:  
            typeItem = hdf5dtype.getTypeItem(dset.dtype)
            
        item['type'] = typeItem
            
        # get shape
        item['shape'] = self.getShapeItemByDsetObj(dset)
         
        #todo - get fillvalue for committed type objects
        if typeItem and typeItem['class'] != 'H5T_VLEN' and typeItem['class'] != 'H5T_OPAQUE':
            try:
                fillvalue = dset.fillvalue
                if fillvalue is not None:
                    item['fillvalue'] = fillvalue.tolist()
            except RuntimeError:
                # exception is thrown if fill value is not set
                pass   # nop
            
        item['ctime'] = self.getCreateTime(obj_uuid)
        item['mtime'] = self.getModifiedTime(obj_uuid)      
        
        return item
        
    """ 
    createTypeFromItem - create type given dictionary definition
    """
    def createTypeFromItem(self, typeItem):
        dt = None
        try:
            dt = hdf5dtype.createDataType(typeItem)
        except KeyError as ke:
            msg = "Unable able to create type: " + ke.message
            self.log.info(msg)
            raise IOError(errno.EINVAL, msg)
        except TypeError as te:
            msg = "Unable able to create type: " + te.message
            self.log.info(msg)
            raise IOError(errno.EINVAL, msg)      
        if dt is None:
            msg = "Unexpected error creating type"
            self.log.error(msg)
            raise IOError(errno, errno.EIO, msg)
        return dt
        
    """
    createCommittedType - creates new named datatype  
    Returns item
    """   
    def createCommittedType(self, datatype, obj_uuid=None):
        self.log.info("createCommittedType")
        self.initFile()
        if self.readonly:
            msg = "Can't create committed type (updates are not allowed)"
            self.log.info(msg)
            raise IOError(errno.EPERM, msg)
        datatypes = self.dbGrp["{datatypes}"]
        if not obj_uuid:
            obj_uuid = str(uuid.uuid1())
        dt = self.createTypeFromItem(datatype)
        
        datatypes[obj_uuid] = np.dtype(dt)  # dt
        
        if obj_uuid not in datatypes:
            msg = "Unexpected failure to create committed datatype"
            self.log.error(msg)
            raise IOError(errno.EIO, msg)
        newType = datatypes[obj_uuid] # this will be a h5py Datatype class 
        # store reverse map as an attribute
        addr = h5py.h5o.get_info(newType.id).addr
        addrGrp = self.dbGrp["{addr}"]
        addrGrp.attrs[str(addr)] = obj_uuid
        # set timestamp
        now = time.time()
        self.setCreateTime(obj_uuid, timestamp=now)
        self.setModifiedTime(obj_uuid, timestamp=now)
        item = { 'id': obj_uuid }
        item['attributeCount'] = len(newType.attrs)
        #item['type'] = hdf5dtype.getTypeItem(datatype.dtype) 
        item['ctime'] = self.getCreateTime(obj_uuid)
        item['mtime'] = self.getModifiedTime(obj_uuid) 
        return item
      
    """
    getCommittedTypeObjByUuid - get obj from {datatypes} collection 
    Returns type obj
    """   
    def getCommittedTypeObjByUuid(self, obj_uuid):
        self.log.info("getCommittedTypeObjByUuid(" + obj_uuid + ")")
        self.initFile()
        datatype = None
        datatypesGrp = self.dbGrp["{datatypes}"]
        if obj_uuid in datatypesGrp.attrs:
            typeRef = datatypesGrp.attrs[obj_uuid]
            # typeRef could be a reference or (for read-only) a path
            datatype = self.f[typeRef]
        elif obj_uuid in datatypesGrp:
            datatype = datatypesGrp[obj_uuid]  # non-linked type
        else:
            msg = "Committed datatype: " + obj_uuid + " not found"
            self.log.info(msg)
     
        return datatype
        
    """
    getCommittedTypeItemByUuid - get json from {datatypes} collection 
    Returns type obj
    """   
    def getCommittedTypeItemByUuid(self, obj_uuid):
        self.log.info("getCommittedTypeItemByUuid(" + obj_uuid + ")")
        self.initFile()
        datatype = self.getCommittedTypeObjByUuid(obj_uuid)
        
        if datatype == None:
            if self.getModifiedTime(obj_uuid, useRoot=False):
                msg = "Datatype with uuid: " + obj_uuid + " has been previously deleted"
                self.log.info(msg)
                raise IOError(errno.ENOENT, msg)
            else:
                msg = "Datatype with uuid: " + obj_uuid + " was not found"
                self.log.info(msg)
                raise IOError(errno.ENXIO, msg)
         
        item = { 'id': obj_uuid }
        alias = []
        if datatype.name:
            alias.append(datatype.name)   # just use the default h5py path for now
        item['alias'] = alias
        item['attributeCount'] = len(datatype.attrs)
        item['type'] = hdf5dtype.getTypeItem(datatype.dtype) 
        item['ctime'] = self.getCreateTime(obj_uuid)
        item['mtime'] = self.getModifiedTime(obj_uuid) 
        
        return item
       
    """
      Get attribute given an object and name
      returns: JSON object 
    """ 
    def getAttributeItemByObj(self, obj, name, includeData=True):
        if name not in obj.attrs:
            msg = "Attribute: [" + name + "] not found in object: " + obj.name
            self.log.info(msg)
            return None
            
        # get the attribute!
        attrObj = h5py.h5a.open(obj.id, name)
        attr = None
                   
        item = { 'name': name }
         
        # check if the dataset is using a committed type
        typeid = attrObj.get_type()
        typeItem = None
        if h5py.h5t.TypeID.committed(typeid):
            type_uuid = None
            addr = h5py.h5o.get_info(typeid).addr
            type_uuid = self.getUUIDByAddress(addr)
            committedType = self.getCommittedTypeItemByUuid(type_uuid)
            typeItem = committedType['type']
            typeItem['uuid'] = type_uuid
        else:  
            typeItem = hdf5dtype.getTypeItem(attrObj.dtype)
        item['type'] = typeItem
        # todo - don't include data for OPAQUE until JSON serialization 
        # issues are addressed
        
        if type(typeItem) == dict and typeItem['class'] in ('H5T_OPAQUE'):
            includeData = False
         
        shape_json = self.getShapeItemByAttrObj(attrObj)
        item['shape'] = shape_json
        if shape_json['class'] == 'H5S_NULL':
            includeData = False
        if includeData:
            try:
                attr = obj.attrs[name]  # returns a numpy array
            except TypeError:
                self.log.warning("type error reading attribute") 
        
        if includeData and attr is not None:
            if typeItem['class'] == 'H5T_VLEN':
                item['value'] = self.vlenToList(attr)
            elif typeItem['class'] == 'H5T_REFERENCE':
                item['value'] = self.refToList(attr)
            elif typeItem['class'] == 'H5T_COMPOUND':
                item['value'] = attr.tolist()  # convert to list
            elif len(attrObj.shape) == 0 and type(attr) in (str, unicode, int, float):
                item['value'] = attr   # just copy value
            else:
                item['value'] = attr.tolist()  # convert to list
        # timestamps will be added by getAttributeItem()
        return item
            
    def getAttributeItems(self, col_type, obj_uuid, marker=None, limit=0):
        self.log.info("db.getAttributeItems(" + obj_uuid + ")")
        if marker:
            self.log.info("...marker: " + marker)
        if limit:
            self.log.info("...limit: " + str(limit))
        
        self.initFile()
        obj = self.getObjectByUuid(col_type, obj_uuid)
        if obj == None:
            msg = "Object: " + obj_uuid + " could not be loaded"
            self.log.info(msg)
            raise IOError(errno.ENXIO, msg)
            
        items = []
        gotMarker = True
        if marker != None:
            gotMarker = False
        count = 0
        for name in obj.attrs:
            if not gotMarker:
                if name == marker:
                    gotMarker = True
                    continue  # start filling in result on next pass
                else:
                    continue  # keep going!
            item = self.getAttributeItemByObj(obj, name, False)
            # mix-in timestamps
            item['ctime'] = self.getCreateTime(obj_uuid, objType="attribute", name=name)
            item['mtime'] = self.getModifiedTime(obj_uuid, objType="attribute", name=name)
                           
            items.append(item)
            count += 1
            if limit > 0 and count == limit:
                break  # return what we got
        return items
            
    def getAttributeItem(self, col_type, obj_uuid, name):
        self.log.info("getAttributeItemByUuid(" + col_type + ", " + obj_uuid + ", " + 
            name + ")")
        self.initFile()
        obj = self.getObjectByUuid(col_type, obj_uuid)
        if obj == None:
            msg = "Parent object: " + obj_uuid + " of attribute not found"
            self.log.info(msg)
            raise IOError(errno.ENXIO, msg)
            return None
        item = self.getAttributeItemByObj(obj, name)
        if item == None:
            if self.getModifiedTime(obj_uuid, objType="attribute", name=name, useRoot=False):
                # attribute has been removed
                msg = "Attribute: [" + name + "] of object: " + obj_uuid + " has been previously deleted"
                self.log(msg)
                raise IOError(errno.ENOINT, msg)
            msg = "Attribute: [" + name + "] of object: " + obj_uuid + " not found"
            self.log.info(msg)
            raise IOError(errno.ENXIO, msg)
        # mix-in timestamps
        item['ctime'] = self.getCreateTime(obj_uuid, objType="attribute", name=name)
        item['mtime'] = self.getModifiedTime(obj_uuid, objType="attribute", name=name)
            
        return item
        
    def createAttribute(self, col_name, obj_uuid, attr_name, shape, attr_type, value):
        self.log.info("createAttribute: [" + attr_name + "]")
        self.initFile()
        if self.readonly:
            msg = "Unable to create attribute (updates are not allowed)"
            self.log.info(msg)
            raise IOError(errno.EPERM, msg)
        obj = self.getObjectByUuid(col_name, obj_uuid)
        is_committed_type = False 
        
        dt = None
        if type(attr_type) in (str, unicode) and len(attr_type) == UUID_LEN:
            # assume attr_type is a uuid of a named datatype
            is_committed_type = True
            tgt = self.getCommittedTypeObjByUuid(attr_type)
            if tgt is None:
                msg = "Unable to create attribute, committed type with uuid of: " + attr_type + " not found"
                self.log.info(msg)
                raise IOError(errno.ENXIO, msg)
            dt = tgt  # can use the object as the dt parameter
        else:    
            dt = self.createTypeFromItem(attr_type)
        if dt is None:
            msg = "Unexpected error creating datatype for attribute"
            self.log.error(msg)
            raise IOError(errno.EIO, msg)
            
        if shape == None:
            # create null space dataset
            # null space datasets not supported in h5py yet:
            # See: https://github.com/h5py/h5py/issues/279
            # work around this by using low-level interface.
            # first create a temp scalar dataset so we can pull out the typeid
            tmpGrp = None
            if "{tmp}" not in self.dbGrp:
                tmpGrp = self.dbGrp.create_group("{tmp}")
            else:
                tmpGrp = self.dbGrp["{tmp}"]
            tmpGrp.attrs.create(attr_name, 0, shape=(), dtype=dt)
            tmpAttr = h5py.h5a.open(tmpGrp.id, name=attr_name)
            if not tmpAttr:
                msg = "Unexpected error creating datatype for nullspace attribute"
                self.log.error(msg)
                raise IOError(errno.EIO, msg)                
            tid = tmpAttr.get_type()
            sid = sid = h5py.h5s.create(h5py.h5s.NULL)
            # now create the permanent attribute
            attr_id = h5py.h5a.create(obj.id, attr_name, tid, sid)
            # delete the temp attribute
            del tmpGrp.attrs[attr_name]
            if not attr_id:
                msg = "Unexpected error creating nullspace attribute"
                self.log.error(msg)
                raise IOError(errno.EIO, msg)
        else:  
            if type(value) == tuple:
                value = list(value) 
            if not is_committed_type:
            	# apparently committed types can not be used as reference types
                # todo - verify why that is
		 
            	h5t_check = h5py.check_dtype(ref=dt)
            	if h5t_check is h5py.Reference:
                    # convert value to data refs
                    value = self.listToRef(value)
                   
            obj.attrs.create(attr_name, value, dtype=dt)
     
        now = time.time()
        self.setCreateTime(obj_uuid, objType="attribute", name=attr_name, timestamp=now)
        self.setModifiedTime(obj_uuid, objType="attribute", name=attr_name, timestamp=now)
        self.setModifiedTime(obj_uuid, timestamp=now)  # owner entity is modified
        
    def deleteAttribute(self, col_name, obj_uuid, attr_name):
        self.initFile()
        if self.readonly:
            msg = "Unable to delete attribute (updates are not allowed)"
            self.log.info(msg)
            raise IOError(errno.EPERM, msg)
        obj = self.getObjectByUuid(col_name, obj_uuid)
        
        if attr_name not in obj.attrs:
            msg = "Attribute with name: [" + attr_name + "] of object: " + obj_uuid + " not found"
            self.log.info(msg)
            raise IOError(errno.ENXIO, msg)
        
        del obj.attrs[attr_name]
        now = time.time()
        self.setModifiedTime(obj_uuid, objType="attribute", name=attr_name, timestamp=now)
        
        return True
        
    """
       Create ascii representation of vlen data object
    """    
    def vlenToList(self, data):
        # todo - verify that data is a numpy.ndarray
        out = None
        try:
            if data.dtype.kind != 'O':
                out = data.tolist()
            else:
                out = []
                for item in data:
                    out.append(self.vlenToList(item))  # recursive call
        except AttributeError:
            # looks like this is not a numpy ndarray, just return the value
            out = data
        return out
        
    """
      Get item description of region reference value
    """
    def getRegionReference(self, regionRef):
        selectionEnums = { h5py.h5s.SEL_NONE:       'H5S_SEL_NONE',
                           h5py.h5s.SEL_ALL:        'H5S_SEL_ALL', 
                           h5py.h5s.SEL_POINTS:     'H5S_SEL_POINTS',
                           h5py.h5s.SEL_HYPERSLABS: 'H5S_SEL_HYPERSLABS'
                          }
                         
        #if regionRef.typecode not in selectionEnums:
        #    self.log.error("Unexpected selection type: " + regionRef.typecode)
        #    return None
        item = {}
        objid = h5py.h5r.dereference(regionRef, self.f.file.file.id)
        if objid:
            item['id'] = self.getUUIDByAddress(h5py.h5o.get_info(objid).addr)
            
        sel = h5py.h5r.get_region(regionRef, objid)  
        select_type = sel.get_select_type()
        if select_type not in selectionEnums:
            msg = "Unexpected selection type: " + regionRef.typecode
            self.log.error(msg)
            raise IOError(errno.EIO, msg)
        item['select_type'] = selectionEnums[select_type]
        points = None
        if select_type == h5py.h5s.SEL_POINTS:
            # retrieve a numpy array of selection points
            points = sel.get_select_elem_pointlist()      
        elif select_type == h5py.h5s.SEL_HYPERSLABS:
            points = sel.get_select_hyper_blocklist()        
        if points is not None:
            item['selection'] = points[...].tolist()     
        
        return item 
           
        
        
    """
       Create ascii representation of ref data object
    """    
    def refToList(self, data):
        # todo - verify that data is a numpy.ndarray
        out = None
        if type(data) is h5py.h5r.Reference:
            if bool(data):
                grpref = self.f[data]
                addr = h5py.h5o.get_info(grpref.id).addr
                uuid = self.getUUIDByAddress(addr)
                if self.getGroupObjByUuid(uuid):
                    out = "/groups/" + uuid
                elif self.getDatasetObjByUuid(uuid):
                    out = "/datasets/" + uuid
                elif self.getCommittedTypeObjByUuid(uuid):
                    out = "/datatypes/" + uuid
                else:
                    self.log.warning("uuid in region ref not found: [" + uuid + "]");
                    return None
            else:
                out = "null"
        elif type(data) is h5py.h5r.RegionReference:
            out = self.getRegionReference(data)
        else:
            out = []
            for item in data:
                out.append(self.refToList(item))  # recursive call
        return out

    """
       Convert ascii representation of data references to data ref 
    """    
    def listToRef(self, data):
        # todo - verify that data is a numpy.ndarray
        out = None
        if not data:
            # null reference
            out = self.getNullReference()
        elif type(data) in (str, unicode):
            obj_ref = None
            # object reference should be in the form: <collection_name>/<uuid>
            for prefix in ("datasets", "groups", "datatypes"):
            	if data.startswith(prefix):
                    uuid_ref = data[len(prefix):]
                    if len(uuid_ref) == (UUID_LEN + 1) and uuid_ref.startswith('/'):
                    	obj = self.getObjectByUuid(prefix, uuid_ref[1:])
                        if obj:
                            obj_ref = obj.ref
                        else:
                            msg = "Invalid object refence value: [" + uuid_ref + "] not found"
                	    self.log.info(msg)
                	    raise IOError(errno.ENXIO, msg)
                    break
            if not obj_ref:
                msg = "Invalid object refence value: [" + data + "]"
                self.log.info(msg)
                raise IOError(errno.EINVAL, msg)
            else:
                out = obj_ref

        elif type(data) in (list, tuple):
            out = []
            for item in data:
            	out.append(self.listToRef(item))  # recursive call
        else:
            msg = "Invalid object refence value: [" + data + "]"
            self.log.info(msg)
            raise IOError(errno.EINVAL, msg)
        return out
        
    """
      Convert a list to a tuple, recursively.
      Example. [[1,2],[3,4]] -> ((1,2),(3,4))
    """
    def toTuple(self, data):
        if type(data) in (list, tuple):
            return tuple(self.toTuple(x) for x in data)
        else:
            return data

    """
    Get values from dataset identified by obj_uuid.
    If a slices list or tuple is provided, it should have the same
    number of elements as the rank of the dataset.
    """    
    def getDatasetValuesByUuid(self, obj_uuid, slices=Ellipsis):
        dset = self.getDatasetObjByUuid(obj_uuid)
        if dset == None:
            return None
        values = None
        dt = dset.dtype
        rank = len(dset.shape)
        if rank == 0:
            # check for null dataspace
            try:
                val = dset[...]
            except IOError:
                # assume null dataspace, return none
                return None
            if not val:
                self.log.warning("no value returned from scalar dataset") 
                         
        if type(slices) != list and type(slices) != tuple and slices is not Ellipsis:
            msg = "Unexpected error: getDatasetValuesByUuid: bad type for dim parameter"
            self.log.error(msg)
            raise IOError(errno.EIO, msg)
                
        if (type(slices) == list or type(slices) == tuple) and len(slices) != rank:
            msg = "Unexpected error: getDatasetValuesByUuid: number of dims in selection not same as rank"
            self.log.error(msg)
            raise IOError(errno.EIO, msg)
        
        if dt.kind == 'O':    
            # numpy object type - could be a vlen string or generic vlen
            h5t_check = h5py.h5t.check_dtype(vlen=dt)
            if h5t_check == str or h5t_check == unicode:
                values = dset[slices].tolist()  # just dump to list
            elif h5t_check is not None:
                # other vlen data
                values = self.vlenToList(dset[slices])
            else:
                # check for reference type
                h5t_check = h5py.h5t.check_dtype(ref=dt)
                if h5t_check is not None:
                    # reference type
                    values = self.refToList(dset[slices])
                else:     
                    msg = "Unexpected error, object type unknown"
                    self.log.error(msg)
                    raise IOError(errno.EIO, msg)
        elif dt.kind == 'V' and  len(dt) <= 1 and len(dt.shape) == 0:
            # opaque type - skip for now
            self.log.warning("unable to print opaque type values")
            values = "????"
        else:
            # just use tolist to dump
            values = dset[slices].tolist()
        return values 
        
    """
    Get values from dataset identified by obj_uuid using the given
    point selection.
    """
    def getDatasetPointSelectionByUuid(self, obj_uuid, points):
        dset = self.getDatasetObjByUuid(obj_uuid)
        if dset == None:
            msg = "Dataset: " + obj_uuid + " not found"
            self.log.info(msg)
            raise IOError(errno.ENXIO, msg)
        rank = len(dset.shape)
        values = np.zeros(len(points), dtype=dset.dtype)
        try:
            i = 0
            for point in points:
                if rank == 1:
                    values[i] = dset[[point]]
                else:
                    values[i] = dset[tuple(point)]
                i += 1
        except ValueError:
            # out of range error
            msg = "getDatasetPointSelection, out of range error"
            self.log.info(msg)
            raise IOError(errno.EINVAL, msg)
        return values.tolist()
                 
    """
    setDatasetValuesByUuid - update the given dataset values with supplied data
      and optionally a hyperslab selection (slices)
    """    
    def setDatasetValuesByUuid(self, obj_uuid, data, slices=None):
        dset = self.getDatasetObjByUuid(obj_uuid)
        if dset == None:
            msg = "Dataset: " + obj_uuid + " not found"
            self.log.info(msg)
            raise IOError(errno.ENXIO, msg)

        # need some special conversion for compound types --
        # each element must be a tuple, but the JSON decoder
        # gives us a list instead.
        if len(dset.dtype) > 1 and type(data) in (list, tuple):
            converted_data = []
            for i in range(len(data)):
                converted_data.append(self.toTuple(data[i]))  
            data = converted_data  
        else:
            h5t_check = h5py.check_dtype(ref=dset.dtype)
            if h5t_check is h5py.Reference:
                # convert value to data refs
                data = self.listToRef(data)
        
        if slices == None:
            # write entire dataset
            dset[()] = data
        else:
            if type(slices) != tuple:
                self.log.error("getDatasetValuesByUuid: bad type for dim parameter")
                return False
            rank = len(dset.shape)
            
            if len(slices) != rank:
                self.log.error("getDatasetValuesByUuid: number of dims in selection not same as rank")
                return False 
            else: 
                if rank == 1:
                    slice = slices[0]
                    dset[slice] = data
                else:
                    dset[slices] = data     
        
        # update modified time
        self.setModifiedTime(obj_uuid)
        return True
        
    """
    setDatasetValuesByPointSelection - Update the dataset values using the given
      data and point selection
    """    
    def setDatasetValuesByPointSelection(self, obj_uuid, data, points):
        dset = self.getDatasetObjByUuid(obj_uuid)
        # need some special conversion for compound types --
        # each element must be a tuple, but the JSON decoder
        # gives us a list instead.
        if len(dset.dtype) > 1 and type(data) in (list, tuple):
            converted_data = []
            for i in range(len(data)):
                converted_data.append(self.toTuple(data[i]))  
            data = converted_data          
        if dset == None:
            msg = "Dataset: " + obj_uuid + " not found"
            self.log.info(msg)
            raise IOError(errno.ENXIO, msg)
        rank = len(dset.shape)
        
        try:
            i = 0
            for point in points:
                if rank == 1:
                    dset[[point]] = data[i]
                else:
                    dset[tuple(point)] = data[i]
                i += 1
        except ValueError:
            # out of range error
            msg = "setDatasetValuesByPointSelection, out of range error"
            self.log.info(msg)
            raise IOError(errno.EINVAL, msg)    
        
        # update modified time
        self.setModifiedTime(obj_uuid)
        return True
    
    """
    createDataset - creates new dataset given shape and datatype
    Returns item
    """   
    def createDataset(self, datatype, datashape, max_shape=None, 
        fill_value=None, obj_uuid=None):
        self.initFile()
        if self.readonly:
            msg = "Unable to create dataset (Updates are not allowed)"
            self.log.info(msg)
            raise IOError(errno.EPERM, msg)
        datasets = self.dbGrp["{datasets}"]
        if not obj_uuid:
            obj_uuid = str(uuid.uuid1())
        dt = None
        item = {}
        if type(datatype) in (str, unicode) and len(datatype) == UUID_LEN:
            # assume datatype is a uuid of a named datatype
            tgt = self.getCommittedTypeObjByUuid(datatype)
            if tgt is None:
                msg = "Unable to create dataset, committed type object: " + datatype + " not found"
                self.log.info(msg)
                raise IOError(errno.ENXIO, msg)
            dt = tgt  # can use the object as the dt parameter
        else:    
             dt = self.createTypeFromItem(datatype)
        if dt is None:
            msg = 'Unexpected error, no type returned'
            self.log.error(msg)
            raise IOError(errno.EIO, msg)
            
        dataset_id = None
        if datashape == None:
            # create null space dataset
            # null space datasets not supported in h5py yet:
            # See: https://github.com/h5py/h5py/issues/279
            # work around this by using low-level interface.
            # first create a temp scalar dataset so we can pull out the typeid
            tmpGrp = None
            if "{tmp}" not in self.dbGrp:
                tmpGrp = self.dbGrp.create_group("{tmp}")
            else:
                tmpGrp = self.dbGrp["{tmp}"]
            tmpDataset = tmpGrp.create_dataset(obj_uuid, shape=(0,), dtype=dt)
            tid = tmpDataset.id.get_type()
            sid = sid = h5py.h5s.create(h5py.h5s.NULL)
            # now create the permanent dataset
            gid = datasets.id
            dataset_id = h5py.h5d.create(gid, obj_uuid, tid, sid)   
            # delete the temp dataset
            del tmpGrp[obj_uuid]     
        else:       
            newDataset = datasets.create_dataset(obj_uuid, shape=datashape, dtype=dt, 
                maxshape=max_shape, fillvalue=fill_value)
            if newDataset:
                dataset_id = newDataset.id
            
        if dataset_id == None:
            msg = 'Unexpected failure to create dataset'
            self.log.error(msg)
            raise IOError(errno.EIO, msg)
        # store reverse map as an attribute
        addr = h5py.h5o.get_info(dataset_id).addr
        addrGrp = self.dbGrp["{addr}"]
        addrGrp.attrs[str(addr)] = obj_uuid
        
        # set timestamp
        now = time.time()
        self.setCreateTime(obj_uuid, timestamp=now)
        self.setModifiedTime(obj_uuid, timestamp=now)
        
        item['id'] = obj_uuid
        item['ctime'] = self.getCreateTime(obj_uuid)
        item['mtime'] = self.getModifiedTime(obj_uuid)
        item['attributeCount'] = 0
        return item
        
    """
    Resize existing Dataset
    """
    def resizeDataset(self, obj_uuid, shape):
        self.log.info("resizeDataset(") #  + obj_uuid + "): ") # + str(shape))
        self.initFile()
        if self.readonly:
            msg = "Unable to resize dataset (Updates are not allowed)"
            self.log.info(msg)
            raise IOError(errno.EACESS, msg)  
        dset = self.getDatasetObjByUuid(obj_uuid)  # will throw exception if not found
        if len(shape) != len(dset.shape):
            msg = "Unable to resize dataset, shape has wrong number of dimensions"
            self.log.info(msg)
            raise IOError(errno.EINVAL, msg)
        for i in range(len(shape)):
            if shape[i] < dset.shape[i]:
                msg = "Unable to resize dataset, cannot make extent smaller"
                self.log.info(msg)
                raise IOError(errno.EINVAL, msg)
            if dset.maxshape[i] != None and shape[i] > dset.maxshape[i]:
                msg = "Unable to resize dataset, max extent exceeded"
                self.log.info(msg)
                raise IOError(errno.EINVAL, msg)
        
        dset.resize(shape)  # resize
        
        # update modified time
        self.setModifiedTime(obj_uuid)
    
    """
    Check if link points to given target (as a HardLink)
    """
    def isObjectHardLinked(self, parentGroup, targetGroup, linkName):
        try:
            linkObj = parentGroup.get(linkName, None, False, True)
            linkClass = linkObj.__class__.__name__
        except TypeError:
            # UDLink? Ignore for now
            return False
        if linkClass == 'SoftLink':
            return False
        elif linkClass == 'ExternalLink':
            return False
        elif linkClass == 'HardLink':
            if parentGroup[linkName] == targetGroup:
                return True
        else:
            self.log.warning("unexpected linkclass: " + linkClass)
            return False    
     
    """
    Delete Dataset, Group or Datatype by UUID
    """    
    def deleteObjectByUuid(self, objtype, obj_uuid):
        if objtype not in ('group', 'dataset', 'datatype'):
            msg = "unexpected objtype: " + objtype
            self.log.error(msg)
            raise IOError(errno.EIO, msg)
        self.initFile()
        self.log.info("delete uuid: " + obj_uuid)
        if self.readonly:
            msg = "Unable to delete object (Updates are not allowed)"
            self.log.info(msg)
            raise IOError(errno.EPERM, msg)
            
        if obj_uuid == self.dbGrp.attrs["rootUUID"] and objtype == 'group':
            # can't delete root group
            msg = "Unable to delete group (root group may not be deleted)" 
            self.log.info(msg)
            raise IOError(errno.EPERM, msg)
            
        dbCol = None
        tgt = None
        if objtype == 'dataset':
            tgt = self.getDatasetObjByUuid(obj_uuid)
            dbCol = self.dbGrp["{datasets}"]  
        elif objtype == 'group':
            tgt = self.getGroupObjByUuid(obj_uuid)
            dbCol = self.dbGrp["{groups}"]
        else:  # datatype
            tgt = self.getCommittedTypeObjByUuid(obj_uuid)
            dbCol = self.dbGrp["{datatypes}"]
            
        if tgt == None:
            msg = "Unable to delete " + objtype + ", uuid: " + obj_uuid + " not found"
            self.log.error(msg)
            raise IOError(errno.ENXIO, msg)
            
        # unlink from root (if present)     
        self.unlinkObject(self.f['/'], tgt) 
         
        groups = self.dbGrp["{groups}"]
        # iterate through each group in the file and unlink tgt if it is linked
        # by the group.
        # We'll store a list of links to be removed as we go, and then actually
        # remove the links after the iteration is done (otherwise we can run into issues
        # where the key has become invalid)
        linkList = []  # this is our list
        for uuidName in groups.attrs:
            grpRef = groups.attrs[uuidName]
            # de-reference handle
            grp = self.f[grpRef]
            for linkName in grp:
                if self.isObjectHardLinked(grp, tgt, linkName):
                    linkList.append({'group': grp, 'link': linkName})
        for item in linkList:
            self.unlinkObjectItem(item['group'], tgt, item['link'])
                  
        addr = h5py.h5o.get_info(tgt.id).addr
        addrGrp = self.dbGrp["{addr}"] 
        del addrGrp.attrs[str(addr)]  # remove reverse map
        dbRemoved = False
          
        # finally, remove the dataset from db
        if obj_uuid in dbCol:
            # should be here (now it is anonymous)
            del dbCol[obj_uuid]
            dbRemoved = True
        
        if not dbRemoved:
            self.log.warning("did not find: " + obj_uuid + " in anonymous collection")
                
            if obj_uuid in dbCol.attrs:
                self.log.info("removing: " + obj_uuid + " from non-anonymous collection")
                del dbCol.attrs[obj_uuid]
                dbRemoved = True
             
        if not dbRemoved:
            msg = "Unexpected Error, did not find reference to: " + obj_uuid
            self.log.error(msg)
            raise IOError(errno.EIO, msg)
        
        # note when the object was deleted
        self.setModifiedTime(obj_uuid)
               
        return True
          
        
    def getGroupItemByUuid(self, obj_uuid):
        self.initFile()
        grp = self.getGroupObjByUuid(obj_uuid)
        if grp == None:
            if self.getModifiedTime(obj_uuid, useRoot=False):
                msg = "Group with uuid: " + obj_uuid + " has been previously deleted"
                self.log.info(msg)
                raise IOError(errno.ENOENT, msg)
            else:
                msg = "Group with uuid: " + obj_uuid + " was not found"
                self.log.info(msg)
                raise IOError(errno.ENXIO, msg)
        
        linkCount = len(grp)    
        if "__db__" in grp:
            linkCount -= 1  # don't include the db group
        
        item = { 'id': obj_uuid }
        alias = []
        if grp.name:
            alias.append(grp.name)   # just use the default h5py path for now
        item['alias'] = alias
        item['attributeCount'] = len(grp.attrs)
        item['linkCount'] = linkCount
        item['ctime'] = self.getCreateTime(obj_uuid)
        item['mtime'] = self.getModifiedTime(obj_uuid)
        
        return item
       
    """
    getLinkItemByObj - return info about a link
        parent: reference to group
        linkName: name of link
        return: item dictionary with link attributes, or None if not found
    """    
    def getLinkItemByObj(self, parent, link_name):
        if not link_name in parent:
            return None
            
        if link_name == "__db__":
            return None  # don't provide link to db group
        #  "http://somefile/#h5path(somepath)")
        item = { 'title': link_name } 
        # get the link object, one of HardLink, SoftLink, or ExternalLink
        try:
            linkObj = parent.get(link_name, None, False, True)
            linkClass = linkObj.__class__.__name__
        except TypeError:
            # UDLink? set class as 'user'
            linkClass = 'UDLink' # user defined links
            item['class'] = 'H5L_TYPE_USER_DEFINED'
        if linkClass == 'SoftLink':
            item['class'] = 'H5L_TYPE_SOFT'
            item['h5path'] = linkObj.path
            item['href'] = '#h5path(' + linkObj.path + ')'
        elif linkClass == 'ExternalLink':
            item['class'] = 'H5L_TYPE_EXTERNAL'
            item['h5path'] = linkObj.path
            item['file'] = linkObj.filename
            item['href'] = '#h5path(' + linkObj.path + ')'
        elif linkClass == 'HardLink':
            # Hardlink doesn't have any properties itself, just get the linked
            # object
            obj = parent[link_name]
            addr = h5py.h5o.get_info(obj.id).addr
            item['class'] = 'H5L_TYPE_HARD'
            item['id'] = self.getUUIDByAddress(addr)
            class_name = obj.__class__.__name__ 
            if class_name == 'Dataset':
                item['href'] = 'datasets/' + item['id']
                item['collection'] = 'datasets'
            elif class_name == 'Group':
                item['href'] = 'groups/' + item['id']
                item['collection'] = 'groups'
            elif class_name == 'Datatype':
                item['href'] = 'datatypes/' + item['id']
                item['collection'] = 'datatypes'
            else:
                self.log.warning("unexpected object type: " + item['type'])
        
        return item
                 
        
    def getLinkItemByUuid(self, grpUuid, link_name):
        self.log.info("db.getLinkItemByUuid(" + grpUuid + ", [" + link_name + "])")
         
        self.initFile()
        parent = self.getGroupObjByUuid(grpUuid)
        if parent == None:
            msg = "Parent group: " + grpUuid + " of link not found"
            self.log.info(msg)
            raise IOError(errno.ENXIO, msg)
         
        item = self.getLinkItemByObj(parent, link_name) 
        # add timestamps
        if item:
            item['ctime'] = self.getCreateTime(grpUuid, objType="link", name=link_name)
            item['mtime'] = self.getModifiedTime(grpUuid, objType="link", name=link_name)
        else:
            self.log.info("link not found")
            mtime = self.getModifiedTime(grpUuid, objType="link", name=link_name, useRoot=False)
            if mtime:
                msg = "Link [" + link_name + "] of: " + grpUuid + " has been previously deleted"
                self.log.info(msg)
                raise IOError(errno.ENOENT, msg)
            else:
                msg = "Link [" + link_name + "] of: " + grpUuid + " not found"
                self.log.info(msg)
                raise IOError(errno.ENXIO, msg)     
                
        return item
        
    def getLinkItems(self, grpUuid, marker=None, limit=0):
        self.log.info("db.getLinkItems(" + grpUuid + ")")
        if marker:
            self.log.info("...marker: " + marker)
        if limit:
            self.log.info("...limit: " + str(limit))
        
        self.initFile()
        parent = self.getGroupObjByUuid(grpUuid)
        if parent == None:
            msg = "Parent group: " + grpUuid + " not found, no links returned"
            self.log.info(msg)
            raise IOError(errno.ENXIO, msg)
        items = []
        gotMarker = True
        if marker != None:
            gotMarker = False
        count = 0
        for link_name in parent:
            if link_name == "__db__":
                continue
            if not gotMarker:
                if link_name == marker:
                    gotMarker = True
                    continue  # start filling in result on next pass
                else:
                    continue  # keep going!
            item = self.getLinkItemByObj(parent, link_name)
            items.append(item)
                
            count += 1
            if limit > 0 and count == limit:
                break  # return what we got
        return items
        
    def unlinkItem(self, grpUuid, link_name):
        if self.readonly:
            msg = "Unable to unlink item (Updates are not allowed)"
            self.log.info(msg)
            raise IOError(errno.EPERM, msg) 
        grp = self.getGroupObjByUuid(grpUuid)
        if grp == None:
            msg = "Parent group: " + grpUuid + " not found, cannot remove link"
            self.log.info(msg)
            raise IOError(errno.ENXIO, msg) 
            
        if link_name not in grp:
            msg = "Link: [" + link_name + "] of group: " + grpUuid + " not found, cannot remove link"
            self.log.info(msg)
            raise IOError(errno.ENXIO, msg) 
            
        if link_name == "__db__":
            # don't allow db group to be unlinked!
            msg = "Unlinking of __db__ group not allowed"
            raise IOError(errno.EPERM, msg)
            
        obj = None   
        try:
            linkObj = grp.get(link_name, None, False, True)
            linkClass = linkObj.__class__.__name__
            if linkClass == 'HardLink':
                # we can safely reference the object
                obj = grp[link_name]
        except TypeError:
            # UDLink? Return false to indicate that we can not delete this
            msg = "Unable to unlink user defined link"
            self.log.info(msg)
            raise IOError(errno.EPERM, msg)
        
        linkDeleted = False
        if obj != None:
            linkDeleted = self.unlinkObjectItem(grp, obj, link_name)
        else:
            # SoftLink or External Link - we can just remove the key
            del grp[link_name]
            linkDeleted = True
            
        if linkDeleted:
            # update timestamp
            self.setModifiedTime(grpUuid, objType="link", name=link_name)
            
        return linkDeleted
        
    def getCollection(self, col_type, marker=None, limit=None):
        self.log.info("db.getCollection(" + col_type + ")")
        #col_type should be either "datasets", "groups", or "datatypes"
        if col_type not in ("datasets", "groups", "datatypes"):
            msg = "Unexpected col_type: [" + col_type + "]"
            self.log.error(msg)
            raise IOError(errno.EIO, msg)
        self.initFile()
        col = None  # Group, Dataset, or Datatype
        if col_type == "datasets":
            col = self.dbGrp["{datasets}"]
        elif col_type == "groups":
            col = self.dbGrp["{groups}"]
        else:  # col_type == "datatypes" 
            col = self.dbGrp["{datatypes}"] 
        
        uuids = []
        count = 0;
        # gather the non-anonymous ids first
        for obj_uuid in col.attrs:
            if marker:
                if obj_uuid == marker:
                    marker = None  # clear and pick up next item
                continue
            uuids.append(obj_uuid)
            count += 1
            if limit > 0 and count == limit:
                break
                
        if limit == 0 or count < limit:
            # grab any anonymous obj ids next
            for obj_uuid in col:
                if marker:
                    if obj_uuid == marker:
                        marker = None  # clear and pick up next item
                    continue
                uuids.append(obj_uuid)
                count += 1
                if limit > 0 and count == limit:
                    break             
                
        return uuids

    
    """
      Get the DB Collection names
    """
    def getDBCollections(self):
        return ("{groups}", "{datasets}", "{datatypes}")
    
    """
        Return the db collection the uuid belongs to
    """
    def getDBCollection(self, obj_uuid):
        dbCollections = self.getDBCollections()
        for dbCollectionName in dbCollections:
            col = self.dbGrp[dbCollectionName]
            if obj_uuid in col or obj_uuid in col.attrs:
                return col;
        return None
         
    
    def unlinkObjectItem(self, parentGrp, tgtObj, link_name):
        if self.readonly:
            msg = "Unexpected attempt to unlink object"
            self.log.error(msg)
            raise IOError(errno.EIO, msg)
        if link_name not in parentGrp:
            msg = "Unexpected: did not find link_name: [" + link_name + "]" 
            self.log.error(msg)
            raise IOError(errno.EIO, msg)
        try:
            linkObj = parentGrp.get(link_name, None, False, True)
        except TypeError:
            # user defined link?
            msg = "Unable to remove link (user-defined link?)"
            self.log.error(msg)
            raise IOError(errno.EIO, msg)
        linkClass = linkObj.__class__.__name__
        # only deal with HardLinks
        linkDeleted = False
        if linkClass == 'HardLink':
            obj = parentGrp[link_name]
            if tgtObj == None or obj == tgtObj:
                
                numlinks =  self.getNumLinksToObject(obj)
                if numlinks == 1:
                    # last link to this object - convert to anonymous object
                    # by creating link under {datasets} or {groups} or {datatypes}
                    # also remove the attribute UUID key
                    addr = h5py.h5o.get_info(obj.id).addr  
                    obj_uuid = self.getUUIDByAddress(addr)
                    self.log.info("converting: " + obj_uuid + " to anonymous obj")
                    dbCol = self.getDBCollection(obj_uuid)
                    del dbCol.attrs[obj_uuid]  # remove the object ref
                    dbCol[obj_uuid] = obj      # add a hardlink        
                self.log.info("deleting link: [" + link_name + "] from: " + parentGrp.name)
                del parentGrp[link_name]  
                linkDeleted = True    
        else:
            self.log.info("unlinkObjectItem: link is not a hardlink, ignoring")           
        return linkDeleted
        
    def unlinkObject(self, parentGrp, tgtObj):
        for name in parentGrp:
            self.unlinkObjectItem(parentGrp, tgtObj, name)             
        return True
        
        
    def linkObject(self, parentUUID, childUUID, link_name):
        self.initFile()
        if self.readonly:
            msg = "Unable to create link (Updates are not allowed)"
            self.log.info(msg)
            raise IOError(errno.EPERM, msg)  
              
        parentObj = self.getGroupObjByUuid(parentUUID)
        if parentObj == None:
            msg = "Unable to create link, parent UUID: " + parentUUID + " not found"
            self.log.info(msg)
            raise IOError(errno.ENXIO, msg)
            
        childObj = self.getDatasetObjByUuid(childUUID)
        if childObj == None:
            # maybe it's a group...
            childObj = self.getGroupObjByUuid(childUUID)
        if childObj == None:
            # or maybe it's a committed datatype...
            childObj = self.getCommittedTypeObjByUuid(childUUID)
        if childObj == None:
            msg = "Unable to link item, child UUID: " + childUUID + " not found"
            self.log.info(msg)
            raise IOError(errno.ENXIO, msg)
        if link_name in parentObj:
            # link already exists
            self.log.info("linkname already exists, deleting")
            self.unlinkObjectItem(parentObj, None, link_name)
        parentObj[link_name] = childObj
        
        # convert this from an anonymous object to ref if needed
        dbCol = self.getDBCollection(childUUID)
        if childUUID in dbCol:
            # convert to a ref
            del dbCol[childUUID]  # remove hardlink
            dbCol.attrs[childUUID] = childObj.ref # create a ref
        
        # set link timestamps
        now = time.time()
        self.setCreateTime(parentUUID, objType="link", name=link_name, timestamp=now)
        self.setModifiedTime(parentUUID, objType="link", name=link_name, timestamp=now)
        return True
        
    def createSoftLink(self, parentUUID, linkPath, link_name):
        self.initFile()
        if self.readonly:
            msg = "Unable to create link (Updates are not allowed)"
            self.log.info(msg)
            raise IOError(errno.EPERM, msg)  
        parentObj = self.getGroupObjByUuid(parentUUID)
        if parentObj == None:
            msg = "Unable to create link, parent UUID: " + parentUUID + " not found"
            self.log.info(msg)
            raise IOError(errno.ENXIO, msg)
        if link_name in parentObj:
            # link already exists
            self.log.info("linkname already exists, deleting")
            del parentObj[link_name]  # delete old link
        parentObj[link_name] = h5py.SoftLink(linkPath)
        
        now = time.time()
        self.setCreateTime(parentUUID, objType="link", name=link_name, timestamp=now)
        self.setModifiedTime(parentUUID, objType="link", name=link_name, timestamp=now)
        
        return True
        
    def createExternalLink(self, parentUUID, extPath, linkPath, link_name):
        self.initFile()
        if self.readonly:
            msg = "Unable to create link (Updates are not allowed)"
            self.log.info(msg)
            raise IOError(errno.EPERM, msg)    
        parentObj = self.getGroupObjByUuid(parentUUID)
        if parentObj == None:
            msg = "Unable to create link, parent UUID: " + parentUUID + " not found"
            self.log.info(msg)
            raise IOError(errno.ENXIO, msg)
        if link_name in parentObj:
            # link already exists
            self.log.info("linkname already exists, deleting")
            del parentObj[link_name]  # delete old link
        parentObj[link_name] = h5py.ExternalLink(extPath, linkPath)
        
        now = time.time()
        self.setCreateTime(parentUUID, objType="link", name=link_name, timestamp=now)
        self.setModifiedTime(parentUUID, objType="link", name=link_name, timestamp=now)
        
        return True
        
    
    def createGroup(self, obj_uuid=None):
        self.initFile()
        if self.readonly:
            msg = "Unable to create group (Updates are not allowed)"
            self.log.info(msg)
            raise IOError(errno.EPERM, msg)    
        groups = self.dbGrp["{groups}"]
        if not obj_uuid:
            obj_uuid = str(uuid.uuid1())
        newGroup = groups.create_group(obj_uuid)
        # store reverse map as an attribute
        addr = h5py.h5o.get_info(newGroup.id).addr
        addrGrp = self.dbGrp["{addr}"]
        addrGrp.attrs[str(addr)] = obj_uuid
        
        #set timestamps
        now = time.time()
        self.setCreateTime(obj_uuid, timestamp=now)
        self.setModifiedTime(obj_uuid, timestamp=now)
        
        return obj_uuid
        
    
    def getNumberOfGroups(self):
        self.initFile()
        count = 0
        groups = self.dbGrp["{groups}"]
        count += len(groups)        #anonymous groups
        count += len(groups.attrs)  #linked groups
        count += 1                  # add of for root group
        
        return count
           
        
    def getNumberOfDatasets(self):
        self.initFile()
        count = 0
        datasets = self.dbGrp["{datasets}"]
        count += len(datasets)        #anonymous datasets
        count += len(datasets.attrs)  #linked datasets
        return count
        
    def getNumberOfDatatypes(self):
        self.initFile()
        count = 0
        datatypes = self.dbGrp["{datatypes}"]
        count += len(datatypes)        #anonymous datatypes
        count += len(datatypes.attrs)  #linked datatypes
        return count
