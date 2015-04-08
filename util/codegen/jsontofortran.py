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
import json
import argparse
import logging
import logging.handlers

# logging global object
log = None
indent = "   " # three char indent for output source

#------------------------------------------------------------------------------
#
#  Get Fortran native type for given hdf5 type
#
#------------------------------------------------------------------------------
def getFortranType(hdf5TypeName):
    log.info("getFortranType")
    predefined_int_types = {
          'H5T_STD_I8':  'INTEGER(KIND=1)', 
          'H5T_STD_U8':  '',  # unsigned int types not supported for fortran
          'H5T_STD_I16': 'INTEGER(KIND=2)', 
          'H5T_STD_U16': '',
          'H5T_STD_I32': 'INTEGER(KIND=4)', 
          'H5T_STD_U32': '',
          'H5T_STD_I64': 'INTEGER(KIND=8)',
          'H5T_STD_U64': '' 
    }
    predefined_float_types = {
          'H5T_IEEE_F32': 'REAL(KIND=4)',
          'H5T_IEEE_F64': 'REAL(KIND=8)'
    }
    if len(hdf5TypeName) < 3:
        raise Exception("Type Error: invalid type")
     
    key = hdf5TypeName
    if hdf5TypeName.endswith('LE'):
        key = hdf5TypeName[:-2]
    elif hdf5TypeName.endswith('BE'):
        key = hdf5TypeName[:-2]
     
    fortranType = None   
    if key in predefined_int_types:
        fortranType = predefined_int_types[key]
    if key in predefined_float_types:
        fortranType = predefined_float_types[key]
    
    if not fortranType:
        raise TypeError("Type Error: invalid type")
    return fortranType
    
#------------------------------------------------------------------------------
#
#  Get HDF5 type identifier
#
#------------------------------------------------------------------------------     

def getBaseDataType(typeItem):
    log.info("getBaseDataType")
 
    if type(typeItem) == str or type(typeItem) == unicode:
        # should be one of the predefined types
        return typeItem
        
    if type(typeItem) != dict:
        raise TypeError("Type Error: invalid type")
              
    if 'class' not in typeItem:
        raise KeyError("'class' not provided")
    typeClass = typeItem['class']
    
    if 'shape' in typeItem:  
        raise TypeError("Array Types are not supported")        
        
    if typeClass == 'H5T_INTEGER':
        if 'base' not in typeItem:
            raise KeyError("'base' not provided")      
        return typeItem['base']
       
    elif typeClass == 'H5T_FLOAT':
        if 'base' not in typeItem:
            raise KeyError("'base' not provided")
        return typeItem['base'] 
   
        
    elif typeClass == 'H5T_STRING':
        if 'length' not in typeItem:
            raise KeyError("'strsize' not provided")
        if 'charSet' not in typeItem:
            raise KeyError("'charSet' not provided")          
            
        if typeItem['length'] == 'H5T_VARIABLE':
            raise TypeError("Variable String types are not supported")
       
        nStrSize = typeItem['length']
        if type(nStrSize) != int:
            raise TypeError("expecting integer value for 'length'")
        return "S" + str(nStrSize)
        # return "CHARACTER(LEN=" + str(nStrSize) + ")"
    elif typeClass == 'H5T_COMPOUND':
        raise TypeError("COMPOUND data type is not supported")
    elif typeClass == 'H5T_ENUM':
        raise TypeError("ENUM data type is not supported") 
    elif typeClass == 'H5T_VLEN':
        raise TypeError("VLEN data type is not supported")   
         
    elif typeClass == 'H5T_OPAQUE':
        raise TypeError("Opaque data type is not supported")
    elif typeClass == 'H5T_ARRAY':
        raise TypeError("Array data type is not supported")
    else:
        raise TypeError("Invalid type class")
           
       
    
 
#------------------------------------------------------------------------------
#
#  Flatten multi-dimensional list to a one-dim list
#
#------------------------------------------------------------------------------
def valueToListString(value):
   # fortran doesn't have a way to initialize multi-dimensional arrays, so
   # flaten array to 1d list
   text = ''
   nelements = len(value)
   line_len = 0
   for i in range(nelements):
       element = value[i]
       if type(element) in (list, tuple):
           next = valueToListString(element) # recursive call
           if i < nelements - 1:
               next += ', '   
           next += ' & \n'  # new line for every sub-array 
       else:
           next = str(element)
           if i < nelements - 1:
               next += ', '
           line_len += len(next)
           if line_len > 75:
               next += ' & \n'
               line_len = 0
       text += next; 
       
   return text

