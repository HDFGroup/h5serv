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
        
    def dumpAttribute(self, obj_uri, jsonOut):
        req = self.endpoint + obj_uri 
        headers = {'host': self.domain}
        rsp = requests.get(req, headers=headers)
        if rsp.status_code != 200:
            print "GET", obj_uri, "returned httpstatus:", rsp.status_code
            return False
        rspJson = json.loads(rsp.text)
        name = rspJson['name']
        jsonOut[name] = rspJson
        return True
        
        
    def dumpAttributes(self, uri, jsonOut):
        req = self.endpoint + uri 
        headers = {'host': self.domain}
        rsp = requests.get(req, headers=headers)
        if rsp.status_code != 200:
            print "GET", uri, "returned httpstatus:", rsp.status_code
            return False
        rspJson = json.loads(rsp.text)
        attributesJson = rspJson['attributes']
        
        if len(attributesJson) > 0:
            attrDict = {}
            jsonOut['attributes'] = attrDict
            for item in attributesJson:
                name = item['name']   
                ok = self.dumpAttribute(uri + '/' + name, attrDict)
                if not ok:
                    return False
        return True
        
    def dumpLink(self, obj_uri, jsonOut):
        req = self.endpoint + obj_uri 
        headers = {'host': self.domain}
        rsp = requests.get(req, headers=headers)
        if rsp.status_code != 200:
            print "GET", obj_uri, "returned httpstatus:", rsp.status_code
            return False
        rspJson = json.loads(rsp.text)
        name = rspJson['name']
        jsonOut[name] = rspJson
        return True
        
    def dumpLinks(self, uri, jsonOut):
        req = self.endpoint + uri 
        headers = {'host': self.domain}
        rsp = requests.get(req, headers=headers)
        if rsp.status_code != 200:
            print "GET", uri, "returned httpstatus:", rsp.status_code
            return False
        rspJson = json.loads(rsp.text)
        linksJson = rspJson['links']
        
        if len(linksJson) > 0:
            linkDict = {}
            jsonOut['links'] = linkDict
            for item in linksJson:
                name = item['name']   
                ok = self.dumpLink(uri + '/' + name, linkDict)
                if not ok:
                    return False
        return True
       
        
    def dumpGroup(self, uri, jsonOut):
        req = self.endpoint + uri
        headers = {'host': self.domain}
        rsp = requests.get(req, headers=headers)
        if rsp.status_code != 200:
            print "GET /groups/", group_uuid, "returned httpstatus:", rsp.status_code
            return False
        rspJson = json.loads(rsp.text)
        group_uuid = rspJson['id'] 
        jsonOut[group_uuid] = rspJson 
        ok = self.dumpLinks(uri + '/links', jsonOut[group_uuid]) 
        if not ok:
            return False
        
        ok = self.dumpAttributes(uri + '/attributes', jsonOut[group_uuid]) 
        if not ok:
            return False
        return True
        
        
    def dumpGroups(self):
        req = self.endpoint + "/groups" 
        headers = {'host': self.domain}
        rsp = requests.get(req, headers=headers)
        if rsp.status_code != 200:
            print "GET /groups returned httpstatus:", rsp.status_code
            return False
        jsonOut = {}
        
        self.json['groups'] = jsonOut
        
        rspJson = json.loads(rsp.text)
        groupIds = rspJson['groups']
        groupIds.append(self.json['root'])  # add in root group
        for group_uuid in groupIds:
            uri = "/groups/" + group_uuid
            ok = self.dumpGroup(uri, jsonOut)
            if not ok:
                return False
        return True
        
    def dumpDataset(self, uri, jsonOut):
        req = self.endpoint + uri
        headers = {'host': self.domain}
        rsp = requests.get(req, headers=headers)
        if rsp.status_code != 200:
            print "GET ", uri, "returned httpstatus:", rsp.status_code
            return False
        rspJson = json.loads(rsp.text)
        dset_uuid = rspJson['id'] 
        jsonOut[dset_uuid] = rspJson 
        
        req = self.endpoint + uri + '/value'
        rsp = requests.get(req, headers=headers)
        if rsp.status_code != 200:
            print "GET ", uri, "returned httpstatus:", rsp.status_code
            return False
        rspJson = json.loads(rsp.text)
        jsonOut[dset_uuid]['value'] = rspJson['value']
         
        ok = self.dumpAttributes(uri + '/attributes', jsonOut[dset_uuid]) 
        if not ok:
            return False
        return True
        
    def dumpDatasets(self):
        req = self.endpoint + "/datasets" 
        headers = {'host': self.domain}
        rsp = requests.get(req, headers=headers)
        if rsp.status_code != 200:
            print "GET /datasets returned httpstatus:", rsp.status_code
            return False
        jsonOut = {}
        
        self.json['datasets'] = jsonOut
        
        rspJson = json.loads(rsp.text)
        datasetIds = rspJson['datasets']
        
        for dset_uuid in datasetIds:
            uri = "/datasets/" + dset_uuid
            ok = self.dumpDataset(uri, jsonOut)
            if not ok:
                return False
        return True
        
    def dumpDatatype(self, uri, jsonOut):
        req = self.endpoint + uri
        headers = {'host': self.domain}
        rsp = requests.get(req, headers=headers)
        if rsp.status_code != 200:
            print "GET ", uri, "returned httpstatus:", rsp.status_code
            return False
        rspJson = json.loads(rsp.text)
        dtype_uuid = rspJson['id'] 
        jsonOut[dtype_uuid] = rspJson 
         
        ok = self.dumpAttributes(uri + '/attributes', jsonOut[dtype_uuid]) 
        if not ok:
            return False
        return True
        
    def dumpDatatypes(self):
        req = self.endpoint + "/datatypes" 
        headers = {'host': self.domain}
        rsp = requests.get(req, headers=headers)
        if rsp.status_code != 200:
            print "GET /datatypes returned httpstatus:", rsp.status_code
            return False
        jsonOut = {}
        
        self.json['datatypes'] = jsonOut
        
        rspJson = json.loads(rsp.text)
        datatypeIds = rspJson['datatypes']
        
        for dtype_uuid in datatypeIds:
            uri = "/datatypes/" + dtype_uuid
            ok = self.dumpDatatype(uri, jsonOut)
            if not ok:
                return False
        return True
             
    
    def dumpDomain(self):
        req = self.endpoint + "/"
        headers = {'host': self.domain}
        rsp = requests.get(req, headers=headers)
        if rsp.status_code != 200:
            print "GET / returned httpstatus:", rsp.status_code
            return
        self.json = json.loads(rsp.text)
        
        ok = self.dumpGroups()
        
        if ok:
            ok = self.dumpDatasets()
            
        if ok:
            ok = self.dumpDatatypes()
            
        if ok:
            print json.dumps(self.json, sort_keys=True, indent=4)
           

def main():
    if len(sys.argv) < 2:
        print "usage: dumpjson <domain>"
        sys.exit(); 
        
    dumper = DumpJson()
    dumper.endpoint = "http://127.0.0.1:5000"
    dumper.domain = sys.argv[1]
    dumper.dumpDomain()
    
     

main()

    
	
