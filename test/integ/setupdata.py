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
import sys
import os
import stat
from shutil import copyfile
import h5py
import numpy as np

SRC = "../test_files"
DES = "../../data/test"

# files to be copied into test directory
testfiles = {
    'tall.h5': ('.',  'tall_updated.h5', 'tall_ro.h5', 'tall_g2_deleted.h5', 
            'tall_dset112_deleted.h5', 'tall_dset22_deleted.h5', 'tall_acl.h5', 
            'tall_acl_delete.h5', 'tall.dots.need.to.be.encoded.h5', 'subdir/tall.h5'),
    'tall_with_udlink.h5': ('.',),
    'scalar.h5': ('.', 'scalar_1d_deleted.h5',),
    'namedtype.h5': ('.', 'namedtype_deleted.h5'),
    'resizable.h5': ('.', 'resized.h5'),
    'notahdf5file.h5': ('.',),
    'zerodim.h5': ('filename with space.h5', 'deleteme.h5', 'readonly.h5', 'subdir',
    'subdir/deleteme.h5', 'subdir/subdir/deleteme.h5'),
    'group1k.h5': ('.', 'group1k_updated.h5'),
    'attr1k.h5': ('.',),
    'type1k.h5': ('.',),
    'dset1k.h5': ('.',),
    'fillvalue.h5': ('.'),
    'null_space_dset.h5': ('.'),
    'compound.h5': ('.',),
    'compound_attr.h5': ('.',),
    'compound_array_attr.h5': ('.',),
    'compound_array_dset.h5': ('.',),
    'compound_committed.h5': ('.',),
    'arraytype.h5': ('.',),
    'array_attr.h5': ('.',),
    'array_dset.h5': ('.',),
    'bitfield_attr.h5': ('.',),
    'bitfield_dset.h5': ('.',),
    'dim_scale.h5': ('.',),
    'dim_scale_data.h5': ('.', 'dim_scale_updated.h5'),
    'dset_gzip.h5': ('.',),
    'enum_attr.h5': ('.',),
    'enum_dset.h5': ('.',),
    'fixed_string_attr.h5': ('.',),
    'fixed_string_dset.h5': ('.',),
    'h5ex_d_alloc.h5': ('.',),
    'h5ex_d_checksum.h5': ('.',),
    'h5ex_d_chunk.h5': ('.',),
    'h5ex_d_compact.h5': ('.',),
    'h5ex_d_extern.h5': ('.',),
    'h5ex_d_fillval.h5': ('.',),
    'h5ex_d_gzip.h5': ('.',),
    'h5ex_d_hyper.h5': ('.',),
    'h5ex_d_nbit.h5': ('.',),
    'h5ex_d_rdwr.h5': ('.',),
    'h5ex_d_shuffle.h5': ('.',),
    'h5ex_d_sofloat.h5': ('.',),
    'h5ex_d_soint.h5': ('.',),
    'h5ex_d_transform.h5': ('.',),
    'h5ex_d_unlimadd.h5': ('.',),
    'h5ex_d_unlimgzip.h5': ('.',),
    'h5ex_d_hyper.h5': ('.',),
    'link_example.h5': ('.',),
    'objref_attr.h5': ('.',),
    'objref_dset.h5': ('.', 'objref_dset_updated.h5'),
    'null_objref_dset.h5': ('.',),
    'regionref_attr.h5': ('.',),
    'regionref_dset.h5': ('.', 'regionref_dset_updated.h5'),    
    'vlen_attr.h5': ('.',),
    'vlen_dset.h5': ('.',),
    'vlen_string_attr.h5': ('.',),
    'vlen_string_dset.h5': ('.',),
    'opaque_attr.h5': ('.',),
    'opaque_dset.h5': ('.',),
    'committed_type.h5': ('.',),
    'tstr.h5': ('.',),
    'null_space_attr.h5': ('.',),
    'bool_dset.h5': ('.',),
    'bool_attr.h5': ('.',)
}

# files that will get set as read-only
read_only_files = ( 'tall_ro.h5', 'readonly.h5')


"""
Create test accounts
 - add test_user1 and test_user2 if they don't exist already
"""


def addTestAccount(user_id):
    password_file = "passwd.h5" 
    cwd = os.getcwd()
    src_dir = os.path.abspath(SRC)
    os.chdir('../../util/admin')
    if not os.path.isfile(password_file):    
        os.system('python makepwd_file.py')
              
    add_user_script = 'python update_pwd.py' 
    add_user_script += ' -f ' + password_file  
    os.system(add_user_script + ' -a -u ' + user_id + ' -p test')
    home_dir = "../../data/home"
    
    
    if not os.path.isdir(home_dir):
        os.mkdir(home_dir)
    os.chdir(home_dir)
    
    # clean out any old files
    if os.path.isdir(user_id):
        removeFilesFromDir(user_id)
    else:
        # create user home directory   
        os.mkdir(user_id)
        
    os.chdir(user_id)
    
    print("cwd:", os.getcwd())
    # link to "public" directory
    # create symlink to public directory
    public_dir = "../../public"
    if os.name != 'nt':
        if not os.path.isdir(public_dir):
            print("create public dir")
            os.mkdir(public_dir)
        if not os.path.islink('public'):
            print("create symlink")
            os.symlink(public_dir, "public")
    copyfile(src_dir + '/tall.h5', 'tall.h5')
    copyfile(src_dir + '/tall.h5', 'tall_deleteme.h5') 
    
    os.chdir(cwd)
    
