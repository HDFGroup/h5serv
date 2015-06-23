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

import weakref
import sys
import os
import uuid

import six

import requests
import json

from . import objectid
from .objectid import ObjectID, GroupID
from . import base
from .base import HLObject
from .base import phil
from . import group
from .group import Group
from . import version



hdf5_version = version.hdf5_version_tuple[0:3]

def make_fapl(driver, libver, **kwds):
    """ Set up a file access property list """
    plist = h5p.create(h5p.FILE_ACCESS)

    if libver is not None:
        if libver in libver_dict:
            low = libver_dict[libver]
            high = h5f.LIBVER_LATEST
        else:
            low, high = (libver_dict[x] for x in libver)
        plist.set_libver_bounds(low, high)

    if driver is None or (driver == 'windows' and sys.platform == 'win32'):
        return plist

    if(driver == 'sec2'):
        plist.set_fapl_sec2(**kwds)
    elif(driver == 'stdio'):
        plist.set_fapl_stdio(**kwds)
    elif(driver == 'core'):
        plist.set_fapl_core(**kwds)
    elif(driver == 'family'):
        plist.set_fapl_family(memb_fapl=plist.copy(), **kwds)
    elif(driver == 'mpio'):
        kwds.setdefault('info', mpi4py.MPI.Info())
        plist.set_fapl_mpio(**kwds)
    else:
        raise ValueError('Unknown driver type "%s"' % driver)

    return plist


class File(Group):

    """
        Represents an HDF5 file.
    """

    @property
    def attrs(self):
        """ Attributes attached to this object """
        # hdf5 complains that a file identifier is an invalid location for an
        # attribute. Instead of self, pass the root group to AttributeManager:
        from . import attrs
        return attrs.AttributeManager(self['/'])

    @property
    def filename(self):
        """File name on disk"""
        return self.id.domain
        

    @property
    def driver(self):
        return "rest_driver"

    @property
    def mode(self):
        """ Python mode used to open file """
        return self._mode

    @property
    def fid(self):
        """File ID (backwards compatibility) """
        return self.id.domain

    @property
    def libver(self):
        """File format version bounds (2-tuple: low, high)"""
        #bounds = self.id.get_access_plist().get_libver_bounds()
        #return tuple(libver_dict_r[x] for x in bounds)
        return ("0.0.1",)

    @property
    def userblock_size(self):
        """ User block size (in bytes) """
        
        return 0
       
        

    def __init__(self, domain_name, mode=None, endpoint=None, **kwds):
        """Create a new file object.

        See the h5py user guide for a detailed explanation of the options.

        name
            Name of the file on disk.  Note: for files created with the 'core'
            driver, HDF5 still requires this be non-empty.
        driver
            Name of the driver to use.  Legal values are None (default,
            recommended), 'core', 'sec2', 'stdio', 'mpio'.
        libver
            Library version bounds.  Currently only the strings 'earliest'
            and 'latest' are defined.
        userblock
            Desired size of user block.  Only allowed when creating a new
            file (mode w, w- or x).
        swmr
            Open the file in SWMR read mode. Only used when mode = 'r'.
        Additional keywords
            Passed on to the selected file driver.
        """
        
        self._endpoint = None
        print "File init"
         
        with phil:
            """
            if isinstance(name, _objects.ObjectID):
                fid = h5i.get_file_id(name)
            else:
                try:
                    # If the byte string doesn't match the default
                    # encoding, just pass it on as-is.  Note Unicode
                    # objects can always be encoded.
                    name = name.encode(sys.getfilesystemencoding())
                except (UnicodeError, LookupError):
                    pass

                fapl = make_fapl(driver, libver, **kwds)
            """
            if mode and mode not in ('r', 'r+', 'w', 'w-', 'x', 'a'):
                raise ValueError("Invalid mode; must be one of r, r+, w, w-, x, a")
                
            if mode is None:
                mode = 'a'        
            
            if endpoint is None:
                # todo - get default from env variable
                endpoint = "http://127.0.0.1:5000"
                
            root_json = None
                
            # try to do a GET from the domain
            req = endpoint + "/"
            print "domain name:", domain_name
            headers = {'host': domain_name}
            rsp = requests.get(req, headers=headers)
            
            print "req:", req
            
            if rsp.status_code == 200:
                root_json = json.loads(rsp.text)
                
            if rsp.status_code != 200 and mode in ('r', 'r+'):
                # file must exist
                raise IOError(rsp.reason)
            if rsp.status_code == 200 and mode in ('w-', 'x'):
                # Fail if exists
                raise IOError("domain already exists")
            if rsp.status_code == 200 and mode == 'w':
                # delete existing domain
                rsp = requests.delete(req, headers=headers)
                if rsp.status_code != 200:
                    # failed to delete
                    raise IOError(rsp.reason)
                root_json = None
            if root_json is None:
                # create the domain
                rsp = requests.put(req, headers=headers)
                if rsp.status_code != 201:
                    raise IOError(rsp.reason)
                root_json = json.loads(rsp.text)
                
            if 'root' not in root_json:
                raise IOError("Unexpected error")
            if 'created' not in root_json:
                raise IOError("Unexpected error")
            if 'lastModified' not in root_json:
                raise IOError("Unexpected error")
                
            print "root_json:", root_json
            root_uuid = root_json['root']
            
            # get the group json for the root group
            req = endpoint + "/groups/" + root_uuid
            
            rsp = requests.get(req, headers=headers)
            
            #print "req:", req
            
            if rsp.status_code != 200:
                raise IOError("Unexpected Error")
            group_json = json.loads(rsp.text)
                
            self._id = GroupID(None, group_json, domain=domain_name, endpoint=endpoint)
                
            self._name = '/' 
            self._mode = mode
            self._created = root_json['created']
            self._modified = root_json['lastModified']       
                    
            Group.__init__(self, self._id)

    def close(self):
        pass

    def flush(self):
        """ Tell the HDF5 library to flush its buffers.
        """
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self.id:
            self.close()

    def __repr__(self):
        if not self.id:
            r = six.u('<Closed HDF5 file>')
        else:
            # Filename has to be forced to Unicode if it comes back bytes
            # Mode is always a "native" string
            filename = self.filename
            if isinstance(filename, bytes):  # Can't decode fname
                filename = filename.decode('utf8', 'replace')
            r = six.u('<HDF5 file "%s" (mode %s)>') % (os.path.basename(filename),
                                                 self.mode)

        if six.PY3:
            return r
        return r.encode('utf8')
