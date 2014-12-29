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

sys.path.append('../server')
from fileUtil import getLinkTarget
from hdf5db import Hdf5db
import hdf5dtype 


"""
DumpJson - return json representation of all objects within the given file
"""

class DumpJson:
    def __init__(self, db, options=None):
        self.options = options
        self.db = db
        self.options = options
        self.json = {}
        
    def dumpAttribute(self, col_name, uuid, attr_name):
        item = self.db.getAttributeItem(col_name, uuid, attr_name)
        response = { 'name': attr_name }
        typeItem = item['type']
        response['type'] = hdf5dtype.getTypeResponse(typeItem)
        response['shape'] = item['shape']
        if not self.options.H:
            response['value'] = item['value']   # dump values unless header flag was passed
        return response
     
        
    def dumpAttributes(self, col_name, uuid):
        attr_list = self.db.getAttributeItems(col_name, uuid)
        items = []
        for attr in attr_list:
            item = self.dumpAttribute(col_name, uuid, attr['name'])
            items.append(item)
                   
        return items      
    
    def dumpLinks(self, uuid):
        link_list = self.db.getLinkItems(uuid)
        items = []
        for link in link_list:
            item = {}
            link_target = getLinkTarget(link)
            item['title'] = link['name']
            item['href'] = link_target
            items.append(item)
        return items
       
        
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
        if 'id' in item:
            del item['id']
        attributes = self.dumpAttributes('groups', uuid)
        if attributes:
            item['attributes'] = attributes
        links = self.dumpLinks(uuid)
        if links:
            item['links'] = links
        return item
        
        
    def dumpGroups(self):
        groups = {}
        item = self.dumpGroup(self.root_uuid)
        groups[self.root_uuid] = item
        uuids = self.db.getCollection("groups") 
        for uuid in uuids:
            item = self.dumpGroup(uuid)
            groups[uuid] = item
        
        self.json['groups'] = groups
        
        
    def dumpDataset(self, uuid):
        response = { }
        item = self.db.getDatasetItemByUuid(uuid)
        response['alias'] = item['alias']
        typeItem = item['type']
        response['type'] = hdf5dtype.getTypeResponse(typeItem)
        shapeItem = item['shape']
        response['shape'] = shapeItem
        if 'dims' in shapeItem and 'maxdims' in shapeItem:
            extensible = False
            dims = shapeItem['dims']
            maxdims = shapeItem['maxdims']
            for i in range(len(dims)):
                if dims[i] < maxdims[i]:
                    extensible = True
                    break
            # dump the fill value
            if extensible and 'fillvalue' in item:
                response['fillvalue'] = item['fillvalue']
        
        attributes = self.dumpAttributes('datasets', uuid)
        if attributes:
            response['attributes'] = attributes
        value = self.db.getDatasetValuesByUuid(uuid)
        
        if not self.options.H:
            response['value'] = value   # dump values unless header flag was passed
        return response
        
    def dumpDatasets(self):
        uuids = self.db.getCollection("datasets") 
        if uuids:
            datasets = {}
            for uuid in uuids:
                item = self.dumpDataset(uuid)
                datasets[uuid] = item
        
            self.json['datasets'] = datasets
        
    def dumpDatatype(self, uuid):
        response = { }
        item = self.db.getCommittedTypeItemByUuid(uuid)
        response['alias'] = item['alias']
        typeItem = item['type']
        response['type'] = hdf5dtype.getTypeResponse(typeItem)
        attributes = self.dumpAttributes('datatypes', uuid)
        if attributes:
            response['attributes'] = attributes
        return response
         
        
    def dumpDatatypes(self):    
        uuids = self.db.getCollection("datatypes") 
        if uuids:
            datatypes = {}
            for uuid in uuids:
                item = self.dumpDatatype(uuid)
                datatypes[uuid] = item
        
            self.json['datatypes'] = datatypes
        
    def dumpFile(self):
        self.root_uuid = self.db.getUUIDByPath('/')
        self.json['root'] = self.root_uuid
        
        self.dumpGroups()
        
        self.dumpDatasets()
            
        self.dumpDatatypes()
            
        print json.dumps(self.json, sort_keys=True, indent=4)
           

def main():
    parser = argparse.ArgumentParser(usage='%(prog)s [-h] [-H] <hdf5_file>')
    parser.add_argument('-H', action='store_true', help='suppress data output')
    parser.add_argument('filename', nargs='+', help='HDF5 to be converted to json')
    args = parser.parse_args()
    
    with Hdf5db(args.filename[0], readonly=True) as db:
        dumper = DumpJson(db, options=args)
        dumper.dumpFile()    
    

main()

    
	
