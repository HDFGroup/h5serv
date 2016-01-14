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
import re
from tornado.web import HTTPError
import logging

import h5py
import config
import fileUtil

"""
 TOC (Table of contents) util helper functions
 Creates a directory listing in the form of an HDF5 file
"""


def getTocFilePath(user=None):
    datapath = config.get('datapath')
    if user is None:
        #print("get default toc")
        toc_file_path = op.join(datapath, config.get('toc_name'))
    else:
        #print("get user toc")
        toc_file_path = op.join(datapath, config.get('home_dir'))
        toc_file_path = op.join(toc_file_path, config.get('toc_name'))
 
    return toc_file_path


def isTocFilePath(filePath):
    datapath = config.get('datapath')
    toc_file_path = op.join(datapath, config.get('toc_name'))
    if filePath == toc_file_path:
        isTocFilePath = True
    else:
        isTocFilePath = False
    return isTocFilePath


def createTocFile(datapath):
    log = logging.getLogger("h5serv")
    log.info("createTocFile(" + datapath + ")")
    
    if datapath.endswith(config.get('toc_name')):
        toc_dir = op.dirname(datapath)
        toc_file = datapath
    else:
        toc_dir = datapath
        toc_file = op.join(toc_dir, config.get("toc_name"))
     
    log.info("check toc with path: " + toc_file)    
    if op.exists(toc_file):
        msg = "toc file already exists"
        log.warn(msg)
        raise IOError(msg)
        
    base_domain = fileUtil.getDomain(toc_dir)
    log.info("base domain: " + base_domain)
    
    #if os.name == 'nt':
    #    toc_dir = toc_dir.replace('\\', '/')  # use unix style to map to HDF5 convention
    
    hdf5_ext = config.get('hdf5_ext')  
    folder_regex = config.get('toc_folder_filter')
    
    f = h5py.File(toc_file, 'w')
     
    for root, subdirs, files in os.walk(toc_dir):
        #print("files: ", files)
        log.info( "root: " + root)
        if folder_regex and re.match(folder_regex, op.basename(root)):
            log.info("skipping director (filter match)")
            continue
        grppath = root[len(toc_dir):]
        if not grppath:
            grppath = '/'
        if grppath[-1] == '.':
            grppath = grppath[:-1]
        log.info("grppath: " + grppath)
         
        if os.name == 'nt':
            grppath = grppath.replace('\\', '/')  # match HDF5 convention
        grp = None
        if grppath == '/':
            grp = f['/']  # use root group
         
        domainpath = fileUtil.getDomain(grppath, base_domain=base_domain)
        log.info("grppath: " + grppath)
        log.info("base_domain: " + base_domain)
        log.info("domainpath: " + domainpath)
        for filename in os.listdir(root):
            log.info("walk, file: " + filename)
            if filename[0] == '.':
                log.info("skip hidden")
                continue  # skip 'hidden' files
            
            filepath = op.join(root, filename)
            if os.name == 'nt':
                filepath = filepath.replace('\\', '/')  # use unix style to map to HDF5 convention
            log.info("createTocFile, path: " + filepath)
            link_target = '/'
            
            if op.islink(filepath):
                log.info("symlink: " + filepath)
                # todo - quick hack for now to set a symlink with to sub-folder of data dir
                # todo - revamp to use os.readlink and do the proper thing with the link value
                filedomain = config.get('domain')
                link_target += filename
                log.info("setting symbolic link domainpath to: " + filedomain, " target: /" + filename)
            else:
                if len(filename) < 4 or filename[-3:] != hdf5_ext:
                    log.info("skip non-hdf5 extension")
                    continue
                if not h5py.is_hdf5(filepath):
                    log.info("skip non-hdf5 file")
                    continue
                filename = filename[:-(len(hdf5_ext))]
                log.info("filename (noext): " + filename)
                if domainpath[0] == '.':        
                    filedomain = filename + domainpath
                else:
                    filedomain = filename + '.' + domainpath
                    
            # create the grp at grppath if it doesn't exist
            if not grp:
                log.info("createTocFile - create_group: " + grppath)
                grp = f.create_group(grppath)           
                
            # verify that we can convert the domain back to a file path
            log.info("filedomain: " + filedomain)
            try:
                fileUtil.getFilePath(filedomain)
                # ok - add the external link
                log.info("createTocFile - ExternalLink: " + domainpath)
                grp[filename] = h5py.ExternalLink(filedomain, link_target)
            except HTTPError:
                log.info("file path: [" + filepath + "] is not valid dns name, ignoring")
