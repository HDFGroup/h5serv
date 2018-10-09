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
import h5serv.config as config
import h5serv.fileUtil as fileUtil
from h5json import Hdf5db

"""
 TOC (Table of contents) util helper functions
 Creates a directory listing in the form of an HDF5 file
"""


def getTocFilePath(user=None):
    datapath = config.get('datapath')
    if user is None:
        #print("get default toc")
        toc_file_path = fileUtil.join(datapath, config.get('toc_name'))
    else:
        #print("get user toc")
        toc_file_path = fileUtil.join(datapath, config.get('home_dir'))
        toc_file_path = fileUtil.join(toc_file_path, config.get('toc_name'))
 
    return toc_file_path


def isTocFilePath(filePath):
    datapath = config.get('datapath')
    toc_file_path = fileUtil.join(datapath, config.get('toc_name'))
    if filePath == toc_file_path:
        isTocFilePath = True
    else:
        isTocFilePath = False
    return isTocFilePath
    
    

"""
helper - get group uuid of hardlink, or None if no link
"""
def getSubgroupId(db, group_uuid, link_name):
    #print("link_name:", link_name)    
    subgroup_uuid = None
    try:
        item = db.getLinkItemByUuid(group_uuid, link_name)
        if item['class'] != 'H5L_TYPE_HARD':
            return None
        if item['collection'] != 'groups':
            return None
        subgroup_uuid = item['id']
    except IOError:
        # link_name doesn't exist, return None
        pass

    return subgroup_uuid
        
"""
Update toc with new filename
"""
def addTocEntry(domain, filePath,  userid=None):
    """
    Helper method - update TOC when a domain is created
    If userid is provide, the acl will be checked to ensure userid has permissions
    to modify the object.
    """
    log = logging.getLogger("h5serv")
    hdf5_ext = config.get('hdf5_ext')
    dataPath = config.get('datapath')
    log.info("addTocEntry - domain: " + domain + " filePath: " + filePath)
    if not filePath.startswith(dataPath):
        log.error("unexpected filepath: " + filePath)
        raise HTTPError(500)
    filePath = fileUtil.getUserFilePath(filePath)   
    tocFile = fileUtil.getTocFilePathForDomain(domain)
    log.info("tocFile: " + tocFile)
    acl = None

    try:         
        with Hdf5db(tocFile, app_logger=log) as db:
            group_uuid = db.getUUIDByPath('/')
            pathNames = filePath.split('/')
            for linkName in pathNames:
                if not linkName:
                    continue
                if linkName.endswith(hdf5_ext):
                    linkName = linkName[:-(len(hdf5_ext))]
                    print("linkName:", linkName)
                    if userid is not None:
                        acl = db.getAcl(group_uuid, userid)
                        if not acl['create']:
                            self.log.info("unauthorized access to group:" + group_uuid)
                            raise IOError(errno.EACCES)  # unauthorized
                    log.info("createExternalLink -- uuid %s, domain: %s, linkName: %s", group_uuid, domain, linkName)
                    db.createExternalLink(group_uuid, domain, '/', linkName)
                else:
                    subgroup_uuid = getSubgroupId(db, group_uuid, linkName)
                    if subgroup_uuid is None:
                        if userid is not None:
                            acl = db.getAcl(group_uuid, userid)
                            if not acl['create']:
                                self.log.info("unauthorized access to group:" + group_uuid)
                                raise IOError(errno.EACCES)  # unauthorized
                        # create subgroup and link to parent group
                        subgroup_uuid = db.createGroup()
                        # link the new group
                        log.info("linkObject -- uuid: %s, subgroup_uuid: %s, linkName: %s", group_uuid, subgroup_uuid, linkName)
                        db.linkObject(group_uuid, subgroup_uuid, linkName)
                    group_uuid = subgroup_uuid 

    except IOError as e:
        log.info("IOError: " + str(e.errno) + " " + e.strerror)
        raise e