#------------------------------------------------------------------------------
#
#  Generate code to create attribute data array decleration
#
#------------------------------------------------------------------------------    
def doAttributeData(attr_json):  
    attr_name = attr_json["name"]
    log.info("doAttributeData: " + attr_name)
    attr_shape = attr_json["shape"]
    attr_type = attr_json["type"]
    base_type = getBaseDataType(attr_type)
    fortran_type = getFortranType(base_type)
    
    
    print "! attribute " + attr_name + " data declaration" 
    if attr_shape["class"] in ("H5S_NULL", "H5S_SCALAR"):
        print "! no decleration for null, scalar att"
    elif attr_shape["class"] == "H5S_SIMPLE":
        for_array_name = "attr_" + attr_name + "_array"
        dims = attr_shape["dims"]
    	rank = len(dims)
        num_elements = 1
        for i in range(rank):
            num_elements *= dims[i]
        # attribute dims code example:
        # INTEGER(hsize_t),   DIMENSION(1:2) :: dims = (/dim0, dim1/)
        for_dims = "   INTEGER(hsize_t),   DIMENSION(1:" + str(rank) + ") :: " + for_array_name + "_dims = (/"
        for i in range(rank):
            for_dims += str(dims[i])
            if i < rank - 1:
                for_dims += ", "
        for_dims += "/)"
        print for_dims
        # attribute data code example:
    	# INTEGER, DIMENSION(1:28), TARGET :: init_array = (/1,2,...,27,28/)
    	decl = indent + fortran_type + ", DIMENSION(1:" + str(num_elements) + "), "    
        decl += "TARGET :: attr_" + attr_name + "_array = (/&\n"
        decl += indent + valueToListString(attr_json["value"])
        decl += "/)"
        print decl
        
    else:
	raise TypeError("Invalid shape class")

#------------------------------------------------------------------------------
#
#  Generate code to create attribute object
#
#------------------------------------------------------------------------------
def doAttributeCreate(attr_json, parent_id):  
    attr_name = attr_json["name"]
    log.info("doAttributeCreate: " + attr_name)
    attr_shape = attr_json["shape"]
    attr_type = attr_json["type"]
    base_type = getBaseDataType(attr_type)
    
    print indent + "! attribute " + attr_name + " creation" 
    if attr_shape["class"] in ("H5S_NULL", "H5S_SCALAR"):
        print indent + "! no declaration for null, scalar att"
    elif attr_shape["class"] == "H5S_SIMPLE":
        for_array_name = "attr_" + attr_name + "_array"
        dims = attr_shape["dims"]
    
    	rank = len(dims)
        print indent + "f_ptr = C_LOC(" + for_array_name + "(1))"
        print indent + "call CreateAttribute('" + attr_name + "', " + parent_id + ", " + \
		str(rank) + ", " + for_array_name + "_dims, " + base_type + ", f_ptr, i_res)"
        
    else:
	raise TypeError("Invalid shape class")
    
#------------------------------------------------------------------------------
#
# Get alias name if present (otherwise return "???")
#
#------------------------------------------------------------------------------
def getObjectName(obj_json):
    name = "???"
    if "alias" in obj_json:
        alias = obj_json["alias"]
        if type(alias) in (list, tuple):
            if len(alias) > 0:
                name = alias[0]
        else:
            name = alias
    return name

#------------------------------------------------------------------------------
#
# convert a h5path to a legal fortran routine name
#
#------------------------------------------------------------------------------
def h5pathToSubroutineName(h5path):
  log.info("h5pathToSubroutineName: " + h5path)
  for_name = ''
  for ch in h5path:
      if ch.isalnum():
          for_name += ch
      else:
          for_name += '_'
  log.info("returning: " + for_name)
  return for_name

#------------------------------------------------------------------------------
#
# Generate attribute data declarations
#
#------------------------------------------------------------------------------
def doAttributesData(group_json):
    log.info("doAttributeData")
    if "attributes" not in group_json:
        return
    attrs_json = group_json["attributes"]
    
    for attr_json in attrs_json:
        doAttributeData(attr_json)

