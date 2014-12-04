#!/bin/sh 
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
#todo - verify that current directory is the same as the script
if [ $# -ne 1 ] || [ $1 != '-f' ]
then
    echo "this will remove all files from ../../data and repopulate using files from ../../testdata!  run with -f to proceed"
    exit 1
fi
export SRC="../../testfiles"
export DES="../../data/test"
if [ ! -d $DES ]
then
    mkdir $DES
fi
rm -rf $DES/*
if [ -f $DES/.*.h5 ]
then
    rm $DES/.*.h5
fi
mkdir $DES/subdir
mkdir $DES/subdir/subsubdir
if [ ! -f $SRC/group1k.h5 ]
then
    echo "creating group1k.h5"
    python makegroups.py  # creates 'group1k.h5'
    mv group1k.h5 $SRC
fi
if [ ! -f $SRC/attr1k.h5 ]
then
    echo "creating attr1k.h5"
    python makeattr.py  # creates 'attr1k.h5'
    mv attr1k.h5 $SRC
fi
cp $SRC/tall.h5 $DES
cp $SRC/tall.h5 $DES/tall_ro.h5
cp $SRC/tall.h5 $DES/tall_updated.h5
cp $SRC/tall.h5 $DES/tall_g2_deleted.h5
cp $SRC/tall.h5 $DES/tall_dset112_deleted.h5
cp $SRC/tall.h5 $DES/tall_dset22_deleted.h5
cp $SRC/tall_with_udlink.h5 $DES
cp $SRC/scalar.h5 $DES/scalar_1d_deleted.h5
cp $SRC/namedtype.h5 $DES
cp $SRC/namedtype.h5 $DES/namedtype_deleted.h5
cp $SRC/resizable.h5 $DES
cp $SRC/resizable.h5 $DES/resized.h5
cp $SRC/notahdf5file.h5 $DES
cp $SRC/zerodim.h5 $DES/"filename with space.h5"
cp $SRC/zerodim.h5 $DES/subdir
cp $SRC/zerodim.h5 $DES/subdir/subsubdir
cp $SRC/zerodim.h5 $DES/deleteme.h5
cp $SRC/zerodim.h5 $DES/subdir/deleteme.h5
cp $SRC/zerodim.h5 $DES/readonly.h5
cp $SRC/group1k.h5 $DES
cp $SRC/group1k.h5 $DES/group1k_updated.h5
cp $SRC/attr1k.h5 $DES
cp $SRC/fillvalue.h5 $DES
cp $SRC/scalar.h5 $DES
cp $SRC/null_space_dset.h5 $DES
chmod -w $DES/tall_ro.h5
chmod -w $DES/readonly.h5
cp $SRC/compound.h5 $DES
cp $SRC/compound_attr.h5 $DES
cp $SRC/arraytype.h5 $DES
# from hdf5 lib examples...
cp $SRC/array_attr.h5 $DES
cp $SRC/array_dset.h5 $DES
cp $SRC/bitfield_attr.h5 $DES
cp $SRC/bitfield_dset.h5 $DES 
cp $SRC/enum_dset.h5 $DES 
cp $SRC/enum_attr.h5 $DES 
cp $SRC/fixed_string_dset.h5 $DES 
cp $SRC/fixed_string_attr.h5 $DES 
cp $SRC/objref_dset.h5 $DES 
cp $SRC/objref_attr.h5 $DES 
cp $SRC/regionref_dset.h5 $DES
cp $SRC/regionref_attr.h5 $DES
cp $SRC/vlen_dset.h5 $DES
cp $SRC/vlen_attr.h5 $DES
cp $SRC/vlen_string_dset.h5 $DES
cp $SRC/vlen_string_attr.h5 $DES
cp $SRC/opaque_dset.h5 $DES
cp $SRC/opaque_attr.h5 $DES
cp $SRC/null_objref_dset.h5 $DES
cp $SRC/committed_type.h5 $DES


