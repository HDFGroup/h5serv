import h5py
import numpy as np
import sys
import argparse
import os.path as op
import shutil
from h5json import Hdf5db
import config

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
        log.error("password file not found")
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

def addTocEntry(toc_file, filePath):
        """
        Helper method - update TOC when a domain is created
          If validateOnly is true, then the acl is checked to verify that create is
          enabled, but doesn't update the .toc
        """
         
        print("addTocEntry, filePath", filePath) 
        hdf5_ext = config.get('hdf5_ext')

        try:
            with Hdf5db(toc_file) as db:
                group_uuid = db.getUUIDByPath('/')
                pathNames = filePath.split('/')
                for linkName in pathNames:
                    print("linkName:", linkName)
                    if not linkName:
                        continue
                    if linkName.endswith(hdf5_ext):
                        linkName = linkName[:-(len(hdf5_ext))]
                        db.createExternalLink(group_uuid, filePath, '/', linkName)
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
    parser.add_argument('-p', "--passwd", help='password file (optional)')
     
      
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
                             
    if args.passwd:
        password_file = args.passwd
    else:
        password_file = config.get("password_file")
        
    if args.folder:
        folder = args.folder
        if not op.isabs(folder):
            print("folder path must be relative")
            return -1
    
            
    print(">source:", src_path)
    print(">username:", username)
    print(">password_file:", password_file)
    print(">folder:", folder)
    
    userid = getUserId(username, password_file)
    print("userid:", userid)
    if not userid:
        print("user not found")
        return -1
    
    tgt_dir = op.join(op.dirname(__file__), config.get("datapath"))
    tgt_dir = op.join(tgt_dir, config.get("home_dir"))
    tgt_dir = op.join(tgt_dir, username)
    toc_file = op.join(tgt_dir, config.get("toc_name"))
    if not op.isfile(toc_file):
        print("toc_file:", toc_file, "not found")
        return -1
    if folder:
        tgt_dir = op.join(tgt_dir, folder)
     
    if not op.isdir(tgt_dir):
        print("directory:", tgt_dir, "not found")
        return -1
        
    tgt_file = op.join(tgt_dir, op.basename(src_path))
    
    if folder:
        tgt_path = folder
    else:    
        tgt_path = "/"
        
    tgt_path = op.join(tgt_path, op.basename(src_path))
     
    if op.isfile(tgt_file):
        print("file already exists")
        return -1
        
    # add toc entry
    addTocEntry(toc_file, tgt_path)    
    # copy file
    shutil.copyfile(src_path, tgt_file) 
    
    return 0
        

main()