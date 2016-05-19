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

import six

if six.PY3:
    unicode = str    
 
import hashlib
 

"""
 Password util helper functions
"""

    
def to_string(data):
    if six.PY3:           
        if type(data) is bytes:
            return data.decode('utf-8')
        else:
            return data
    else:
        return data
        
def to_bytes(data):
    if six.PY3:
        if type(data) is unicode:
            return data.encode('utf-8')
        else:
            return data
    else:
        return data
        
def encrypt_pwd(passwd):
    """
     One way password encryptyion
    """
    encrypted = hashlib.sha224(passwd).hexdigest()
    
    return to_bytes(encrypted)
    
    

            



 