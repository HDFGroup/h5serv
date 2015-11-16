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
import os
import os.path as op
from tornado.web import HTTPError
import logging

import h5py
import config
import fileUtil

"""
 TOC (Table of contents) util helper functions
 Creates a directory listing in the form of an HDF5 file
"""


def getTocFilePath():
    datapath = config.get('datapath')
    toc_file_path = op.join(datapath, config.get('toc_name'))
    if not op.exists(toc_file_path):
        createTocFile(datapath)
    return toc_file_path


def isTocFilePath(filePath):
    datapath = config.get('datapath')
    toc_file_path = op.join(datapath, config.get('toc_name'))
    if filePath == toc_file_path:
        isTocFilePath = True
    else:
        isTocFilePath = False
    return isTocFilePath


def createTocFile(dir_path):
    log = logging.getLogger("h5serv")
    log.info("createTocFile(" + dir_path + ")")
    hdf5_ext = config.get('hdf5_ext')
    if not op.exists(dir_path):
        raise IOError("invalid path")
    toc_path = op.join(dir_path, config.get('toc_name'))
    if op.isfile(toc_path):
        raise IOError("toc file exists")
    f = h5py.File(toc_path, 'w')
    for root, subdirs, files in os.walk(dir_path):
        grp_path = root[len(dir_path):]
        if not grp_path:
            continue
        grp = None
        for file_name in files:
            if file_name[0] == '.':
                continue  # skip 'hidden' files
            if len(file_name) < 4 or file_name[-3:] != hdf5_ext:
                continue
            file_path = op.join(root, file_name)
            file_name = file_name[:-3]
            if h5py.is_hdf5(file_path):
                if not grp:
                    log.info("createTocFile - create_group: " + grp_path)
                    grp = f.create_group(grp_path)
                domain_path = fileUtil.getDomain(file_path)
                # verify that we can convert the domain back to a file path
                try:
                    fileUtil.getFilePath(domain_path)
                    # ok - add the external link
                    log.info("createTocFile - ExternalLink: " + domain_path)
                    grp[file_name] = h5py.ExternalLink(domain_path, "/")
                except HTTPError:
                    log.info(
                        "file path: [" + file_path +
                        "] is not valid dns name, ignoring")
