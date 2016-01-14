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
import h5py
import sys

def dumpAttr(col):
    for k in col.attrs:
        attr = col.attrs[k]
        
        if attr.__class__.__name__ == 'Reference':
            obj = col[attr]
            print('\t\tattr[' + k + ']: ->' + obj.name)
        else:
            print('\t\tattr[' + k + ']: ' + str(attr))  # path
        
def dumpCol(col):   
    if len(col) == 0:
        pass # return  # skip
    npos = col.name.rfind('/') + 1
    name = col.name[npos:]
    print('\t{' + name + '}')
    dumpAttr(col)
    for uuid in col:
        g = col[uuid]
        addr = h5py.h5o.get_info(g.id).addr
        print('\t\t' + uuid + ': ' + g.__class__.__name__ + ' addr: ' + str(addr))
    
def dumpFile(filePath):
    print("db info for: ", filePath)
    f = h5py.File(filePath, 'r')
    dbGrp = f['/']
    if '__db__'  in f:
        dbGrp = f['__db__']
    else:
        if '{groups}' not in f:
            print("no db data found!")
            return
    print('__db__', 'Group')
    dumpAttr(dbGrp)
    dumpCol(dbGrp['{groups}'])
    dumpCol(dbGrp['{datasets}'])
    dumpCol(dbGrp['{datatypes}'])
    dumpCol(dbGrp['{addr}'])
    
    f.close()

def main():
    if len(sys.argv) < 1:
        print("usage: dumpobjdb <filename>")
        sys.exit(); 
        
    dumpFile(sys.argv[1])
     

main()

    
	