def addTestAccounts():
    for test_user in ('test_user1', 'test_user2'):
        addTestAccount(test_user)
    
    
    
"""
Make a testfile with 1000 sub-groups
"""
def makeGroup1k():
    file_path = SRC + "/group1k.h5"
    if os.path.exists(file_path):
        return # don't waste time re-creating
    print('makeGroup1k')
    f = h5py.File(file_path, "w")
    for i in range(1000):
        name = 'g{:04d}'.format(i)
        f.create_group(name)
    f.close()
 
"""
Make a testfile with 1000 attributes
"""
def makeAttr1k():
    file_path = SRC + "/attr1k.h5" 
    if os.path.exists(file_path):
        return # don't waste time re-creating  
    print('makeAttr1k()')
    f = h5py.File(file_path, "w")
    for i in range(1000):
        name = 'a{:04d}'.format(i)
        f.attrs[name] = "this is attribute: " + str(i)
    f.close()
    
"""
Make a testfile with 1000 types
"""
def makeType1k():
    file_path = SRC + "/type1k.h5" 
    if os.path.exists(file_path):
        return # don't waste time re-creating  
    f = h5py.File(file_path, "w")
    for i in range(1000):
        name = 'S{:04d}'.format(i+1)
        f[name] = np.dtype(name)  #create fixed length string
    f.close()
    
"""
Make a testfile with 1000 datasets
"""
def makeDataset1k():
    file_path = SRC + "/dset1k.h5" 
    if os.path.exists(file_path):
        return # don't waste time re-creating  
    f = h5py.File(file_path, "w")
    for i in range(1000):
        name = 'd{:04d}'.format(i+1)
        dim = i+1
        f.create_dataset(name, (dim,), dtype=np.int32)
    f.close()

"""
Make a testfile with external links
"""
def makeExternalLinks():
    file_path = SRC + "/link_example.h5"
    if os.path.exists(file_path):
        return # don't waste time re-creating  
    tgt_link_path = os.path.abspath(DES)  # for absolute paths in link
    tgt_link_path += "/tall.h5"
    f = h5py.File(file_path, 'w')
    f.create_group('g1')
    f.create_group('g1/g1.1')
    f['soft_link'] = h5py.SoftLink('g1')
    f['external_link1'] = h5py.ExternalLink('tall.h5', 'g1/g1.1')
    f['external_link2'] = h5py.ExternalLink('tall', 'g1/g1.1')
    f['external_link3'] = h5py.ExternalLink('tall.test.hdfgroup.org', 'g1/g1.1')
    f['external_link4'] = h5py.ExternalLink(tgt_link_path, 'g1/g1.1')
    f['external_link5'] = h5py.ExternalLink('tall.subdir.test.hdfgroup.org', 'g1/g1.1')
    f['external_link6'] = h5py.ExternalLink('tall.subdir', 'g1/g1.1')
    f['external_link7'] = h5py.ExternalLink('subdir/tall.h5', 'g1/g1.1')
    f.close()


"""
Remove files from given directory
"""    
def removeFilesFromDir(dir_name):
    print('remove files', dir_name)
    if not os.path.isdir(dir_name):
        print("expected", dir_name, "to be a directory")
        sys.exit()
    for file_name in os.listdir(dir_name):
        file_path = os.path.join(dir_name, file_name)
        try:
            if os.path.isdir(file_path):
                if os.path.islink(file_path):
                    os.unlink(file_path)  # just remove the link
                else:
                    removeFilesFromDir(file_path)
                    os.rmdir(file_path)
            else:
                if os.path.isfile(file_path):
                    # check for read-only
                    if (os.stat(file_path).st_mode & stat.S_IWUSR) == 0:
                        # make read-write
                        os.chmod(file_path, 0O666)
                    os.unlink(file_path)
        except Exception as e:
            print(e)
    
"""
main
"""
# verify we are in the right place and the correct argument has been passed
if len(sys.argv) > 1 and sys.argv[1] == '-h':
    print("this script will remove all files from ../../data/test and repopulate using files from ../../testdata")
    sys.exit(); 
    
if not os.path.exists(SRC):
    print("run this from the integ test directory!")
    sys.exit()
    
if not  os.path.exists(DES):
    # create the data/test directory if it doesn't exist
    os.mkdir(DES)
   
   
# create test accounts
addTestAccounts()
    
# create group1k.h5 (if not created before)
makeGroup1k()

# create attr1k.h5 (if not created before)
makeAttr1k()

# create type1k.h5 (if not created before)
makeType1k()

# create dset1k.h5 (if not created before)
makeDataset1k()

# create link_example.h5 (if not created before))
makeExternalLinks()

removeFilesFromDir(DES)


test_dirs = ('.', 'subdir', 'subdir/subdir')
for dir_name in test_dirs:
    tgt_dir = DES
    if dir_name != '.':
        tgt_dir += '/' + dir_name
    if not os.path.exists(tgt_dir):
        os.mkdir(tgt_dir)
  
for file_name in testfiles:
    for tgt in testfiles[file_name]:
        src = SRC + '/' + file_name
        des = DES + '/'
        if tgt == '.':
            # copy to DES
            des += file_name
        else:
            des += tgt
            if os.path.isdir(des):
                # copy to directory
                des += '/'
                des += file_name
            
        print('copyfile("'+file_name+'", "'+des+'")')  
        copyfile(src, des) 
        
for file_name in read_only_files:
    file_path = DES + '/' + file_name
    print('chmod', file_path)
    os.chmod(file_path, 0O444)

    



