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
import requests
import sys
import json


"""
DumpJson - return json representation of all objects within the given domain
"""

class DumpJson:
    def __init__(self):
        pass
        
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
        
        
    def dumpAttribute(self, obj_uri):
        rsp_json = self.makeRequest(obj_uri)
        attr_json = {}
        attr_json['name'] = rsp_json['name']
        attr_json['type'] = rsp_json['type']
        attr_json['shape'] = rsp_json['shape']
        if 'value' in rsp_json and rsp_json['value']:
            attr_json['value'] = rsp_json['value']
        return attr_json
        
    def dumpAttributes(self, uri, jsonOut):
        rsp_json = self.makeRequest(uri)
        attributes_json = rsp_json['attributes']
        
        if len(attributes_json) > 0:
            items = []
            
            for attr in attributes_json:
                name = attr['name']
                
                if self.noAttrData:
                    # just copy what we got from "attributes" request
                    items.append(attr)
                else:
                    # fetch the attribute data
                    uri_attr_request = uri + "/" + name
                    item = self.dumpAttribute(uri_attr_request)
                    items.append(item)
            jsonOut['attributes'] = items;
        
    def dumpLinks(self, uri, jsonOut):
        rsp_json = self.makeRequest(uri)
        links_json = rsp_json['links']
        
        if len(links_json) > 0:
            linkDict = []
            jsonOut['links'] = links_json
        
    def dumpGroup(self, uri, jsonOut):
        rsp_json = self.makeRequest(uri)
        group_uuid = rsp_json['id'] 
        jsonOut[group_uuid] = {} 
        self.dumpLinks(uri + '/links', jsonOut[group_uuid]) 
        self.dumpAttributes(uri + '/attributes', jsonOut[group_uuid]) 
        
    def dumpGroups(self):
        uri = "/groups" 
        rsp_json = self.makeRequest(uri)
        jsonOut = {}
        
        self.json['groups'] = jsonOut
        
        group_ids = rsp_json['groups']
        group_ids.append(self.json['root'])  # add in root group
        for group_uuid in group_ids:
            uri = "/groups/" + group_uuid
            self.dumpGroup(uri, jsonOut)
        
    def dumpDataset(self, uri, jsonOut):
        rsp_json = self.makeRequest(uri)
        dset_uuid = rsp_json['id'] 
        dset_json = {}
        dset_json['shape'] = rsp_json['shape']
        dset_json['type'] = rsp_json['type']
        
        # get the data values    
        rsp_json = self.makeRequest(uri + '/value')
        
        if not self.noDsetData:
            # get the dataset values
            if 'value' in rsp_json:
                data = rsp_json['value']
                if data:
                    dset_json['value'] = data
        
        jsonOut[dset_uuid] = dset_json 
         
        self.dumpAttributes(uri + '/attributes', jsonOut[dset_uuid]) 
        
    def dumpDatasets(self):
        rsp_json = self.makeRequest("/datasets")
        jsonOut = {}
        
        self.json['datasets'] = jsonOut
        
        dataset_ids = rsp_json['datasets']
        
        for dset_uuid in dataset_ids:
            uri = "/datasets/" + dset_uuid
            self.dumpDataset(uri, jsonOut)
        
    def dumpDatatype(self, uri, jsonOut):
        rsp_json = self.makeRequest(uri)
        
        dtype_uuid = rsp_json['id']
        
        type_json = {}
        type_json['type'] = rsp_json['type']
        
        jsonOut[dtype_uuid] =  type_json
         
        self.dumpAttributes(uri + '/attributes', jsonOut[dtype_uuid]) 
        
    def dumpDatatypes(self):
        rsp_json = self.makeRequest("/datatypes")
        jsonOut = {}
        
        self.json['datatypes'] = jsonOut
        
        datatype_ids = rsp_json['datatypes']
        
        for dtype_uuid in datatype_ids:
            uri = "/datatypes/" + dtype_uuid
            self.dumpDatatype(uri, jsonOut)
             
    
    def dumpDomain(self):
        rsp_json = self.makeRequest("/")
        
        self.json = {}
        
        # save the root uuid
        self.json['root'] = rsp_json['root']
        
        self.dumpGroups()
        
        self.dumpDatasets()
            
        self.dumpDatatypes()
            
        print(json.dumps(self.json, sort_keys=True, indent=4))

#
# Print usage and exit
#
def printUsage():
    print("usage: python exportjson.py [-v] [-D|d] [-endpoint=<server_ip>]  [-port=<port] <domain>")
    print("  options -v: verbose, print request and response codes from server")
    print("  options -D: suppress all data output")
    print("  options -d: suppress data output for datasets (but not attributes)")
    print("  options -endpoint: specify IP endpoint of server")
    print("  options -port: port address of server [default 7253]")
    print(" ------------------------------------------------------------------------------")
    print("  Example - get 'tall' collection from HDF Group server:")
    print("       python exportjson.py tall.data.hdfgroup.org")
    print("  Example - get 'tall' collection from a local server instance ")
    print("        (assuming the server is using port 5000):")
    print("        python exportjson.py -endpoint=127.0.0.1 -port=5000 tall.test.hdfgroup.org")
    sys.exit(); 
    
#
# main
#
def main():
    
    nargs = len(sys.argv)
        
    dumper = DumpJson()
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
        elif arg == "-D":
            dumper.noDsetData = True
            dumper.noAttrData = True
        elif arg == "-d":
            dumper.noDsetData = True
            
     
    if nargs - option_count <= 1:
        printUsage()
        
    dumper.domain = sys.argv[nargs-1]
    dumper.dumpDomain()
    

main()

    
	
