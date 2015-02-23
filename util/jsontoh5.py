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
import json
import argparse
import numpy as np
import h5py

sys.path.append('../server')
from hdf5db import Hdf5db
import hdf5dtype 


"""
Writeh5 - return json representation of all objects within the given file
    h5writer = Writeh5(db, h5json)
        h5writer.writeFile()   
"""

class Writeh5:
    def __init__(self, db, json, options=None):
        self.options = options
        self.db = db
        self.json = json
        self.root_uuid = None
             
    
    #
    # Create a hard, soft, or external link
    #    
    def createLink(self, link_obj, parent_uuid):
        title = link_obj["title"]
        link_class = link_obj["class"]
        if link_class == 'H5L_TYPE_HARD':
            child_uuid = link_obj["id"]
            self.db.linkObject(parent_uuid, child_uuid, title)
        elif link_class == 'H5L_TYPE_SOFT':
            h5path = link_obj["h5path"]
            self.db.createSoftLink(parent_uuid, h5path, title)
        elif link_class == 'H5L_TYPE_EXTERNAL':
            h5path = link_obj["h5path"]
            link_file = link_obj["file"]
            self.db.createExternalLink(parent_uuid, link_file, h5path, title)
        else:
            print "Unable to create link with class:", link_class
    
    #
    # Create HDF5 dataset object and write data values
    #        
    def createDataset(self, uuid, body):
        datatype = body['type']
        if type(datatype) in (str, unicode) and datatype.startswith("datatypes/"):
            #committed datatype, just pass in the UUID part
            datatype = datatype[len("datatypes/"):]
        dims = None
        max_shape=None
        fill_value=None
        if "shape" in body:
            shape = body["shape"]
            if shape["class"] == 'H5S_SIMPLE':
                dims = shape["dims"]
                if type(dims) == int:
                    # convert int to array
                    dim1 = shape
                    dims = [dim1]
                if "maxdims" in shape:
                    max_shape = shape["maxdims"]
                    if type(max_shape) == int:
                        #convert to array
                        dim1 = max_shape
                        max_shape = [dim1]
                    # convert 0's to None's
                    for i in range(len(max_shape)):
                        if max_shape[i] == 0:
                            max_shape[i] = None
                if "filvalue" in body:
                    fill_value = body["fillvalue"]
                    
        self.db.createDataset(datatype, dims, max_shape=max_shape, fill_value=fill_value,
            obj_uuid=uuid)
            
        if "value" in body:
            data = body["value"]
            self.db.setDatasetValuesByUuid(uuid, data) 
            
    def createAttribute(self, attr_json, col_name, uuid):
    
        attr_name = attr_json["name"]
        datatype = attr_json["type"]
        if type(datatype) in (str, unicode) and datatype.startswith("datatypes/"):
            #committed datatype, just pass in the UUID part
            datatype = datatype[len("datatypes/"):]
            
        attr_value = attr_json["value"]
        dims = None
        if "shape" in attr_json:
            shape = attr_json["shape"]
            if shape["class"] == 'H5S_SIMPLE':
                dims = shape["dims"]
                if type(dims) == int:
                    # convert int to array
                    dim1 = shape
                    dims = [dim1]
        self.db.createAttribute(col_name, uuid, attr_name, dims, datatype, attr_value)
                    
            
    #
    # create committed datatype HDF5 object
    #   
    def createDatatype(self, uuid, body):
        datatype = body['type']
        self.db.createCommittedType(datatype, obj_uuid=uuid)    
            
    #
    # Create HDF5 group object  (links and attributes will be added later)
    #        
    def createGroup(self, uuid, body):
        if uuid != self.root_uuid:
            self.db.createGroup(obj_uuid=uuid)
                 
    # 
    # Create all the HDF5 objects defined in the JSON file
    #       
    def createObjects(self):
        # create datatypes
        if "datatypes" in self.json:
            datatypes = self.json["datatypes"]      
            for uuid in datatypes:
                json_obj = datatypes[uuid]
                self.createDatatype(uuid, json_obj) 
        # create groups
        if "groups" in self.json:
            groups = self.json["groups"]
            for uuid in groups:
                json_obj = groups[uuid]
                self.createGroup(uuid, json_obj)
        # create datasets
        if "datasets" in self.json:
            datasets = self.json["datasets"]    
            for uuid in datasets:
                json_obj = datasets[uuid]
                self.createDataset(uuid, json_obj)
       
            
    # 
    # Create all the attributes for HDF5 objects defined in the JSON file
    # Note: this needs to be done after createObjects since an attribute
    # may use a committed datatype
    #       
    def createAttributes(self):
        # create datatype attributes
        if "datatypes" in self.json:
            datatypes = self.json["datatypes"]      
            for uuid in datatypes:
                body = datatypes[uuid]
                if "attributes" in body:
                    attributes = body["attributes"]
                    for attribute in attributes:
                        self.createAttribute(attribute, "datatypes", uuid)
        # create group attributes
        if "groups" in self.json:
            groups = self.json["groups"]
            for uuid in groups:
                body = groups[uuid]
                if "attributes" in body:
                    attributes = body["attributes"]
                    for attribute in attributes:
                        self.createAttribute(attribute, "groups", uuid)
        # create datasets   
        if "datasets" in self.json:  
            datasets = self.json["datasets"]  
            for uuid in datasets:
                body = datasets[uuid]
                if "attributes" in body:
                    attributes = body["attributes"]
                    for attribute in attributes:
                        self.createAttribute(attribute, "datasets", uuid)
                    
    #
    # Link all the objects 
    # Note: this will "de-anonymous-ize" objects defined in the HDF5 file
    #   Any non-linked objects will be deleted when the __db__ group is deleted
    #               
    def createLinks(self):
        if "groups" in self.json:
            groups = self.json["groups"]
            for uuid in groups:
                json_obj = groups[uuid]
                if "links" in json_obj:
                    links = json_obj["links"]
                    for link in links:
                        self.createLink(link, uuid)
              
        
    def writeFile(self):
        
        self.root_uuid = self.json["root"]
        
        self.createObjects()    # create datasets, groups, committed datatypes
        self.createAttributes() # create attributes for objects
        self.createLinks()      # link it all together
           
def main():
    parser = argparse.ArgumentParser(usage='%(prog)s [-h] <json_file> <h5_file>')
    parser.add_argument('in_filename', nargs='+', help='JSon file to be converted to h5')
    parser.add_argument('out_filename', nargs='+', help='name of HDF5 output file')
    args = parser.parse_args()
    
    text = open(args.in_filename[0]).read()
    
    # parse the json file
    h5json = json.loads(text)
    
    if "root" not in h5json:
        raise Exception("no root key in input file")
    root_uuid = h5json["root"]
    
    filename = args.out_filename[0]
    

    # create the file, will raise IOError if there's a problem
    Hdf5db.createHDF5File(filename)
    
    with Hdf5db(filename, root_uuid=root_uuid) as db:
        h5writer = Writeh5(db, h5json)
        h5writer.writeFile() 
        
    # open with h5py and remove the _db_ group
    # Note: this will delete any anonymous (un-linked) objects
    f = h5py.File(filename, 'a') 
    del f["__db__"]
    f.close()
    
        
    print "done!"   
    

main()

    
	
