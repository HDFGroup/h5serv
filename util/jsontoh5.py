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
        self.groups = {}  # uuid to object dictionary
        
        
    def createAttribute(self, attr_json, col_name, uuid):
    
        attr_name = attr_json["name"]
        attr_type = attr_json["type"]
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
        self.db.createAttribute(col_name, uuid, attr_name, dims, attr_type, attr_value)
                    
        
    def dumpAttributes(self, col_name, uuid):
        attr_list = self.db.getAttributeItems(col_name, uuid)
        items = []
        for attr in attr_list:
            item = self.dumpAttribute(col_name, uuid, attr['name'])
            items.append(item)
                   
        return items    
        
    def dumpLink(self, uuid, name):
        item = self.db.getLinkItemByUuid(uuid, name)
        for key in ('ctime', 'mtime', 'href'):
            if key in item:
                del item[key]
        return item
        
    
    def dumpLinks(self, uuid):
        link_list = self.db.getLinkItems(uuid)
        items = []
        for link in link_list:
            item = self.dumpLink(uuid, link['title'])
            items.append(item)
        return items
       
        
    def createGroup(self, uuid, body):
        if uuid != self.root_uuid:
            self.db.createGroup(obj_uuid=uuid)
        if "attributes" in body:
            attributes = body["attributes"]
            for attribute in attributes:
                self.createAttribute(attribute, "groups", uuid)
        
        
    def createGroups(self):
        groups = self.json["groups"]
        for uuid in groups:
            json_obj = groups[uuid]
            self.createGroup(uuid, json_obj)
            
    def createLink(self, link_obj, parent_uuid):
        title = link_obj["title"]
        link_class = link_obj["class"]
        if link_class == 'H5L_TYPE_HARD':
            child_uuid = link_obj["uuid"]
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
         
            
    def createLinks(self):
        groups = self.json["groups"]
        for uuid in groups:
            json_obj = groups[uuid]
            if "links" in json_obj:
                links = json_obj["links"]
                for link in links:
                    self.createLink(link, uuid)
            
    
    def createDataset(self, uuid, body):
        datatype = body['type']
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
                    if type(maxdims) == int:
                        #convert to array
                        dim1 = max_shape
                        max_shape = [dim1]
                if "filvalue" in body:
                    fill_value = body["fillvalue"]
          
        self.db.createDataset(datatype, dims, max_shape=max_shape, fill_value=fill_value,
            obj_uuid=uuid)
            
        if "value" in body:
            data = body["value"]
            self.db.setDatasetValuesByUuid(uuid, data)
            
        if "attributes" in body:
            attributes = body["attributes"]
            for attribute in attributes:
                self.createAttribute(attribute, "datasets", uuid)
            
        
            
    def createDatasets(self):
        datasets = self.json["datasets"]
        
        for uuid in datasets:
            json_obj = datasets[uuid]
            self.createDataset(uuid, json_obj)
            
    def createDatatype(self, uuid, body):
        datatype = body['type']
        self.db.createCommittedType(datatype, obj_uuid=uuid)
        if "attributes" in body:
            attributes = body["attributes"]
            for attribute in attributes:
                self.createAttribute(attribute, "datatypes", uuid)
            
            
    def createDatatypes(self):
        datatypes = self.json["datatypes"]
        
        for uuid in datatypes:
            json_obj = datatypes[uuid]
            self.createDatatype(uuid, json_obj)  
        
    def writeFile(self):
        
        self.root_uuid = self.json["root"]
           
        self.createGroups()
        
        self.createDatasets()
        
        self.createDatatypes()
        
        self.createLinks()
           

def main():
    parser = argparse.ArgumentParser(usage='%(prog)s [-h] <json_file> <h5_file>')
    parser.add_argument('in_filename', nargs='+', help='JSon file to be converted to h5')
    parser.add_argument('out_filename', nargs='+', help='name of HDF5 output file')
    args = parser.parse_args()
    
    text = open(args.in_filename[0]).read()
    
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
    f = h5py.File(filename, 'a') 
    del f["__db__"]
    f.close()
    
        
    print "done!"   
    

main()

    
	
