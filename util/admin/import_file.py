import h5py
import numpy as np
import sys
import argparse
import os.path as op
import os
import shutil
from tornado.escape import url_escape
from h5json import Hdf5db
import config
 

"""
 Create directories as needed along the given path.
"""
def makeDirs(filePath):
    #print("makeDirs:", filePath)
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

def addTocEntry(toc_file, domain, base_domain):
    """
    Helper method - update TOC when a domain is created
    """
         
    if not domain.endswith(base_domain):
        sys.exit("unexpected domain value: " + domain)
    # trim domain by base domain

    try:
        with Hdf5db(toc_file) as db:
            group_uuid = db.getUUIDByPath('/')
            names = domain.split('.')
            base_names = base_domain.split('.')
            indexes = list(range(len(names)))
            indexes = indexes[::-1] # reverse
            for i in indexes:
                if i >= len(names) - len(base_names):
                    continue # still in the base domain
                linkName = names[i]
                if not linkName:
                    continue
                if i == 0:
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
    parser.add_argument('-u', "--user", help="user name (optional)")
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
        print("Importing into public")
                             
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
    
    hdf5_ext = config.get("hdf5_ext")
    
    if username:
        userid = getUserId(username, password_file)
    
        if not userid:
            print("user not found")
            return -1
    
    tgt_dir = op.join(op.dirname(__file__), config.get("datapath"))
    tgt_dir = op.normpath(tgt_dir)
    
    if username:
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
    
    tgt_file = op.basename(src_path)
    tgt_file = op.splitext(tgt_file)[0] # ignore the extension
    tgt_file = url_escape(tgt_file)  # make the filename url compatible
    tgt_file = tgt_file.replace('.', '_')  # replace dots with underscores
       
    tgt_path = op.join(tgt_dir, tgt_file)
    tgt_path = op.normpath(tgt_path)
        
    if op.isfile(tgt_path + hdf5_ext):
        print("file already exists")
        return -1
    
    # determine target domain
    domain = tgt_file
    if folder:
        domain += '.' + folder
    if username:
        domain += '.' + username + '.' + config.get("home_dir")
    domain += "." + config.get("domain") 
    
    # determine the base so that the toc update can be done relative to the base.
    if username:
        base_domain = username + '.' + config.get("home_dir") + '.' + config.get("domain")
    else:
        base_domain = config.get("domain")
    
     
    print("domain:", domain)
    # add toc entry
    addTocEntry(toc_file, domain, base_domain)    
    # copy file
    tgt_path += hdf5_ext
    shutil.copyfile(src_path, tgt_path) 
    
    return 0
        

main()