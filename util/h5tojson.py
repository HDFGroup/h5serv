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

sys.path.append('../server')
from hdf5db import Hdf5db
import hdf5dtype 


"""
DumpJson - return json representation of all objects within the given file
"""

class DumpJson:
    def __init__(self, db):
        self.db = db
        self.json = {}
        
    def dumpAttribute(self, col_name, uuid, attr_name):
        item = self.db.getAttributeItem(col_name, uuid, attr_name)
        response = { 'name': attr_name }
        typeItem = item['type']
        response['type'] = hdf5dtype.getTypeResponse(typeItem)
        response['shape'] = item['shape']
        response['value'] = item['value']
        return response
     
        
    def dumpAttributes(self, col_name, uuid):
        attr_list = self.db.getAttributeItems(col_name, uuid)
        items = []
        for attr in attr_list:
            item = self.dumpAttribute(col_name, uuid, attr['name'])
            items.append(item)
                   
        return items      
    
    def dumpLinks(self, uuid):
        links = self.db.getLinkItems(uuid)
        return links
       
        
    def dumpGroup(self, uuid):
        item = self.db.getGroupItemByUuid(uuid)
        if 'ctime' in item:
            del item['ctime']
        if 'mtime' in item:
            del item['mtime']
        if 'linkCount' in item:
            del item['linkCount']
        if 'attributeCount' in item:
            del item['attributeCount']
        item['id'] = uuid
        attributes = self.dumpAttributes('groups', uuid)
        item['attributes'] = attributes
        links = self.dumpLinks(uuid)
        item['links'] = links
        return item
        
        
    def dumpGroups(self):
        groupList = []
        item = self.dumpGroup(self.root_uuid)
        groupList.append(item)
        uuids = self.db.getCollection("groups") 
        for uuid in uuids:
            item = self.dumpGroup(uuid)
            groupList.append(item)
        
        self.json['groups'] = groupList
        
        
    def dumpDataset(self, uuid):
        response = { 'id': uuid }
        item = self.db.getDatasetItemByUuid(uuid)
        print json.dumps(item, sort_keys=True, indent=4)
        
        typeItem = item['type']
        response['type'] = hdf5dtype.getTypeResponse(typeItem)
        shapeItem = item['shape']
        response['shape'] = shapeItem
        if 'dims' in shapeItem and 'maxdims' in shapeItem:
            extensible = False
            dims = shapeItem['dims']
            maxdims = shapeItem['maxdims']
            print dims
            print maxdims
            for i in range(len(dims)):
                if dims[i] < maxdims[i]:
                    extensible = True
                    break
            # dump the fill value
            if extensible and 'fillvalue' in item:
                response['fillvalue'] = item['fillvalue']
        
        attributes = self.dumpAttributes('datasets', uuid)
        response['attributes'] = attributes
        value = self.db.getDatasetValuesByUuid(uuid)
        response['value'] = value
        return response
        
    def dumpDatasets(self):
        datasetList = []
        uuids = self.db.getCollection("datasets") 
        for uuid in uuids:
            item = self.dumpDataset(uuid)
            datasetList.append(item)
        
        self.json['datasets'] = datasetList
        
    def dumpDatatype(self, uuid):
        item = self.db.getCommittedTypeItemByUuid(uuid)
        if 'ctime' in item:
            del item['ctime']
        if 'mtime' in item:
            del item['mtime']
        if 'attributeCount' in item:
            del item['attributeCount']
        attributes = self.dumpAttributes('datatypes', uuid)
        item['attributes'] = attributes
        return item
        
    def dumpDatatypes(self):
        datatypeList = []
        uuids = self.db.getCollection("datatypes") 
        for uuid in uuids:
            item = self.dumpDatatype(uuid)
            datatypeList.append(item)
        
        self.json['datatypes'] = datatypeList
        
    def dumpFile(self):
        self.root_uuid = self.db.getUUIDByPath('/')
        self.json['root'] = self.root_uuid
        
        self.dumpGroups()
        
        self.dumpDatasets()
            
        self.dumpDatatypes()
            
        print json.dumps(self.json, sort_keys=True, indent=4)
           

def main():
    if len(sys.argv) < 2:
        print "usage: h5tojson <filename>"
        sys.exit(); 
    filepath = sys.argv[1]
    with Hdf5db(filepath, readonly=True) as db:
        dumper = DumpJson(db)
        dumper.dumpFile()    

main()

    
	