#------------------------------------------------------------------------------
#
# Process attributes in group
#
#------------------------------------------------------------------------------
def doAttributesCreate(group_json, parent_id):
    log.info("doAttributes - " + getObjectName(group_json))
    if "attributes" not in group_json:
        return
    attrs_json = group_json["attributes"]
    
    print "! creating attributes for '" + getObjectName(group_json) + "'"
    for attr_json in attrs_json:
        doAttributeCreate(attr_json, parent_id)
        

#------------------------------------------------------------------------------
#
# Generate group 
#
#------------------------------------------------------------------------------    
def doGroup(h5json, group_id, group_name, parent_id, h5path):
    log.info("doGroup h5path: " + h5path)
    subroutine_name = h5pathToSubroutineName("CreateGroup" + h5path )
    groups = h5json["groups"]
    group_json = groups[group_id]
    log.info("group name: " + group_name)
    newPath = h5path+"/"
    log.info("new path: " + newPath)
    print """
    
!
! Create Group {0}
!
!
SUBROUTINE {1}(group_name, parent_hid, i_res) 
USE HDF5
USE ISO_C_BINDING
IMPLICIT NONE
  character(len=*), intent(in) :: group_name
  INTEGER(HID_T), intent(in) :: parent_hid
  INTEGER, intent(out) :: i_res
  INTEGER(HID_T) :: group_hid
    """.format(group_name, subroutine_name)

    # declare attribute arrays
    doAttributesData(group_json)

    print """
  print *, "creating group: {0}" 
  print *, "group path: {1}"
  CALL h5gcreate_f(parent_hid, group_name, group_hid, i_res)
    """.format(group_name, newPath)

    doAttributesCreate(group_json, "group_hid")
    doLinks(h5json, group_json, "group_hid", newPath)
    
    print "end SUBROUTINE"
    print "!"
    #
    # add more subroutines for links of this group
    #
  
    doDatasets(h5json, group_json, "group_hid", newPath)
    doGroups(h5json, group_json, "group_hid", newPath)

#------------------------------------------------------------------------------
#
# Process Group links
#
#------------------------------------------------------------------------------
def doGroups(h5json, group_json, parent_id, h5path):
    log.info("doGroups h5path: " + h5path)
    links = group_json["links"]
    for link in links:
        if link["class"] == "H5L_TYPE_HARD" and link["collection"] == "groups":
            doGroup(h5json, link["id"], link["title"], parent_id, h5path + link['title']) 
    	 

#------------------------------------------------------------------------------
#
# Generate dataset code
#
#------------------------------------------------------------------------------   
  
def doDataset(h5json, dataset_id, dset_name, parent_id, h5path):
    log.info("doDataset h5path: " + h5path)
    subroutine_name = h5pathToSubroutineName("CreateDataset" + h5path )
    datasets = h5json["datasets"]
    dataset_json = datasets[dataset_id]
    type_json = dataset_json["type"]
    base_type = getBaseDataType(type_json)

    # get shape info
    rank = 0
    dset_shape = dataset_json["shape"]
     
    for_dims = None
 
    if dset_shape["class"] in ("H5S_NULL", "H5S_SCALAR"):
        print "! no declaration for null, scalar dataset"
    elif dset_shape["class"] == "H5S_SIMPLE":
        dims = dset_shape["dims"]
    	rank = len(dims)
         
        # INTEGER(hsize_t),   DIMENSION(1:2) :: dims = (/dim0, dim1/)
        for_dims = "INTEGER(hsize_t),   DIMENSION(1:" + str(rank) + ") :: dset_dims = (/"
        for i in range(rank):
            for_dims += str(dims[i])
            if i < rank - 1:
                for_dims += ", "
        for_dims += "/)"

    print """
    
!
! Create Dataset {0}
!
!
SUBROUTINE {1}(dataset_name, parent_hid, i_res) 
USE HDF5
USE ISO_C_BINDING
IMPLICIT NONE
  character(len=*), intent(in) :: dataset_name
  INTEGER(HID_T), intent(in) :: parent_hid
  INTEGER, intent(out) :: i_res
  INTEGER(HID_T) :: space_id, dataset_hid
  TYPE(C_PTR) :: f_ptr   ! c ptr for hdf5 lib calls
    """.format(dset_name, subroutine_name)

    # declare attribute arrays
    doAttributesData(dataset_json)
    # declare daset dimensions
    if for_dims:
        print """\
  ! dataset dimensions
  {0}  
        """.format(for_dims)
    
     
    print """\
  print *, "creating dataset: ", dataset_name 
    """
    
    if rank > 0:
        # need to create dataspace
        print """\
  CALL h5screate_simple_f({0}, dset_dims, space_id, i_res)
        """.format(rank)
    else:
        print "space_id = 0"
     
    print """\
  CALL h5dcreate_f(parent_hid, dataset_name, {0}, space_id, dataset_hid, i_res)
  """.format(base_type)

    if rank > 0:
        print indent + "CALL H5Sclose_f(space_id, i_res)"
        

    doAttributesCreate(dataset_json, "dataset_hid")

    print indent + "CALL H5Dclose_f(dataset_hid, i_res)"
     
    print "end SUBROUTINE"
 
