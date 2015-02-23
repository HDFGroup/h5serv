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
import logging
import logging.handlers

sys.path.append('../server')
from hdf5db import Hdf5db
import hdf5dtype 


"""
DumpJson - return json representation of all objects within the given file
"""

class DumpJson:
    def __init__(self, db, options=None):
        self.options = options
        self.db = db
        self.json = {}
        
    def dumpAttribute(self, col_name, uuid, attr_name):
        item = self.db.getAttributeItem(col_name, uuid, attr_name)
        response = { 'name': attr_name }
        typeItem = item['type']
        response['type'] = hdf5dtype.getTypeResponse(typeItem)
        response['shape'] = item['shape']
        if not self.options.D:
            response['value'] = item['value']   # dump values unless header -D was passed
        return response
     
        
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
       
        
    def dumpGroup(self, uuid):
        item = self.db.getGroupItemByUuid(uuid)
        for key in ('ctime', 'mtime', 'linkCount', 'attributeCount', 'id'):
            if key in item:
                del item[key]
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
        
        if not (self.options.D or self.options.d):
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
    parser = argparse.ArgumentParser(usage='%(prog)s [-h] [-D|-d] <hdf5_file>')
    parser.add_argument('-D', action='store_true', help='surpress all data output')
    parser.add_argument('-d', action='store_true', help='surpress data output for' +
        ' datasets (but not attribute values)')
    parser.add_argument('filename', nargs='+', help='HDF5 to be converted to json')
    args = parser.parse_args()
    
    # create logger
    log = logging.getLogger("h5serv")
    log.setLevel(logging.INFO)
    # set daily rotating log
    handler = logging.FileHandler('./h5tojson.log')
    
    # add handler to logger
    log.addHandler(handler)
    log.info("h5tojson " + args.filename[0])
    
    
    with Hdf5db(args.filename[0], readonly=True) as db:
        dumper = DumpJson(db, options=args)
        dumper.dumpFile()    
    

main()

    
	
