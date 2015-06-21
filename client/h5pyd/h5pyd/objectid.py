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

#from base import HLObject
from . import base
from .base import phil
from . import version


 
class ObjectID:

    """
        Uniquelely identifies an h5serv resource
    """

    @property
    def uuid(self):
        return self._uuid
    
    @property    
    def id(self):
        return self._uuid

    @property
    def domain(self):
        """domain resource"""
        return self._domain
        
    @property
    def endpoint(self):
        """service endpoint"""
        return self._endpoint
        
    @property
    def parent(self):
        """parent obj - none for anonymous obj"""
        return self._parent
        

    def __init__(self, parent, uuid, domain=None, endpoint=None, **kwds):
        """Create a new objectId.
        """
        
        self._endpoint = None
         
        with phil:
            if parent is not None:
                self._domain = parent.id.domain 
                self._endpoint = parent.id.endpoint
                #self._parent = parent
            else:
                self._domain = domain
                self.endpoint = endpoint
            self._uuid = uuid
            
