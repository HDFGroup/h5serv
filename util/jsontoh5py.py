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
from sets import Set

variable_names = Set()

"""
jsontoh5py - output Python code that generates HDF5 file based on given JSON input  
"""

def getNumpyTypename(hdf5TypeName, typeClass=None):
    predefined_int_types = {
          'H5T_STD_I8':  'i1', 
          'H5T_STD_U8':  'u1',
          'H5T_STD_I16': 'i2', 
          'H5T_STD_U16': 'u2',
          'H5T_STD_I32': 'i4', 
          'H5T_STD_U32': 'u4',
          'H5T_STD_I64': 'i8',
          'H5T_STD_U64': 'u8' 
    }
    predefined_float_types = {
          'H5T_IEEE_F32': 'f4',
          'H5T_IEEE_F64': 'f8'
    }
    if len(hdf5TypeName) < 3:
        raise Exception("Type Error: invalid type")
    endian = '<'  # default endian
    key = hdf5TypeName
    if hdf5TypeName.endswith('LE'):
        key = hdf5TypeName[:-2]
    elif hdf5TypeName.endswith('BE'):
        key = hdf5TypeName[:-2]
        endian = '>'
        
    if key in predefined_int_types and (typeClass == None or 
            typeClass == 'H5T_INTEGER'):
        return endian + predefined_int_types[key]
    if key in predefined_float_types and (typeClass == None or 
            typeClass == 'H5T_FLOAT'):
        return endian + predefined_float_types[key]
    raise TypeError("Type Error: invalid type")
    
     

def getBaseDataType(typeItem):
    code = "dt = "
    if type(typeItem) == str or type(typeItem) == unicode:
        # should be one of the predefined types
        dtName = getNumpyTypename(typeItem)
        code += "np.dtype('" + dtName + "')"
        return code
        
    if type(typeItem) != dict:
        raise TypeError("Type Error: invalid type")
              
    if 'class' not in typeItem:
        raise KeyError("'class' not provided")
    typeClass = typeItem['class']
    shape = ''
    if 'shape' in typeItem:  
        dims = None      
        if type(typeItem['shape']) == int:
            dims = (typeItem['shape'])  # make into a tuple
        elif type(typeItem['shape']) not in (list, tuple):
            raise TypeError("expected list or integer for shape")
        else:
            dims = typeItem['shape']
        shape = str(tuple(dims))
        
    if typeClass == 'H5T_INTEGER':
        if 'base' not in typeItem:
            raise KeyError("'base' not provided")      
        baseType = getNumpyTypename(typeItem['base'], typeClass='H5T_INTEGER')
        code += "np.dtype('" + shape + baseType + "')"
    elif typeClass == 'H5T_FLOAT':
        if 'base' not in typeItem:
            raise KeyError("'base' not provided")
        baseType = getNumpyTypename(typeItem['base'], typeClass='H5T_FLOAT')
        code += "np.dtype('" + shape + baseType + "')"
    elif typeClass == 'H5T_STRING':
        if 'strsize' not in typeItem:
            raise KeyError("'strsize' not provided")
        if 'cset' not in typeItem:
            raise KeyError("'cset' not provided")          
            
        if typeItem['strsize'] == 'H5T_VARIABLE':
            if shape:
                raise TypeError("ArrayType is not supported for variable len types")
            if typeItem['cset'] == 'H5T_CSET_ASCII':
                code += "special_dtype(vlen=str)"
            elif typeItem['cset'] == 'H5T_CSET_UTF8':
                code += "special_dtype(vlen=unicode)"
            else:
                raise TypeError("unexpected 'cset' value")
        else:
            nStrSize = typeItem['strsize']
            if type(nStrSize) != int:
                raise TypeError("expecting integer value for 'strsize'")
            code += "np.dtype(" + shape + "S" + str(nStrSize) + ")"  # fixed size ascii string
    elif typeClass == 'H5T_VLEN':
        if shape:
            raise TypeError("ArrayType is not supported for variable len types")
        if 'base' not in typeItem:
            raise KeyError("'base' not provided") 
        vlenBaseType = typeItem['base']
        baseType = getNumpyTypename(vlenBaseType['base'], typeClass=vlenBaseType['class'])
        code += "special_dtype(vlen=np.dtype('" + baseType + "'))"
    elif typeClass == 'H5T_OPAQUE':
        if shape:
            raise TypeError("Opaque Type is not supported for variable len types")
        if 'size' not in typeItem:
            raise KeyError("'size' not provided")
        nSize = int(typeItem['size'])
        if nSize <= 0:
            raise TypeError("'size' must be non-negative")
        code +=  "np.dtype('V'"  + str(nSize) + "')"
    elif typeClass == 'H5T_ARRAY':
        if not shape:
            raise KeyError("'shape' must be provided for array types")
        if 'base' not in typeItem:
            raise KeyError("'base' not provided") 
        baseType = getNumpyTypename(typeItem['base'])
        if type(baseType) not in  (str, unicode):
            raise TypeError("Array type is only supported for predefined base types")
        # should be one of the predefined types
        code += "np.dtype('" + shape + baseType + "')"
    else:
        raise TypeError("Invalid type class")
           
    return code  
    
def valueToString(attr_json):
    value = attr_json["value"]
    return json.dumps(value)
    
