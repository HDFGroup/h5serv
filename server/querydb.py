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
This class provides an interface to pytables.
"""

import six

if six.PY3:
    unicode = str

import tables
import os
import logging


class Querydb:
    @staticmethod
    def getVersionInfo():
        versionInfo = {}
        versionInfo['pytables_version'] = tables.__version__
        versionInfo['hdf5_version'] = tables.hdf5Version
        return versionInfo

    def __init__(self, filePath, readonly=True, app_logger=None):
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

        self.f = tables.open_file(filePath, mode=mode)

    def __enter__(self):
        self.log.info('querydb __enter')
        return self

    def __exit__(self, type, value, traceback):
        self.log.info('querydb __exit')
        filename = self.f.filename
        self.f.flush()
        self.f.close()

    def doQuery(self, item_type, path, query, start=0, stop=-1, step=1, limit=None):
        self.log.info("doQuery - path: " + path + "query:" + query)

        dset = self.f.root._f_get_child(path)
        values = []
        indexes = []
        count = 0
        if stop == -1:
            stop = dset.nrows
        for row in dset.where(query, start=start, stop=stop, step=step):
            item = []
            for field in dset.colnames:
                item.append(row[field])
            values.append(item)
            indexes.append(int(row.nrow))  # convert numpy.int64 to int
            count += 1

            if limit and (count == limit):
                break  # no more rows for this batch
        rsp = {}
        rsp["indexes"] = indexes
         
        values = self.getDataValue(item_type, values, dimension=1, dims=(len(values),))
        
        rsp["values"] = values
        return rsp

    """
      Return a json-serializable representation of the numpy value
    """
    # todo - merge this with the hdf5db.getDataValue method
    def getDataValue(self, typeItem, value, dimension=0, dims=None):
      
        if dimension > 0:
            if type(dims) not in (list, tuple):
                msg = "unexpected type for type array dimensions"
                self.log.error(msg)
                raise IOError(errno.EIO, msg)
            out = []
            rank = len(dims)
            if dimension > rank:
                msg = "unexpected dimension for type array"
                self.log.error(msg)
                raise IOError(errno.EIO, msg)
            nElements = dims[rank - dimension]
             
            for i in range(nElements):
                item_value = self.getDataValue(typeItem, value[i],
                                               dimension=(dimension-1),
                                               dims=dims)
                out.append(item_value)
            return out  # done for array case

        out = None
        typeClass = typeItem['class']
         
        """
        # this section if from the hdf5db version of this method
        if isinstance(value, (np.ndarray, np.generic)):
            value = value.tolist()  # convert numpy object to list
        else:
            pass # is not ndarray
        """
        if typeClass == 'H5T_COMPOUND':
            if type(value) not in (list, tuple):
                msg = "Unexpected type for compound value"
                self.log.error(msg)
                raise IOError(errno.EIO, msg)

            fields = typeItem['fields']
            
            if len(fields) != len(value):
                msg = "Number of elements in compound type does not match type"
                self.log.error(msg)
                raise IOError(errno.EIO, msg)
            nFields = len(fields)
            out = []
            for i in range(nFields):
                field = fields[i]
                item_value = self.getDataValue(field['type'], value[i])
                out.append(item_value)
        elif typeClass == 'H5T_VLEN':
            if type(value) not in (list, tuple):
                msg = "Unexpected type for vlen value"
                self.log.error(msg)
                raise IOError(errno.EIO, msg)

            baseType = typeItem['base']
            out = []
            nElements = len(value)
            for i in range(nElements):
                item_value = self.getDataValue(baseType, value[i])
                out.append(item_value)
        elif typeClass == 'H5T_REFERENCE':
            out = self.refToList(value)
        elif typeClass == 'H5T_OPAQUE':
            out = "???"  # todo
        elif typeClass == 'H5T_ARRAY':
            type_dims = typeItem["dims"]
            if type(type_dims) not in (list, tuple):
                msg = "unexpected type for type array dimensions"
                self.log.error(msg)
                raise IOError(errno.EIO, msg)
            rank = len(type_dims)
            baseType = typeItem['base']
            out = self.getDataValue(baseType, value, dimension=rank,
                                    dims=type_dims)

        elif typeClass in ('H5T_INTEGER', 'H5T_FLOAT', 'H5T_ENUM'):
            out = value  # just copy value
        elif typeClass == 'H5T_STRING':
           
            if six.PY3:
                if "charSet" in typeItem:
                    charSet = typeItem["charSet"]
                else:
                    charSet =  "H5T_CSET_ASCII"
                if charSet == "H5T_CSET_ASCII":
                    out = value.decode("utf-8")
                else:
                    out = value
            else:
                # things are simpler in PY2
                out = value
        else:
            msg = "Unexpected type class: " + typeClass
            self.log.info(msg)
            raise IOError(errno.ENINVAL, msg)
        return out   