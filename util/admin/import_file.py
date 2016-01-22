import h5py
import numpy as np
import sys
import argparse
import os.path as op
import os
import shutil
from h5json import Hdf5db
import config

"""
Get domain for given file path
"""
def getDomain(file_path, base_domain=None):
    # Get domain given a file path
    
    data_path = op.normpath(config.get('datapath'))  # base path for data directory
    file_path = op.normpath(file_path)
    hdf5_ext = config.get("hdf5_ext")
    if op.isabs(file_path):
        # compare with absolute path if we're given an absolute path
        data_path = op.abspath(data_path)
    
    if file_path == data_path:
        return config.get('domain')
            
    if file_path.endswith(hdf5_ext):
        domain = op.basename(file_path)[:-(len(hdf5_ext))]
    else:
        domain = op.basename(file_path)

    dirname = op.dirname(file_path)
    
    while len(dirname) > 1 and dirname != data_path:
        domain += '.'
        domain += op.basename(dirname)
        dirname = op.dirname(dirname)
     
    domain += '.'
    if base_domain:
        domain += base_domain
    else:
        domain += config.get('domain')

    return domain

"""
 Create directories as needed along the given path.
"""
def makeDirs(filePath):
    print("makeDirs:", filePath)
    # Make any directories along path as needed
    if len(filePath) == 0 or op.isdir(filePath):
        return
    dirname = op.dirname(filePath)

    if len(dirname) >= len(filePath):
        return
    makeDirs(dirname)  # recursive call
    os.mkdir(filePath)  # should succeed since parent directory is created
    
"""
 Get userid given username.
 If user_name is not found, return None
"""
def getUserId(user_name, password_file):
    """
      getUserInfo: return user data
    """
      
    userid = None

    if not user_name:
        return None

    # verify file exists and is writable
    if not op.isfile(password_file):
        print("password file not found")
        raise None

    with h5py.File(password_file, 'r') as f:
        if user_name not in f.attrs:
            return None

        data = f.attrs[user_name]
        #print(data)
        return data['userid']

"""
get group uuid of hardlink, or None if no link
"""
def getSubgroupId(db, group_uuid, link_name):
    print("link_name:", link_name)    
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

def addTocEntry(toc_file, file_path, domain):
        """
        Helper method - update TOC when a domain is created
          If validateOnly is true, then the acl is checked to verify that create is
          enabled, but doesn't update the .toc
        """
         
        print("addTocEntry, filePath", file_path, "domain:", domain) 
        hdf5_ext = config.get('hdf5_ext')

        try:
            with Hdf5db(toc_file) as db:
                group_uuid = db.getUUIDByPath('/')
                pathNames = file_path.split('/')
                for linkName in pathNames:
                    if not linkName:
                        continue
                    if linkName.endswith(hdf5_ext):
                        linkName = linkName[:-(len(hdf5_ext))]
                        db.createExternalLink(group_uuid, domain, '/', linkName)
                    else:
                        subgroup_uuid = getSubgroupId(db, group_uuid, linkName)
                        if subgroup_uuid is None:
                            # create subgroup and link to parent group
                            subgroup_uuid = db.createGroup()
                            # link the new group
                            db.linkObject(group_uuid, subgroup_uuid, linkName)
                        group_uuid = subgroup_uuid

        except IOError as e:
            print("IOError: " + str(e.errno) + " " + e.strerror)
            sys.exit(-1)
            
"""
main method
"""
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', "--src", help="source path for the file to be imported")
    parser.add_argument('-u', "--user", help="user name")
    parser.add_argument('-f', "--folder", help='folder path under user home dir (optional)')
    parser.add_argument('-p', "--passwd_file", help='password file (optional)')
     
      
    args = parser.parse_args()
       
    src_path = None
    username = None
    folder = None
    password_file = None
    
    if args.src:
        src_path = args.src
    else:
        print("no source file provided")
        return -1
    if not op.isfile(src_path):
        print("no file found")
        return -1
    if not h5py.is_hdf5(src_path):
        print("file must be an HDF5 file")
        
    if args.user:
        username = args.user
    else:
        print("no user provided")
        return -1
                             
    if args.passwd_file:
        password_file = args.passwd_file
    else:
        password_file = config.get("password_file")
        
    if args.folder:
        folder = args.folder
        if op.isabs(folder):
            print("folder path must be relative")
            return -1
        folder = op.normpath(folder)
    
            
    print(">source:", src_path)
    print(">username:", username)
    print(">password_file:", password_file)
    print(">folder:", folder)  
    
    userid = getUserId(username, password_file)
    
    if not userid:
        print("user not found")
        return -1
    print(">userid:", userid)
    
    tgt_dir = op.join(op.dirname(__file__), config.get("datapath"))
    tgt_dir = op.normpath(tgt_dir)
    tgt_dir = op.join(tgt_dir, config.get("home_dir"))
    tgt_dir = op.join(tgt_dir, username)
    toc_file = op.join(tgt_dir, config.get("toc_name"))
    if not op.isfile(toc_file):
        print("toc_file:", toc_file, "not found")
        return -1
    if folder:
        tgt_dir = op.join(tgt_dir, folder)
     
    if not op.isdir(tgt_dir):
        print("directory:", tgt_dir, "not found, creating")
        makeDirs(tgt_dir)
        
    tgt_file = op.join(tgt_dir, op.basename(src_path))
    
    if folder:
        tgt_path = folder
    else:    
        tgt_path = "/"
        
    tgt_path = op.join(tgt_path, op.basename(src_path))
     
    if op.isfile(tgt_file):
        print("file already exists")
        return -1
    
    base_domain = config.get("domain")
    base_domain = username + '.' + config.get("home_dir") + '.' + config.get("domain")
    domain = getDomain(tgt_path, base_domain=base_domain)
   
    # add toc entry
    addTocEntry(toc_file, tgt_path, domain)    
    # copy file
    shutil.copyfile(src_path, tgt_file) 
    
    return 0
        

main()