def doAttribute(attr_json, parent_var):    
    print parent_var + ".attrs['" + attr_json['name'] + "'] = " + valueToString(attr_json)
    
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

def doAttributes(group_json, parent_var):
    if "attributes" not in group_json:
        return
    attrs_json = group_json["attributes"]
    
    print "# creating attributes for '" + getObjectName(group_json) + "'"
    for attr_json in attrs_json:
        doAttribute(attr_json, parent_var)
        
def getObjectVariableName(title):
    char_list = list(title.lower())
    for i in range(len(char_list)):
        ch = char_list[i]
        if (ch >= 'a' and ch <= 'z') or (ch >= '0' and ch <= '9'):
            pass  # ok char
        else:
            char_list[i] = '_'  # replace with underscore
    var_name = "".join(char_list)
    if char_list[0] >= '0' and char_list[0] <= '9':
        var_name = 'v' + var_name   # pre-pend with a non-numeric
    if var_name in variable_names:
        for i in range(1, 99):
           if (var_name + '_' + str(i)) not in variable_names:
                var_name += '_' + str(i)
                break
        raise TypeError("Type Error: unable to create type for name: " + title)
    variable_names.add(var_name)  # add to our list of variable names
               
    return var_name
    
def doGroup(h5json, group_id, group_name, parent_var):
    print "# group -- ", group_name
    group_var = getObjectVariableName(group_name)
    print "{0} = {1}.create_group('{2}')".format(group_var, parent_var, group_name)
    groups = h5json["groups"]
    group_json = groups[group_id]
    #print "group_json:", group_json
    doAttributes(group_json, group_var)
    doLinks(h5json, group_json, group_var)

def doDataset(h5json, dset_id, dset_name, parent_var):
    print "# make dataset: ", dset_name
    dset_var = getObjectVariableName(dset_name)
    datasets = h5json["datasets"]
    dset_json = datasets[dset_id]
    #dt = createDataType(dset_json["type"])
    type_json = dset_json["type"]
    dtLine = getBaseDataType(type_json)  # "dt = ..."
    print dtLine
    #dset_type_str = hdf5dtype.getNumpyTypename(type_json["base"])  # todo - read type info, convert to numpy type
    dset_space_str = None
    if "shape" in dset_json:
        shape_json = dset_json["shape"]
        if shape_json["class"] == "H5S_SIMPLE":
            dset_space_str = "("
            dims = shape_json["dims"]
            rank = len(dims)
            for i in range(rank):
                dset_space_str += str(dims[i])
                if i < rank-1 or rank == 1:
                    dset_space_str += ","
            dset_space_str += "), "
    code_line = dset_var + " = " + parent_var + ".create_dataset('" + dset_var + "', "
    if dset_space_str:
        code_line += dset_space_str
    code_line += "dtype=dt)"
    print code_line
    print "# initialize dataset values here"
    doAttributes(dset_json, dset_var)    
    
    
def doLink(h5json, link_json, parent_var):
    if link_json["class"] == "H5L_TYPE_EXTERNAL":
        print "{0}['{1}'] = h5py.ExternalLink('{2}', '{3}')".format(parent_var, link_json["title"], link_json["file"], link_json["h5path"])
    elif link_json["class"] == "H5L_TYPE_SOFT":
        print "{0}['{1}'] = h5py.SoftLink('{2}')".format(parent_var, link_json["title"], link_json["h5path"])
    elif link_json["class"] == "H5L_TYPE_HARD":
        if link_json["collection"] == "groups":
            doGroup(h5json, link_json["id"], link_json["title"], parent_var) 
        elif link_json["collection"] == "datasets":   
            doDataset(h5json, link_json["id"], link_json["title"], parent_var)       
        elif link_json["collection"] == "datatypes":
            pass # todo
        else:
            raise Exception("unexpected collection name: " + link_json["collection"])
    elif link_json["class"] == "H5L_TYPE_UDLINK":
        print "# ignoring user defined link: '{0}'".format(link_json["title"])
    else:
        raise Exception("unexpected link type: " + link_json["class"]) 
    
    
def doLinks(h5json, group_json, parent_var):
    links = group_json["links"]
    for link in links:
        doLink(h5json, link, parent_var)
         
def main():
    parser = argparse.ArgumentParser(usage='%(prog)s [-h] <json_file> <out_filename>')
    parser.add_argument('in_filename', nargs='+', help='JSon file to be converted to h5py')
    parser.add_argument('out_filename', nargs='+', help='name of HDF5 file to be created by generated code')
    args = parser.parse_args()
    
    text = open(args.in_filename[0]).read()
    
    # parse the json file
    h5json = json.loads(text)
    
    if "root" not in h5json:
        raise Exception("no root key in input file")
    root_uuid = h5json["root"]
    
    filename = args.out_filename[0]
    file_variable = 'f' 
    
    print "import h5py"
    print "import numpy as np"
    print " "
    print "print 'creating file: {0}'".format(filename)
    print "{0} = h5py.File('{1}', 'w')".format(file_variable, filename)
    print " "
    
    group_json = h5json["groups"]
    root_json = group_json[root_uuid]
    doAttributes(root_json, file_variable)
    doLinks(h5json, root_json, file_variable)
    
    print "print 'done!'"   
    

main()

    
	