#------------------------------------------------------------------------------
#
# Generate dataset for each hard link to a dataset in a group
#
#------------------------------------------------------------------------------         
def doDatasets(h5json, group_json, parent_id, h5path):
    log.info("doDatasets h5path: " + h5path)
    links = group_json["links"]
    for link in links:
        if link["class"] == "H5L_TYPE_HARD" and link["collection"] == "datasets":
            doDataset(h5json, link["id"], link["title"], parent_id, h5path + link['title'])    

    
#------------------------------------------------------------------------------
#
# Process link items
#
#------------------------------------------------------------------------------    
def doLink(h5json, link_json, parent_id, h5path):
    log.info("doLink h5path: " + h5path)
   
    if link_json["class"] == "H5L_TYPE_EXTERNAL":
        print "{0}call h5lcreate_external_f('{1}', '{2}', {3}, '{4}', i_res)".format(indent, link_json["title"], 
		link_json["h5path"], parent_id, link_json["title"])  
    elif link_json["class"] == "H5L_TYPE_SOFT":
        print "{0}call h5lcreate_soft_f('{1}', {2}, '{3}', i_res)".format(indent, link_json["h5path"], parent_id, link_json["title"])
    elif link_json["class"] == "H5L_TYPE_HARD":
        if link_json["collection"] == "groups":
            subroutine_name = h5pathToSubroutineName("CreateGroup" + h5path + link_json['title'])
            print "{0}call {1}('{2}', {3}, i_res)".format(indent, subroutine_name, link_json['title'], parent_id);
        elif link_json["collection"] == "datasets":   
            subroutine_name = h5pathToSubroutineName("CreateDataset" + h5path  + link_json['title'])
            print "{0}call {1}('{2}', {3}, i_res)".format(indent, subroutine_name, link_json['title'], parent_id);     
        elif link_json["collection"] == "datatypes":
            pass # todo
        else:
            raise Exception("unexpected collection name: " + link_json["collection"])
    elif link_json["class"] == "H5L_TYPE_UDLINK":
        print "{0}!ignoring user defined link: '{1}'".format(indent, link_json["title"])
    else:
        raise Exception("unexpected link type: " + link_json["class"]) 
    
#------------------------------------------------------------------------------
#
# Process group links
#
#------------------------------------------------------------------------------    
def doLinks(h5json, group_json, parent_id, h5path):
    log.info("doLinks h5path: " + h5path)
    links = group_json["links"]
    for link in links:
        doLink(h5json, link, parent_id, h5path)


