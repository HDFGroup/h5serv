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

import six

if six.PY3:
    unicode = str

import sys
import requests
import json
import numpy as np
import h5py

from h5json import Hdf5db
  

"""
exporth5 - creates an HDF5 file based from h5serv domain  
"""

class Dumph5:
    def __init__(self):
        self.group_uuids = []
        self.dataset_uuids = []
        self.datatype_uuids = []
               
    #
    # Make request to service, convert json response to python dictionary 
    # and return.
    #      
    def makeRequest(self, uri):
        endpoint = self.endpoint
        if not endpoint:
            endpoint = "http://" + self.domain
        endpoint += ':'
        endpoint += str(self.port)
        req = endpoint + uri
        if self.verbose:
            print("REQ:", req)
        #print "headers:", self.domain
        headers = {'host': self.domain}
        rsp = requests.get(req, headers=headers)
        if self.verbose:
            print("RSP:", rsp.status_code)
            
        if rsp.status_code != 200:
            raise Exception("got bad httpstatus: " + str(rsp.status_code) +
                " for request: " + uri);
        #print "got response text:", rsp.text
        rsp_json = json.loads(rsp.text)
        return rsp_json
        
     
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
            link_file = link_obj["h5domain"]
            self.db.createExternalLink(parent_uuid, link_file, h5path, title)
        else:
            print("Unable to create link with class:", link_class)
    
    #
    # Create HDF5 dataset object and write data values
    #        
    def createDataset(self, uuid):
        # get json for the dataset
        rsp_json = self.makeRequest("/datasets/" + uuid)
        
        self.dataset_uuids.append(uuid)

        datatype = rsp_json['type']
        if type(datatype) in (str, unicode) and datatype.startswith("datatypes/"):
            #committed datatype, just pass in the UUID part
            datatype = datatype[len("datatypes/"):]
        dims = None
        max_shape=None
        creation_props=None
        if "shape" in rsp_json:
            shape = rsp_json["shape"]
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
        if 'creationProperties' in rsp_json:
            creation_props = rsp_json['creationProperties']
                                 
        self.db.createDataset(datatype, dims, max_shape=max_shape, 
            creation_props=creation_props, obj_uuid=uuid)         
        
        # get the data values    
        rsp_json = self.makeRequest("/datasets/" + uuid + '/value')
           
        if "value" in rsp_json:
            data = rsp_json["value"]
            #print json.dumps(data, sort_keys=True, indent=4)
            self.db.setDatasetValuesByUuid(uuid, data) 
            
    #
    # Create all datasets in the domain
    #
    def createDatasets(self):
        uri = "/datasets" 
        rsp_json = self.makeRequest(uri)
        dataset_ids = rsp_json['datasets']
        
        for dataset_uuid in dataset_ids:
            self.createDataset(dataset_uuid)
            
    def createAttribute(self, attr_name, col_name, uuid):
    
        attr_json = self.makeRequest("/" + col_name + "/" + uuid + "/attributes/" + attr_name)
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
    def createDatatype(self, uuid):
        rsp_json = self.makeRequest("/datatypes/" + uuid)
        datatype = rsp_json['type']
        self.db.createCommittedType(datatype, obj_uuid=uuid)   
        
        
    #
    # create datatypes
    #
    def createDatatypes(self):   
        rsp_json = self.makeRequest("/datatypes")
        datatype_ids = rsp_json['datatypes']
        
        for datatype_uuid in datatype_ids:
            self.createDatatype(datatype_uuid)
    
            
    #
    # Create HDF5 group object  (links and attributes will be added later)
    #        
    def createGroup(self, uuid):
        self.group_uuids.append(uuid)
        if uuid != self.root_uuid:
            self.db.createGroup(obj_uuid=uuid)
            
            
    #
    # Create all groups in the domain
    #
    def createGroups(self):
        rsp_json = self.makeRequest("/groups")
        group_ids = rsp_json['groups']
        group_ids.append(self.root_uuid)  # add root group uuid
        
        for group_uuid in group_ids:
            self.createGroup(group_uuid)
                 
    # 
    # Create all the HDF5 objects defined in the JSON file
    #       
    def createObjects(self):
        # create datatypes
        self.createDatatypes()
        
        # create groups
        self.createGroups()
                
        # create datasets
        self.createDatasets()
         
       
            
    # 
    # Create all the attributes for HDF5 objects defined in the JSON file
    # Note: this needs to be done after createObjects since an attribute
    # may use a committed datatype
    #       
    def createAttributes(self):
        # create datatype attributes
        for datatype_uuid in self.datatype_uuids:
            rsp_json = self.makeRequest("/datatypes/" + datatype_uuid + "/attributes")
            attributes = rsp_json["attributes"]
            for attribute_json in attributes:
                self.createAttribute(attribute_json["name"], "datatypes", uuid)
                
        # create group attributes
        for group_uuid in self.group_uuids:
            rsp_json = self.makeRequest("/groups/" + group_uuid + "/attributes")
            attributes = rsp_json["attributes"]
            for attribute_json in attributes:
                self.createAttribute(attribute_json["name"], "groups", group_uuid)
                
        # create dataset attributes
        for dataset_uuid in self.dataset_uuids:
            rsp_json = self.makeRequest("/datasets/" + dataset_uuid + "/attributes")
            attributes = rsp_json["attributes"]
            for attribute_json in attributes:
                self.createAttribute(attribute_json["name"], "datasets", dataset_uuid)
            
                    
    #
    # Link all the objects 
    # Note: this will "de-anonymous-ize" objects defined in the HDF5 file
    #   Any non-linked objects will be deleted when the __db__ group is deleted
    #               
    def createLinks(self):
        for group_uuid in self.group_uuids:
            rsp_json = self.makeRequest("/groups/" + group_uuid + "/links")
            links = rsp_json["links"]
            for link in links:
                self.createLink(link, group_uuid)
                 
        
    def writeFile(self, db):
    
        self.db = db
        
        self.root_uuid = db.root_uuid
        
        print("file root_uuid:", self.root_uuid)
        
        
        self.createObjects()    # create datasets, groups, committed datatypes
        self.createAttributes() # create attributes for objects
        self.createLinks()      # link it all together

