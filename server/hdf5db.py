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
import sys
import time
import h5py
import numpy as np
import shutil
import uuid
import logging
import os.path as op
import os

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
            # already a file there!
            return False
        f = h5py.File(filePath, 'w')
        f.close()
        return True
           
        
    def __init__(self, filePath, readonly=False):
        mode = 'r'
        if readonly:
            self.readonly = True
        else:
            if os.access(filePath, os.W_OK):         
                mode = 'r+'
                self.readonly = False
            else:
                self.readonly = True
        #logging.info("init -- filePath: " + filePath + " mode: " + mode)
        
        self.f = h5py.File(filePath, mode)
        
        if self.readonly:
            # for read-only files, add a dot in front of the name to be used as the 
            # db file.  This won't collide with actual data files, since "." is not 
            # allowed as the first character in a domain name.
            dirname = op.dirname(self.f.filename)
            basename = op.basename(self.f.filename)
            if len(dirname) > 0: 
                dbFilePath = dirname + '/.' + basename
            else:
                dbFilePath = '.' + basename
            dbMode = 'r+'
            if not op.isfile(dbFilePath):
                dbMode = 'w'
            logging.info("dbFilePath: " + dbFilePath + " mode: " + dbMode)
            self.dbf = h5py.File(dbFilePath, dbMode)
        else:
            self.dbf = None # for read only
        # create a global reference to this class
        # so visitObj can call back
        _db[filePath] = self 
    
    def __enter__(self):
        logging.info('Hdf5db __enter')
        return self

    def __exit__(self, type, value, traceback):
        logging.info('Hdf5db __exit')
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
                logging.error("empty name passed to setCreateTime")
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
                logging.error("bad objType passed to setCreateTime")
                raise Exception("bad setCreateTimeParameter")
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
            logging.warning("modifying create time for object: " + ts_name)
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
        # logging.info("initFile")
        self.httpStatus = 200
        self.httpMessage = None
        if self.readonly:
            self.dbGrp = self.dbf
            if "{groups}" in self.dbf:
                # file already initialized
                return
            
        else:
            if "__db__" in self.f:
                # file already initialized
                self.dbGrp = self.f["__db__"]
                return;  # already initialized 
            self.dbGrp = self.f.create_group("__db__")
           
        logging.info("initializing file") 
        root_uuid = str(uuid.uuid1())
        self.dbGrp.attrs["rootUUID"] = root_uuid
        self.dbGrp.create_group("{groups}")
        self.dbGrp.create_group("{datasets}")
        self.dbGrp.create_group("{datatypes}")
        self.dbGrp.create_group("{addr}") # store object address
        self.dbGrp.create_group("{ctime}") # stores create timestamps
        self.dbGrp.create_group("{mtime}") # store modified timestamps
        
        mtime = op.getmtime(self.f.filename)
        ctime = mtime
        self.setCreateTime(root_uuid, timestamp=ctime)
        self.setModifiedTime(root_uuid, timestamp=mtime)
            
        self.f.visititems(visitObj)
        
    def visit(self, path, obj):
        name = obj.__class__.__name__
        if len(path) >= 6 and path[:6] == '__db__':
            return  # don't include the db objects
        logging.info('visit: ' + path +' name: ' + name)
        col = None 
        if name == 'Group':
            col = self.dbGrp["{groups}"].attrs
        elif name == 'Dataset':
            col = self.dbGrp["{datasets}"].attrs
        elif name == 'Datatype':
            col = self.dbGrp["{datatypes}"].attrs
        else:
            logging.error("unknown type: " + __name__)
            self.httpStatus = 500
            self.httpMessage = "Unexpected error"
            return
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
            logging.error("expected to find {addr} group") 
            return None
        addrGrp = self.dbGrp["{addr}"]
        objUuid = None
        if str(addr) in addrGrp.attrs:
            objUuid = addrGrp.attrs[str(addr)] 
        return objUuid
    
        
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
        logging.info("getUUIDByPath: [" + path + "]")
        if len(path) >= 6 and path[:6] == '__db__':
            logging.error("getUUIDByPath called with invalid path: [" + path + "]")
            raise Exception
        if path == '/':
            # just return the root UUID
            return self.dbGrp.attrs["rootUUID"]
            
        obj = self.f[path]  # will throw KeyError if object doesn't exist
        addr = h5py.h5o.get_info(obj.id).addr
        objUuid = self.getUUIDByAddress(addr)
        return objUuid
                     
    def getObjByPath(self, path):
        if len(path) >= 6 and path[:6] == '__db__':
            return None # don't include the db objects
        obj = self.f[path]  # will throw KeyError if object doesn't exist
        return obj
        
    
    def getObjectByUuid(self, col_type, objUuid):
        #col_type should be either "datasets", "groups", or "datatypes"
        if col_type not in ("datasets", "groups", "datatypes"):
            logging.error("invalid col_type: [" + col_type + "]")
            self.httpStatus = 500
            return None
        if col_type == "groups" and objUuid == self.dbGrp.attrs["rootUUID"]:
            return self.f['/']  # returns root group
            
        obj = None  # Group, Dataset, or Datatype
        col_name = '{' + col_type + '}'
        # get the collection group for this collection type
        col = self.dbGrp[col_name]
        if objUuid in col.attrs:
            ref = col.attrs[objUuid]
            obj = self.f[ref]  # this works for read-only as well
        elif objUuid in col: 
            # anonymous object
            obj = col[objUuid]
                
        return obj
        
    def getDatasetObjByUuid(self, objUuid):
        logging.info("getDatasetObjByUuid(" + objUuid + ")")
        self.initFile()
        obj = self.getObjectByUuid("datasets", objUuid)
                                 
        if obj == None:
            if self.getModifiedTime(objUuid, useRoot=False):
                self.httpStatus = 410  # Gone
                self.httpMessage = "Resource has been removed"
            else:
                self.httpStatus = 404  # Not Found
                self.httpMessage = "Resource not found"
        return obj
        
    def getGroupObjByUuid(self, objUuid):
        logging.info("getGroupObjByUuid(" + objUuid + ")")
        self.initFile()
        obj =  self.getObjectByUuid("groups", objUuid)
         
        if obj == None:
            if self.getModifiedTime(objUuid, useRoot=False):
                self.httpStatus = 410  # Gone
                self.httpMessage = "Resource has been removed"
            else:
                self.httpStatus = 404  # Not Found
                self.httpMessage = "Resource not found"
        return obj
    
    def getDatasetTypeItemByUuid(self, objUuid):
        dset = self.getDatasetObjByUuid(objUuid)
        if dset == None:
            logging.info("dataset: " + objUuid + " not found")
            return None
        item = { 'id': objUuid }
        item['type'] = hdf5dtype.getTypeItem(dset.dtype)
        item['ctime'] = self.getCreateTime(objUuid)
        item['mtime'] = self.getModifiedTime(objUuid)      
        
        return item    
        
    def getShapeItemByDsetObj(self, obj):
        item = {}
        if len(obj.shape) == 0:
            # check to see if this is a null space vs a scalar dataset
            # we'll do this by seeing if an exception is raised when reading the dataset
            # h5py issue https://github.com/h5py/h5py/issues/279 will provide a better
            # way to determine null spaces
            try: 
                val = obj[...]
                item['class'] = 'H5S_SCALAR'
            except IOError:
                item['class'] = 'H5S_NULL'
        else:
            item['class'] = 'H5S_SIMPLE'
            item['dims'] = obj.shape
            maxshape = []
            for i in range(len(obj.shape)):
                extent = 0
                if len(obj.maxshape) > i:
                    if obj.maxshape[i] != None:
                        extent = obj.maxshape[i]
                maxshape.append(extent)
            item['maxdims'] = maxshape
        return item
        
    def getShapeItemByAttrObj(self, obj):
        item = {}
        if len(obj.shape) == 0:
            # No clear way to determine if an attribute has a null space or not.
            # for now, just return scalar.
            # See: h5py issue https://github.com/h5py/h5py/issues/279  
            item['class'] = 'H5S_SCALAR'
        else:
            item['class'] = 'H5S_SIMPLE'
            item['dims'] = obj.shape
        return item
        
    def getDatasetItemByUuid(self, objUuid):
        dset = self.getDatasetObjByUuid(objUuid)
        if dset == None:
            logging.info("dataset: " + objUuid + " not found")
            return None
        item = { 'id': objUuid }
        
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
            
        item['ctime'] = self.getCreateTime(objUuid)
        item['mtime'] = self.getModifiedTime(objUuid)      
        
        return item
        
    """
    createCommittedType - creates new named datatype  
    Returns UUID
    """   
    def createCommittedType(self, datatype):
        self.initFile()
        if self.readonly:
            self.httpStatus = 403  # Forbidden
            self.httpMessage = "Updates are not allowed"
            return None   
        datatypes = self.dbGrp["{datatypes}"]
        objUuid = str(uuid.uuid1())
        dt = hdf5dtype.createDataType(datatype);
        if dt is None:
            logging.error('no type returned')
            return None  # invalid type
        datatypes[objUuid] = np.dtype(dt)  # dt
        
        if objUuid not in datatypes:
            logging.error('unexpected failure to create named datatype')
            return None
        newType = datatypes[objUuid] # this will be a h5py Datatype class 
        # store reverse map as an attribute
        addr = h5py.h5o.get_info(newType.id).addr
        addrGrp = self.dbGrp["{addr}"]
        addrGrp.attrs[str(addr)] = objUuid
        # set timestamp
        now = time.time()
        self.setCreateTime(objUuid, timestamp=now)
        self.setModifiedTime(objUuid, timestamp=now)
        return objUuid
      
    """
    getCommittedTypeObjByUuid - get obj from {datatypes} collection 
    Returns type obj
    """   
    def getCommittedTypeObjByUuid(self, objUuid):
        logging.info("getCommittedTypeObjByUuid(" + objUuid + ")")
        self.initFile()
        datatype = None
        datatypesGrp = self.dbGrp["{datatypes}"]
        if objUuid in datatypesGrp.attrs:
            typeRef = datatypesGrp.attrs[objUuid]
            # typeRef could be a reference or (for read-only) a path
            datatype = self.f[typeRef]
        elif objUuid in datatypesGrp:
            datatype = datatypesGrp[objUuid]  # non-linked type
     
        return datatype
        
    """
    getCommittedTypeItemByUuid - get json from {datatypes} collection 
    Returns type obj
    """   
    def getCommittedTypeItemByUuid(self, objUuid):
        logging.info("getCommittedTypeItemByUuid(" + objUuid + ")")
        self.initFile()
        datatype = self.getCommittedTypeObjByUuid(objUuid)
         
        if datatype == None:
            if self.getModifiedTime(objUuid, useRoot=False):
                self.httpStatus = 410  # Gone
                self.httpMessage = "Resource has been removed"
            else:
                self.httpStatus = 404  # Not Found
                self.httpMessage = "Resource not found"
            return None
        item = { 'id': objUuid }
        alias = []
        if datatype.name:
            alias.append(datatype.name)   # just use the default h5py path for now
        item['alias'] = alias
        item['attributeCount'] = len(datatype.attrs)
        item['type'] = hdf5dtype.getTypeItem(datatype.dtype) 
        item['ctime'] = self.getCreateTime(objUuid)
        item['mtime'] = self.getModifiedTime(objUuid) 
        
        return item
       
    """
      Get attribute given an object and name
      returns: Json object 
    """ 
    def getAttributeItemByObj(self, obj, name, includeData=True):
         
        if name not in obj.attrs:
            logging.info("attribute: [" + name + "] not found in object: " + obj.name)
            self.httpStatus = 404  # not found
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
        if includeData:
            try:
                attr = obj.attrs[name]  # returns a numpy array
            except TypeError:
                logging.warning("type error reading attribute") 
        item['shape'] = self.getShapeItemByAttrObj(attrObj)
        if includeData and attr is not None:
            if typeItem['class'] == 'H5T_VLEN':
                item['value'] = self.vlenToList(attr)
            elif typeItem['class'] == 'H5T_REFERENCE':
                item['value'] = self.refToList(attr)
            elif typeItem['class'] == 'H5T_COMPOUND':
                item['value'] = attr.tolist()  # convert to list
            else:
                item['value'] = attr.tolist()  # convert to list
        # timestamps will be added by getAttributeItem()
        return item
            
    def getAttributeItems(self, col_type, objUuid, marker=None, limit=0):
        logging.info("db.getAttributeItems(" + objUuid + ")")
        if marker:
            logging.info("...marker: " + marker)
        if limit:
            logging.info("...limit: " + str(limit))
        
        self.initFile()
        obj = self.getObjectByUuid(col_type, objUuid)
        if obj == None:
            logging.error("uuid: " + objUuid + " could not be loaded")
            self.httpStatus = 404  # not found
            return None
            
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
            item['ctime'] = self.getCreateTime(objUuid, objType="attribute", name=name)
            item['mtime'] = self.getModifiedTime(objUuid, objType="attribute", name=name)
                           
            items.append(item)
            count += 1
            if limit > 0 and count == limit:
                break  # return what we got
        return items
            
    def getAttributeItem(self, col_type, objUuid, name):
        logging.info("getAttributeItemByUuid(" + col_type + ", " + objUuid + ", " + 
            name + ")")
        self.initFile()
        obj = self.getObjectByUuid(col_type, objUuid)
        if obj == None:
            return None
        item = self.getAttributeItemByObj(obj, name)
        if item == None:
            return None
        # mix-in timestamps
        item['ctime'] = self.getCreateTime(objUuid, objType="attribute", name=name)
        item['mtime'] = self.getModifiedTime(objUuid, objType="attribute", name=name)
            
        return item
        
    def createAttribute(self, col_name, objUuid, attr_name, shape, attr_type, value):
        self.initFile()
        if self.readonly:
            self.httpStatus = 403  # Forbidden
            self.httpMessage = "Updates are not allowed"
            return None   
        obj = self.getObjectByUuid(col_name, objUuid)
        
        dt = None
        if type(attr_type) in (str, unicode) and len(attr_type) == UUID_LEN:
            # assume attr_type is a uuid of a named datatype
            tgt = self.getCommittedTypeObjByUuid(attr_type)
            if tgt is None:
                self.httpStatus = 404  # not found
                return None
            dt = tgt  # can use the object as the dt parameter
        else:    
            try:
                dt = hdf5dtype.createDataType(attr_type)
            except Exception:
                self.httpStatus = 400 # invalid
                return None
        if dt is None:
            logging.error('no type returned')
            self.httpStatus = 500  # unexpected
            return None  # invalid type  
            
        if type(value) == tuple:
            value = list(value) 
        newAttr = obj.attrs.create(attr_name, value, dtype=dt)
        now = time.time()
        self.setCreateTime(objUuid, objType="attribute", name=attr_name, timestamp=now)
        self.setModifiedTime(objUuid, objType="attribute", name=attr_name, timestamp=now)
        self.setModifiedTime(objUuid, timestamp=now)  # owner entity is modified
        
    def deleteAttribute(self, col_name, objUuid, attr_name):
        self.initFile()
        if self.readonly:
            self.httpStatus = 403  # Forbidden
            self.httpMessage = "Updates are not allowed"
            return False   
        obj = self.getObjectByUuid(col_name, objUuid)
        
        if attr_name not in obj.attrs:
            self.httpStatus = 404 # not found
            return False
        
        del obj.attrs[attr_name]
        now = time.time()
        self.setModifiedTime(objUuid, objType="attribute", name=attr_name, timestamp=now)
        
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
        #    logging.error("Unexpected selection type: " + regionRef.typecode)
        #    return None
        item = {}
        objid = h5py.h5r.dereference(regionRef, self.f.file.file.id)
        if objid:
            item['id'] = self.getUUIDByAddress(h5py.h5o.get_info(objid).addr)
            
        sel = h5py.h5r.get_region(regionRef, objid)  
        select_type = sel.get_select_type()
        if select_type not in selectionEnums:
            logging.error("Unexpected selection type: " + regionRef.typecode)
            return None
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
                    logging.warning("uuid in region ref not found: [" + uuid + "]");
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
    Get values from dataset identified by objUuid.
    If a slices list or tuple is provided, it should have the same
    number of elements as the rank of the dataset.
    """    
    def getDatasetValuesByUuid(self, objUuid, slices=Ellipsis):
        dset = self.getDatasetObjByUuid(objUuid)
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
                         
        if type(slices) != list and type(slices) != tuple and slices is not Ellipsis:
            logging.error("getDatasetValuesByUuid: bad type for dim parameter")
            return None
                
        if (type(slices) == list or type(slices) == tuple) and len(slices) != rank:
            logging.error("getDatasetValuesByUuid: number of dims in selection not same as rank")
            return None 
        
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
                    self.httpStatus = 500
                    logging.error("unknown object type")
        elif dt.kind == 'V' and  len(dt) <= 1 and len(dt.shape) == 0:
            # opaque type - skip for now
            logging.warning("unable to print opaque type values")
            values = "????"
        else:
            # just use tolist to dump
            values = dset[slices].tolist()
        return values 
        
    """
    Get values from dataset identified by objUuid using the given
    point selection.
    """
    def getDatasetPointSelectionByUuid(self, objUuid, points):
        self.httpStatus = 200
        dset = self.getDatasetObjByUuid(objUuid)
        if dset == None:
            logging.info("dataset: " + objUuid + " not found")
            self.httpStatus = 404  # not found
            return False
        rank = len(dset.shape)
        values = np.zeros(len(points), dtype=dset.dtype)
        try:
            i = 0
            for point in points:
                # need to convert to strings so result can be JSON serializable
                #values.append(dset[[point]].tolist())
                if rank == 1:
                    values[i] = dset[[point]]
                else:
                    values[i] = dset[tuple(point)]
                i += 1
        except ValueError:
            # out of range error
            logging.info("getDatasetPointSelection, out of range error")
            self.httpStatus = 400
            return None
        return values.tolist()
                 
        
    def setDatasetValuesByUuid(self, objUuid, data, slices=None):
        dset = self.getDatasetObjByUuid(objUuid)
        if dset == None:
            logging.info("dataset: " + objUuid + " not found")
            self.httpStatus = 404  # not found
            return False
        if slices == None:
            # write entire dataset
            dset[()] = data
        else:
            if type(slices) != tuple:
                logging.error("getDatasetValuesByUuid: bad type for dim parameter")
                return False
            rank = len(dset.shape)
            
            if len(slices) != rank:
                logging.error("getDatasetValuesByUuid: number of dims in selection not same as rank")
                return False 
            else: 
                if rank == 1:
                    slice = slices[0]
                    dset[slice] = data
                else:
                    dset[slices] = data     
        
        # update modified time
        self.setModifiedTime(objUuid)
        return True
    
    """
    createDataset - creates new dataset given shape and datatype
    Returns UUID
    """   
    def createDataset(self, datatype, datashape, max_shape=None, fill_value=None):
        self.initFile()
        if self.readonly:
            self.httpStatus = 403  # Forbidden
            self.httpMessage = "Updates are not allowed"
            return None   
        datasets = self.dbGrp["{datasets}"]
        objUuid = str(uuid.uuid1())
        dt = None
        if type(datatype) in (str, unicode) and len(datatype) == UUID_LEN:
            # assume datatype is a uuid of a named datatype
            tgt = self.getCommittedTypeObjByUuid(datatype)
            if tgt is None:
                self.httpStatus = 404  # not found
                return None
            dt = tgt  # can use the object as the dt parameter
        else:    
            try:
                dt = hdf5dtype.createDataType(datatype)
            except Exception:
                self.httpStatus = 400 # invalid
                return None
        if dt is None:
            logging.error('no type returned')
            self.httpStatus = 500  # unexpected
            return None  # invalid type     
            
        newDataset = datasets.create_dataset(objUuid, shape=datashape, dtype=dt, 
            maxshape=max_shape, fillvalue=fill_value)
        if newDataset == None:
            logging.error('unexpected failure to create dataset')
            return None
        # store reverse map as an attribute
        addr = h5py.h5o.get_info(newDataset.id).addr
        addrGrp = self.dbGrp["{addr}"]
        addrGrp.attrs[str(addr)] = objUuid
        
        # set timestamp
        now = time.time()
        self.setCreateTime(objUuid, timestamp=now)
        self.setModifiedTime(objUuid, timestamp=now)
        return objUuid
        
    """
    Resize existing Dataset
    """
    def resizeDataset(self, objUuid, shape):
        logging.info("resizeDataset(") #  + objUuid + "): ") # + str(shape))
        self.initFile()
        self.httpStatus = 500  # will reset before returning
        if self.readonly:
            self.httpStatus = 403  # Forbidden
            self.httpMessage = "Updates are not allowed"
            return    
        dset = self.getDatasetObjByUuid(objUuid)
        if dset == None:
            self.httpStatus = 404  # Not found
            return
        if len(shape) != len(dset.shape):
            self.httpStatus = 400  
            self.httpMessage = "Resize shape doesn't match dataset rank"
            return
        for i in range(len(shape)):
            if shape[i] < dset.shape[i]:
                self.httpStatus = 400  
                self.httpMessage = "Resize cannot make extent smaller"
                return
            if dset.maxshape[i] != None and shape[i] > dset.maxshape[i]:
                self.httpStatus = 400  
                self.httpMessage = "Max extent exceeeded"
                return
        
        dset.resize(shape)  # resize
        
        # update modified time
        self.setModifiedTime(objUuid)
        self.httpStatus = 200
    
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
            logging.warning("unexpected linkclass: " + linkClass)
            return False    
     
    """
    Delete Dataset, Group or Datatype by UUID
    """    
    def deleteObjectByUuid(self, objUuid):
        self.initFile()
        logging.info("delete uuid: " + objUuid)
        if self.readonly:
            self.httpStatus = 403  # Forbidden
            self.httpMessage = "Updates are not allowed"
            return False   
            
        if objUuid == self.dbGrp.attrs["rootUUID"]:
            # can't delete root group
            logging.info("attempt to delete root group")
            self.httpStatus = 403
            self.httpMessage = "Root group can not be deleted"
            return False
            
        dbCol = None
        tgt = self.getDatasetObjByUuid(objUuid)
        if tgt:
            dbCol = self.dbGrp["{datasets}"]  
        
        if tgt == None:
            #maybe this is a group...
            tgt = self.getGroupObjByUuid(objUuid)
            if tgt:
                dbCol = self.dbGrp["{groups}"]
            
        if tgt == None:
            # ok - last chance - check for datatype
            tgt = self.getCommittedTypeObjByUuid(objUuid)
            if tgt:
                dbCol = self.dbGrp["{datatypes}"]
            
        if tgt == None:
            logging.info("delete uuid: " + objUuid + " not found")
            self.httpStatus = 404  # Not Found
            self.httpMessage = "id: " + objUuid + " was not found"
            return False 
            
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
        if objUuid in dbCol:
            # should be here (now it is anonymous)
            del dbCol[objUuid]
            dbRemoved = True
        
        if not dbRemoved:
            logging.warning("did not find: " + objUuid + " in anonymous collection")
                
            if objUuid in dbCol.attrs:
                logging.info("removing: " + objUuid + " from non-anonymous collection")
                del dbCol.attrs[objUuid]
                dbRemoved = True
             
        if not dbRemoved:
            logging.error("expected to find reference to: " + objUuid)
        else:
            # note when the object was deleted
            self.setModifiedTime(objUuid)
               
        return dbRemoved
          
        
    def getGroupItemByUuid(self, objUuid):
        self.initFile()
        grp = self.getGroupObjByUuid(objUuid)
        if grp == None:
            return None
        
        
        linkCount = len(grp)    
        if "__db__" in grp:
            linkCount -= 1  # don't include the db group
        
        item = { 'id': objUuid }
        alias = []
        if grp.name:
            alias.append(grp.name)   # just use the default h5py path for now
        item['alias'] = alias
        item['attributeCount'] = len(grp.attrs)
        item['linkCount'] = linkCount
        item['ctime'] = self.getCreateTime(objUuid)
        item['mtime'] = self.getModifiedTime(objUuid)
        
        return item
       
    """
    getLinkItemByObj - return info about a link
        parent: reference to group
        linkName: name of link
        return: item dictionary with link attributes, or None if not found
    """    
    def getLinkItemByObj(self, parent, linkName):
        if not linkName in parent:
            return None
            
        if linkName == "__db__":
            return None  # don't provide link to db group
            
        item = { 'name': linkName } 
        # get the link object, one of HardLink, SoftLink, or ExternalLink
        try:
            linkObj = parent.get(linkName, None, False, True)
            linkClass = linkObj.__class__.__name__
        except TypeError:
            # UDLink? set class as 'user'
            linkClass = 'UDLink' # user defined links
            item['className'] = linkClass  
            item['class'] = 'user'
        if linkClass == 'SoftLink':
            item['class'] = 'soft'
            item['className'] = linkClass
            item['path'] = linkObj.path
        elif linkClass == 'ExternalLink':
            item['class'] = 'external'
            item['className'] = linkClass
            item['path'] = linkObj.path
            item['filename'] = linkObj.filename
        elif linkClass == 'HardLink':
            # Hardlink doesn't have any properties itself, just get the linked
            # object
            obj = parent[linkName]
            addr = h5py.h5o.get_info(obj.id).addr
            item['class'] = 'hard'
            item['className'] =  obj.__class__.__name__
            item['id'] = self.getUUIDByAddress(addr)
        
        return item
                 
        
    def getLinkItemByUuid(self, grpUuid, linkName):
        logging.info("db.getLinkItemByUuid(" + grpUuid + ", [" + linkName + "])")
         
        self.initFile()
        parent = self.getGroupObjByUuid(grpUuid)
        if parent == None:
            logging.info("grp_uuid not found")
            return None
         
        item = self.getLinkItemByObj(parent, linkName) 
        # add timestamps
        if item:
            item['ctime'] = self.getCreateTime(grpUuid, objType="link", name=linkName)
            item['mtime'] = self.getModifiedTime(grpUuid, objType="link", name=linkName)
        else:
            logging.info("link not found")
            mtime = self.getModifiedTime(grpUuid, objType="link", name=linkName, useRoot=False)
            if mtime:
                self.httpStatus = 410  # Gone
                self.httpMessage = "Link has been removed"
            else:
                self.httpStatus = 404 # Not found
                self.httpMessage = "Link does not exist"        
                
        return item
        
    def getLinkItems(self, grpUuid, marker=None, limit=0):
        logging.info("db.getLinkItems(" + grpUuid + ")")
        if marker:
            logging.info("...marker: " + marker)
        if limit:
            logging.info("...limit: " + str(limit))
        
        self.initFile()
        parent = self.getGroupObjByUuid(grpUuid)
        if parent == None:
            return None
        items = []
        gotMarker = True
        if marker != None:
            gotMarker = False
        count = 0
        for linkName in parent:
            if linkName == "__db__":
                continue
            if not gotMarker:
                if linkName == marker:
                    gotMarker = True
                    continue  # start filling in result on next pass
                else:
                    continue  # keep going!
            item = self.getLinkItemByObj(parent, linkName)
            items.append(item)
                
            count += 1
            if limit > 0 and count == limit:
                break  # return what we got
        return items
        
    def unlinkItem(self, grpUuid, linkName):
        grp = self.getGroupObjByUuid(grpUuid)
        if grp == None:
            logging.info("parent group not found")
            self.httpStatus = 404 # not found
            return False 
            
        if linkName not in grp:
            logging.info("linkName not found")
            self.httpStatus = 404 # not found
            return False 
            
        if linkName == "__db__":
            # don't allow db group to be unlinked!
            logging.info("linkName not found")
            self.httpStatus = 404 # not found
            return False 
            
        obj = None   
        try:
            linkObj = grp.get(linkName, None, False, True)
            linkClass = linkObj.__class__.__name__
            if linkClass == 'HardLink':
                # we can safely reference the object
                obj = grp[linkName]
        except TypeError:
            # UDLink? Return false to indicate that we can not delete this
            self.httpStatus = 501  # Not implemented
            self.httpMessage = "Unable to remove user defined link"
            logging.info("unable to remove udlink: " + grpUuid + 
                " linkName: " + linkName)
            return False
        
        linkDeleted = False
        if obj != None:
            linkDeleted = self.unlinkObjectItem(grp, obj, linkName)
        else:
            # SoftLink or External Link - we can just remove the key
            del grp[linkName]
            linkDeleted = True
            
        if linkDeleted:
            # update timestamp
            self.setModifiedTime(grpUuid, objType="link", name=linkName)
            
        return linkDeleted
        
    def getCollection(self, col_type, marker=None, limit=None):
        logging.info("db.getCollection(" + col_type + ")")
        #col_type should be either "datasets", "groups", or "datatypes"
        if col_type not in ("datasets", "groups", "datatypes"):
            logging.error("invalid col_type: [" + col_type + "]")
            self.httpStatus = 500
            return None
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
        for uuid in col.attrs:
            if marker:
                if uuid == marker:
                    marker = None  # clear and pick up next item
                continue
            uuids.append(uuid)
            count += 1
            if limit > 0 and count == limit:
                break
                
        if limit == 0 or count < limit:
            # grab any anonymous obj ids next
            for uuid in col:
                if marker:
                    if uuid == marker:
                        marker = None  # clear and pick up next item
                    continue
                uuids.append(uuid)
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
    def getDBCollection(self, objUuid):
        dbCollections = self.getDBCollections()
        for dbCollectionName in dbCollections:
            col = self.dbGrp[dbCollectionName]
            if objUuid in col or objUuid in col.attrs:
                return col;
        return None
         
    
    def unlinkObjectItem(self, parentGrp, tgtObj, linkName):
        if self.readonly:
            self.httpStatus = 403  # Forbidden
            self.httpMessage = "Updates are not allowed"
            return None 
        if linkName not in parentGrp:
            logging.info("linkName: [" + linkName + "] not found")
            return False
        try:
            linkObj = parentGrp.get(linkName, None, False, True)
        except TypeError:
            # user defined link?
            logging.info("Unknown link type for item: " + name)
            return False
        linkClass = linkObj.__class__.__name__
        # only deal with HardLinks
        linkDeleted = False
        if linkClass == 'HardLink':
            obj = parentGrp[linkName]
            if tgtObj == None or obj == tgtObj:
                
                numlinks =  self.getNumLinksToObject(obj)
                if numlinks == 1:
                    # last link to this object - convert to anonymous object
                    # by creating link under {datasets} or {groups} or {datatypes}
                    # also remove the attribute UUID key
                    addr = h5py.h5o.get_info(obj.id).addr  
                    objUuid = self.getUUIDByAddress(addr)
                    logging.info("converting: " + objUuid + " to anonymous obj")
                    dbCol = self.getDBCollection(objUuid)
                    del dbCol.attrs[objUuid]  # remove the object ref
                    dbCol[objUuid] = obj      # add a hardlink        
                logging.info("deleting link: [" + linkName + "] from: " + parentGrp.name)
                del parentGrp[linkName]  
                linkDeleted = True    
        else:
            logging.info("unlinkObjectItem: link is not a hardlink, ignoring")           
        return linkDeleted
        
    def unlinkObject(self, parentGrp, tgtObj):
        for name in parentGrp:
            self.unlinkObjectItem(parentGrp, tgtObj, name)             
        return True
        
        
    def linkObject(self, parentUUID, childUUID, linkName):
        self.initFile()
        if self.readonly:
            self.httpStatus = 403  # Forbidden
            self.httpMessage = "Updates are not allowed"
            return False    
        parentObj = self.getGroupObjByUuid(parentUUID)
        if parentObj == None:
            self.httpStatus = 404 # Not found
            self.httpMessage = "Parent Group not found"
            return False
        childObj = self.getDatasetObjByUuid(childUUID)
        if childObj == None:
            # maybe it's a group...
            childObj = self.getGroupObjByUuid(childUUID)
        if childObj == None:
            # or maybe it's a committed datatype...
            childObj = self.getCommittedTypeObjByUuid(childUUID)
        if childObj == None:
            self.httpStatus = 404 # Not found
            self.httpMessage = "Child object not found"
            return False
        if linkName in parentObj:
            # link already exists
            logging.info("linkname already exists, deleting")
            self.unlinkObjectItem(parentObj, None, linkName)
        parentObj[linkName] = childObj
        
        # convert this from an anonymous object to ref if needed
        dbCol = self.getDBCollection(childUUID)
        if childUUID in dbCol:
            # convert to a ref
            del dbCol[childUUID]  # remove hardlink
            dbCol.attrs[childUUID] = childObj.ref # create a ref
        self.htpStatus = 201 # set status to created
        
        # set link timestamps
        now = time.time()
        self.setCreateTime(parentUUID, objType="link", name=linkName, timestamp=now)
        self.setModifiedTime(parentUUID, objType="link", name=linkName, timestamp=now)
        return True
        
    def createSoftLink(self, parentUUID, linkPath, linkName):
        self.initFile()
        if self.readonly:
            self.httpStatus = 403  # Forbidden
            self.httpMessage = "Updates are not allowed"
            return False    
        parentObj = self.getGroupObjByUuid(parentUUID)
        if parentObj == None:
            self.httpStatus = 404 # Not found
            self.httpMessage = "Parent Group not found"
            return False
        if linkName in parentObj:
            # link already exists
            logging.info("linkname already exists, deleting")
            del parentObj[linkName]  # delete old link
        parentObj[linkName] = h5py.SoftLink(linkPath)
        self.htpStatus = 201 # set status to created
        
        now = time.time()
        self.setCreateTime(parentUUID, objType="link", name=linkName, timestamp=now)
        self.setModifiedTime(parentUUID, objType="link", name=linkName, timestamp=now)
        
        return True
        
    def createExternalLink(self, parentUUID, extPath, linkPath, linkName):
        self.initFile()
        if self.readonly:
            self.httpStatus = 403  # Forbidden
            self.httpMessage = "Updates are not allowed"
            return False    
        parentObj = self.getGroupObjByUuid(parentUUID)
        if parentObj == None:
            self.httpStatus = 404 # Not found
            self.httpMessage = "Parent Group not found"
            return False
        if linkName in parentObj:
            # link already exists
            logging.info("linkname already exists, deleting")
            del parentObj[linkName]  # delete old link
        parentObj[linkName] = h5py.ExternalLink(extPath, linkPath)
        self.htpStatus = 201 # set status to created
        
        now = time.time()
        self.setCreateTime(parentUUID, objType="link", name=linkName, timestamp=now)
        self.setModifiedTime(parentUUID, objType="link", name=linkName, timestamp=now)
        
        return True
        
    
    def createGroup(self):
        self.initFile()
        if self.readonly:
            self.httpStatus = 403  # Forbidden
            self.httpMessage = "Updates are not allowed"
            return None   
        groups = self.dbGrp["{groups}"]
        objUuid = str(uuid.uuid1())
        newGroup = groups.create_group(objUuid)
        # store reverse map as an attribute
        addr = h5py.h5o.get_info(newGroup.id).addr
        addrGrp = self.dbGrp["{addr}"]
        addrGrp.attrs[str(addr)] = objUuid
        
        #set timestamps
        now = time.time()
        self.setCreateTime(objUuid, timestamp=now)
        self.setModifiedTime(objUuid, timestamp=now)
        
        return objUuid
        
    
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