#------------------------------------------------------------------------------
#
# Generate main fortran routine
#
#------------------------------------------------------------------------------
def fortran_main(h5json, filename): 
    log.info("fortran_main")
     
    # fortran create root attribute
    root_uuid = h5json["root"]
    group_json = h5json["groups"]
    root_json = group_json[root_uuid]
    
    log.info("fortran_main")

    # fortran main header, file creation
    print """
!-BEGIN_PROLOG-----------------------------------------------------------------
!
! NAME: {0}.f90
!
! PURPOSE: Example program that inserts values into a {0}
!          template file.
!
! REFERENCES: None
!
! COMMENTS: This requires than an empty HDF5 template file has been generated
!           for {0}. This will be the input argument.
!
!           Error checking is not performed for each call. Production code
!           should perform extensive error checking.
!
! TO COMPILE: Rename the generated code to {0}.f90, then
!
!    h5fc h5_param_n_mod.f90 {0}.f90 -o {0}
!
! HISTORY:
!
!   YYYY-MM-DD AUID      SCM  Comment
!   ---------- --------- ---- -------------------------------------------------
!   $dstamp  jelee1         Automatically generated via H5ES Builder
!
!-END_PROLOG-------------------------------------------------------------------
!
program main
!
! Include the HDF5 Library
!
! The HDF5 library is required. The library must be compiled with these flags:
!
!   --enable-fortran --enable-fortran2003
!
! This software has been tested with version 1.8.9.
!
use ISO_C_BINDING
use HDF5
  
implicit none
 
!
! Set error code for a fatal error
!
integer, parameter :: &
    FATAL=3                 ! FATAL errorcode
!
    """.format(filename)
     

    # declare attribute arrays
    doAttributesData(root_json)

    print """
!
! Misc Variables
!
integer :: &
    ios, &                   ! Input/Output status
    i_res                    ! Result code
character(len=255) :: arg    ! Input arguments
integer(HID_T) :: file_id    ! ID of HDF5 file
TYPE(C_PTR) :: f_ptr         ! c ptr for hdf5 lib calls
!
! Open the HDF5 library
!
call H5open_f(i_res)
if (i_res /= 0) then
    print *, 'Error: Initializing HDF library'
    call exit(FATAL)
endif
 
!
! Open HDF5 File
!
call H5Fcreate_f('{0}.h5', H5F_ACC_TRUNC_F, file_id, i_res)
if (i_res /= 0) then
    print *, 'Error: Opening file : {0}.h5'
    call exit(3)
endif

!
! Create the attributes for root group
!
    """.format(filename)
    doAttributesCreate(root_json, "file_id")


    # create root items
    doLinks(h5json, root_json, "file_id", "/")

    print """
!
!  
!
!  call write_attributes(file_id)
!
! Fill the datasets
!
!
! Close the file
!
call H5Fclose_f(file_id, i_res)
!
! Close HDF5
!
call h5close_f(i_res)
!
! End of program
!
print *, ' '
print *, '{0}.f90 complete.'
end program main
    """.format(filename)
    #
    # next add group and dataset subroutines after the main program
    #
    doDatasets(h5json, root_json, "file_id", "/")
    doGroups(h5json, root_json, "file_id", "/")
    
#------------------------------------------------------------------------------
#
# Program entry point
#
#------------------------------------------------------------------------------
         
def main():
    
    parser = argparse.ArgumentParser(usage='%(prog)s [-h] <json_file> <out_filename>')
    parser.add_argument('in_filename', nargs='+', help='JSon file to be converted to h5py')
    parser.add_argument('out_filename', nargs='+', help='name of HDF5 file to be created by generated code')
    args = parser.parse_args()

    # create logger
    global log
    log = logging.getLogger("h5serv")
    # log.setLevel(logging.WARN)
    log.setLevel(logging.INFO)
    # add log handler
    handler = logging.FileHandler('./jsontofortran.log')
    
    # add handler to logger
    log.addHandler(handler)
    
    text = open(args.in_filename[0]).read()
    
    log.info("loading " + args.in_filename[0]);
    # parse the json file
    h5json = json.loads(text)
    
    if "root" not in h5json:
        raise Exception("no root key in input file")


    filename = args.out_filename[0]
    
    fortran_main(h5json, filename)
  
    
    #group_json = h5json["groups"]
    #root_json = group_json[root_uuid]
    #doAttributes(root_json, file_variable)
    #doLinks(h5json, root_json, file_variable)

    # generic create attribute routine
    print """
!
! Create an Attribute
!
!
SUBROUTINE CreateAttribute(attr_name, parent_id, rank, dims, h5_type, buf, i_res) 
USE HDF5
USE ISO_C_BINDING
IMPLICIT NONE
  character(len=*), intent(in) :: attr_name
  integer(HID_T), intent(in) :: parent_id
  integer, intent(in) :: rank
  integer(hsize_t), intent(in), dimension(*) :: dims
  integer, intent(in) :: h5_type
  integer, intent(out) :: i_res
  TYPE(C_PTR), intent(in) :: buf
  INTEGER :: hdferr  
  INTEGER(HID_T)  :: space, attr ! Handles
  
  print *, "creat attribute ", attr_name
  print *, "parent id", parent_id
  print *, "rank", rank
  print *, "dims: ", dims(1)
  CALL H5Screate_simple_f(rank, dims, space, hdferr)
  CALL H5Acreate_f(parent_id, attr_name, h5_type, space, attr, hdferr)
  CALL H5Awrite_f(attr, H5T_NATIVE_INTEGER, buf, hdferr)
  CALL H5Aclose_f(attr, hdferr)
  CALL H5Sclose_f(space, hdferr)
  i_res = 0

end SUBROUTINE
    """
    

main()

    
	
