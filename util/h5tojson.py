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


"""
DumpJson - return json representation of all objects within the given file
"""

class DumpJson:
    def __init__(self, db):
        self.db = db
        self.json = {}
        
    def dumpAttribute(self, col_name, uuid, attr_name):
        item = self.db.getAttributeItem(col_name, uuid, attr_name)
        if 'ctime' in item:
            del item['ctime']
        if 'mtime' in item:
            del item['mtime']
        return item
     
        
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
        item = self.db.getDatasetItemByUuid(uuid)
        if 'ctime' in item:
            del item['ctime']
        if 'mtime' in item:
            del item['mtime']
        if 'attributeCount' in item:
            del item['attributeCount']
        attributes = self.dumpAttributes('datasets', uuid)
        item['attributes'] = attributes
        value = self.db.getDatasetValuesByUuid(uuid)
        item['value'] = value
        return item
        
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
    print filepath
    with Hdf5db(filepath, readonly=True) as db:
        dumper = DumpJson(db)
        dumper.dumpFile()    

main()

    
	