#
# Print usage and exit
#
def printUsage():
    print("usage: python exporth5.py [-v] [-endpoint=<server_ip>]  [-port=<port>] <domain> <filename>")
    print("  options -v: verbose, print request and response codes from server")
    print("  options -endpoint: specify IP endpoint of server")
    print("  options -port: port address of server [default 7253]")
    print(" ------------------------------------------------------------------------------")
    print("  Example - get 'tall' collection from HDF Group server, save to tall.h5:")
    print("       python exporth5.py tall.data.hdfgroup.org tall.h5")
    print("  Example - get 'tall' collection from a local server instance ")
    print("        (assuming the server is using port 5000):")
    print("        python exporth5.py -endpoint=127.0.0.1 -port=5000 tall.test.hdfgroup.org tall.h5")
    sys.exit(); 
               
def main():
    nargs = len(sys.argv)
        
    dumper = Dumph5()
    dumper.verbose = False 
    dumper.endpoint = None
    dumper.port = 7253
    dumper.noDsetData = False
    dumper.noAttrData = False
    
    endpoint_option = "-endpoint="
    port_option = "-port="
    
    option_count = 0
    
    for arg in sys.argv:
        if arg.startswith(endpoint_option):
            endpoint = arg[len(endpoint_option):]
            if endpoint.startswith("http"):
                dumper.endpoint = endpoint
            else:
                dumper.endpoint = "http://" + endpoint
            option_count += 1
        elif arg.startswith(port_option):
            port = arg[len(port_option):]
            dumper.port = int(port)
            option_count += 1
        elif arg == "-v":
            dumper.verbose = True
            
     
    if nargs - option_count <= 2:
        printUsage()
        
    domain = sys.argv[nargs-2]
    filename = sys.argv[nargs-1]
    
    print("domain:", domain)
    print("filename:", filename)
    
    dumper.domain = domain
    
    
    domain_json = dumper.makeRequest("/")
    
    if "root" not in domain_json:
        raise Exception("no root key in domain response")
        
    root_uuid = domain_json["root"]
    
    # create the file, will raise IOError if there's a problem
    Hdf5db.createHDF5File(filename)
    
    with Hdf5db(filename, root_uuid=root_uuid) as db:
        dumper.writeFile(db) 

    # open with h5py and remove the _db_ group
    # Note: this will delete any anonymous (un-linked) objects
    f = h5py.File(filename, 'a') 
    del f["__db__"]
    f.close()
    
           
    print("done!")  
    

main()

    
	