"""
Helper method - update TOC when a domain is deleted
"""
def removeTocEntry(domain, filePath, userid=None):
    log = logging.getLogger("h5serv")
    hdf5_ext = config.get('hdf5_ext')
    dataPath = config.get('datapath')

    if not filePath.startswith(dataPath):
        log.error("unexpected filepath: " + filePath)
        raise HTTPError(500)
    filePath = fileUtil.getUserFilePath(filePath)   
    tocFile = fileUtil.getTocFilePathForDomain(domain)
    log.info("removeTocEntry - domain: " + domain + " filePath: " + filePath + " tocfile: " + tocFile)
    pathNames = filePath.split('/')
    log.info("pathNames: " + str(pathNames))

    try:
        with Hdf5db(tocFile, app_logger=log) as db:
            group_uuid = db.getUUIDByPath('/')
            log.info("group_uuid:" + group_uuid)
                           
            for linkName in pathNames:
                if not linkName:
                    continue
                log.info("linkName:" + linkName)
                if linkName.endswith(hdf5_ext):
                    linkName = linkName[:-(len(hdf5_ext))]
                    log.info("unklink " + group_uuid + ", " + linkName)
                    db.unlinkItem(group_uuid, linkName)
                else:
                    subgroup_uuid = getSubgroupId(db, group_uuid, linkName)
                    if subgroup_uuid is None:
                        msg = "Didn't find expected subgroup: " + group_uuid
                        log.error(msg)
                        raise HTTPError(500, reason=msg)
                    group_uuid = subgroup_uuid

    except IOError as e:
        log.info("IOError: " + str(e.errno) + " " + e.strerror)
        raise e

"""
Create a populate TOC file if not present
"""            
def createTocFile(datapath):
    log = logging.getLogger("h5serv")
    log.info("createTocFile(" + datapath + ")")
    data_dir = fileUtil.posixpath(op.normpath(config.get('datapath')))
    home_dir = fileUtil.join(data_dir, config.get("home_dir"))
    log.info("home dir: " + home_dir)
    if datapath.startswith(home_dir):
        log.info("user toc")
        user_toc = True
    else:
        log.info("system toc")
        user_toc = False
    
    if datapath.endswith(config.get('toc_name')):
        toc_dir = fileUtil.posixpath(op.normpath(op.dirname(datapath)))
        toc_file = datapath
    else:
        toc_dir = fileUtil.posixpath(op.normpath(datapath))
        toc_file = fileUtil.join(toc_dir, config.get("toc_name"))
   
           
    log.info("toc_dir:[" + toc_dir + "]")
    log.info("data_dir:[" + data_dir + "]") 
    log.info("home_dir:[" + home_dir + "]")
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
    
    f = h5py.File(toc_file, 'w')
     
    for root, subdirs, files in os.walk(toc_dir):
        root = fileUtil.posixpath(root)
        log.info( "toc walk: " + root)
        
        if toc_dir == data_dir:
            log.info(fileUtil.join(toc_dir, home_dir))
            if root.startswith(home_dir):
                log.info("skipping home dir")
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
            
            filepath = fileUtil.join(root, filename)
            log.info("walk, filepath: " + filepath)
            link_target = '/'
            
            if op.islink(filepath):
                log.info("symlink: " + filepath)
                # todo - quick hack for now to set a symlink with to sub-folder of data dir
                # todo - revamp to use os.readlink and do the proper thing with the link value
                filedomain = config.get('domain')
                link_target += filename
                log.info("setting symbolic link domainpath to: " + filedomain + " target: /" + filename)
            else:
                ext_len = len(hdf5_ext)
                if len(filename) < ext_len or filename[-ext_len:] != hdf5_ext:
                    log.info("skip non-hdf5 extension")
                    continue
                if not h5py.is_hdf5(filepath):
                    log.info("skip non-hdf5 file")
                    continue
                filename = filename[:-ext_len]
                # replace any dots with '%2E' to disambiguate from domain seperators
                filename_encoded = filename.replace('.', '%2E')
                log.info("filename (noext): " + filename)
                if domainpath[0] == '.':        
                    filedomain = filename_encoded + domainpath
                else:
                    filedomain = filename_encoded + '.' + domainpath
                    
            # create the grp at grppath if it doesn't exist
            if not grp:
                log.info("tocfile - create_group: " + grppath)
                grp = f.create_group(grppath)           
                
            # verify that we can convert the domain back to a file path
            log.info("filedomain: " + filedomain)
            try:
                fileUtil.getFilePath(filedomain)
                # ok - add the external link
                log.info("tocFile - ExternalLink: " + domainpath)
                grp[filename] = h5py.ExternalLink(filedomain, link_target)
            except HTTPError:
                log.info("file path: [" + filepath + "] is not valid dns name, ignoring")
