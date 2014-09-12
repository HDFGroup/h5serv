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
import time
import signal
import logging
import os
import os.path as op
import posixpath as pp
import json
import tornado.httpserver
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url, HTTPError
from tornado.escape import json_encode, json_decode, url_escape, url_unescape
from sets import Set
import config
from hdf5db import Hdf5db

"""

""" 

def getFileModCreateTimes(filePath):
    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filePath)
    return (mtime, ctime)

def getFilePath(host):
    print 'host:', host
    topdomain = config.get('domain')
    if len(host) <= len(topdomain) or host[-len(topdomain):].lower() != topdomain:
        raise HTTPError(403, message='top-level domain is not valid')
        
    if host[-(len(topdomain) + 1)] != '.':
        # there needs to be a dot separator
        raise HTTPError(400, message='domain name is not valid')
    
    host = host[:-(len(topdomain)+1)]   # strip off top domain part
    
    if len(host) == 0 or host[0] == '.':
        # needs a least one character (which can't be '.')
        raise HTTPError(400, message='domain name is not valid')
        
    filePath = config.get('datapath')
    while len(host) > 0:
        if len(filePath) > 0 and filePath[len(filePath) - 1] != '/':
            filePath += '/'  # add a directory separator
        npos = host.rfind('.')
        if npos < 0:
            filePath += host
            host = ''
        elif npos == 0 or npos == len(host) - 1:
            raise HTTPError(400) # Bad syntax
        else:     
            filePath += host[(npos+1):]
            host = host[:npos]

    filePath += ".h5"   # add extension
    
    logging.info('getFilePath[' + host + '] -> "' + filePath + '"')
    
    return filePath
        
    
def getDomain(filePath):
    # Get domain given a file path
    domain = op.basename(filePath)[:-3]
    dirname = op.dirname(filePath)
    while len(dirname) > 0 and not op.samefile(dirname, config.get('datapath')):
        domain += '.'
        domain += op.basename(dirname)
        dirname = op.dirname(dirname)
    domain += '.'
    domain += config.get('domain')
      
    return domain 

def verifyFile(filePath, writable=False):
    logging.info("filePath: " + filePath)
    if not op.isfile(filePath):
        raise HTTPError(404)  # not found
    if not Hdf5db.isHDF5File(filePath):
        logging.warning('this is not a hdf5 file!')
        raise HTTPError(404)
    if writable and not os.access(filePath, os.W_OK):
        logging.warning('attempting update of read-only file')
        raise HTTPError(403)

def makeDirs(filePath):
    # Make any directories along path as needed
    if len(filePath) == 0 or op.isdir(filePath):
        return
    logging.info('makeDirs filePath: [' + filePath + ']')
    topdomain = config.get('domain')
    dirname = op.dirname(filePath)
    
    if len(dirname) >= len(filePath):
        logging.warning('makeDirs - unexpected dirname')
        return
    makeDirs(dirname)  # recursive call
    logging.info('mkdir("' + filePath + '")')
    os.mkdir(filePath)  # should succeed since parent directory is created   
    
class DefaultHandler(RequestHandler):
    def put(self):
        logging.warning("got default put request")
        logging.warning(self.request)
        
    def get(self):
        logging.warning("got default get request")
        logging.warning(self.request)
        
    def delete(self):
        logging.warning("got default delete request")
        logging.warning(self.request)
        
class LinkHandler(RequestHandler):
    def getRequestId(self, uri):
        # helper method
        # uri should be in the form: /groups/<uuid>/links
        # extract the <uuid>
        uri = self.request.uri
        if uri[:len('/groups/')] != '/groups/':
            # should not get here!
            logging.error("unexpected uri: " + uri)
            raise HTTPError(500)
        uri = uri[len('/groups/'):]  # get stuff after /groups/
        npos = uri.find('/')
        if npos <= 0:
            logging.info("bad uri")
            raise HTTPError(400)  
        id = uri[:npos]
         
        logging.info('got id: [' + id + ']')
    
        return id
        
    def getName(self, uri):
        # helper method
        # uri should be in the form: /group/<uuid>/links/<name>
        # this method returns name
        npos = uri.find('/links/')
        if npos < 0:
            # shouldn't be possible to get here
            logging.info("unexpected uri")
            raise HTTPError(500)
        if npos+len('/links/') >= len(uri):
            # no name specified
            logging.info("no name specified")
            raise HTTPError(400)
        linkName = uri[npos+len('/links/'):]
        if linkName.find('/') >= 0:
            # can't have '/' in link name
            logging.info("invalid linkname")
            raise HTTPError(400)
        return linkName
        
    def get(self):
        logging.info('LinkHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
         
        
        reqUuid = self.getRequestId(self.request.uri)
        domain = self.request.host
        filePath = getFilePath(domain) 
        
        # Get optional query parameters
        limit = self.get_query_argument("Limit", 0)
        if type(limit) is not int:
            try:
                limit = int(limit)
            except ValueError:
                logging.info("expected int type for limit")
                raise HTTPError(400) 
        marker = self.get_query_argument("Marker", None)
        classFilter = self.get_query_argument("ClassFilter", None)
                
        ctime = op.getctime(filePath)
        mtime = ctime
        response = { }
        
        verifyFile(filePath)
        items = None
        with Hdf5db(filePath) as db:
            items = db.getItems(reqUuid, classFilter, marker, limit)
            if items == None:
                httpError = 404  # not found
                #todo: return 410 if the group was recently deleted
                logging.info("group: [" + reqUuid + "] not found");
                raise HTTPError(httpError)
                         
        # got everything we need, put together the response
        links = [ ]
        for item in items:
            href = self.request.protocol + '://' + domain + '/'
            selfref = href + 'groups/' + reqUuid + '/links/' + item['name']
            if item['class'] == 'Dataset':
                href += 'datasets/' + item['uuid']
                links.append({'id': item['uuid'], 'name': item['name'], 'rel': 'Dataset',
                    'self': selfref, 'href': href, 'attributeCount': item['attributeCount']})
            elif item['class'] == 'Group':
                href += 'groups/' + item['uuid']
                links.append({'id': item['uuid'], 'name': item['name'], 'rel': 'Group',
                    'self': selfref, 'href': href, 'attributeCount': item['attributeCount']})
            elif item['class'] == 'Datatype':
                href += 'datatypes/' + item['uuid']
                links.append({'id': item['uuid'], 'name': item['name'], 'rel': 'Datatype',
                    'self': selfref, 'href': href})
            elif item['class'] == 'SoftLink':
                href += 'search?hdf5={' + item['path'] + '}'
                links.append({'name': item['name'], 'rel': 'SoftLink', 'self': selfref,
                    'href': href})
            elif item['class'] == 'ExternalLink':
                href = 'external link' # todo
                links.append({'name': item['name'], 'rel': 'ExternalLink', 'self': selfref,
                    'href': href})
            else:
                logging.error("unexpected group item class: " + item['class'])
                raise HTTPError(500);
             
        response['links'] = links
        
        self.write(response)
    
    def put(self):
        logging.info('LinkHandler.put host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        # put - create a new link
        # patterns are:
        # PUT /group/<id>/links/<name> {id: <id> } 
        # PUT /group/<id>/links/<name> {h5path: <path> } 
        # PUT /group/<id>/links/<name> {href: <href> }
        uri = self.request.uri
        reqUuid = self.getRequestId(self.request.uri)
        
        linkName = url_unescape(self.getName(self.request.uri))
        
        print "name: [", linkName, "] parentUuid:", reqUuid
        
        body = json.loads(self.request.body)
        
        childUuid = None
        h5path = None
        
        if "id" in body:
            childUuid = body["id"]
        elif "h5path" in body:
            # todo
            h5path = body["h5path"]
        elif "href" in body:
            #todo
            raise HTTPError(501)   # not implemented
        else: 
            logging.info("bad query syntax: [" + self.request.body + "]")
            raise HTTPError(400)
                        
        
        domain = self.request.host
        filePath = getFilePath(domain) 
        
        ctime = op.getctime(filePath)
        mtime = ctime
        response = { }
        
        verifyFile(filePath)
        items = None
        rootUUID = None
        with Hdf5db(filePath) as db:
            if childUuid:
                ok = db.linkObject(reqUuid, childUuid, linkName)
            elif h5path:
                ok = db.createSoftLink(reqUuid, h5path, linkName)
            else:
                raise HTTPError(500)
            if not ok:
                httpStatus = 500
                if db.httpStatus != 200:
                    httpStatus = db.httpStatus
                raise HTTPError(httpStatus)
            rootUUID = db.getUUIDByPath('/')
            
        response['title'] = linkName
        if childUuid:
            response['idref'] = childUuid
        elif h5path:
            response['hdf5'] = h5path
        else:
            pass   # todo - external link
        links = []
        href = self.request.protocol + '://' + domain + '/groups/'
        links.append({'rel': 'group', 'href': href + reqUuid})
        links.append({'rel': 'links', 'href': href + reqUuid + '/links'})
        links.append({'rel': 'root',  'href': href + rootUUID})
        links.append({'rel': 'self',  'href': href +  reqUuid + '/links/' + linkName})
        response['links'] = links
        self.write(response)    
        
    def delete(self): 
        logging.info('LinkHandler.delete ' + self.request.host)   
        print "uri: ", self.request.uri 
        reqUuid = self.getRequestId(self.request.uri)
        
        linkName = self.getName(self.request.uri)
        
        logging.info( " delete link  name[: " + linkName + "] parentUuid: " + reqUuid)
           
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        with Hdf5db(filePath) as db:
            ok = db.unlinkItem(reqUuid, linkName)
            if not ok:
                httpStatus = db.httpStatus
                if httpStatus == 200:
                    httpStatus = 500
                raise HTTPError(httpStatus)   
                
class DatasetHandler(RequestHandler):
    # supported datatypes
    _dtypes = Set([    'int8',        'int16',   'int32',  'int64',
                      'uint8',       'uint16',  'uint32', 'uint64',
                    'float16',      'float32', 'float64',
                  'complex64',   'complex128',
                 'vlen_bytes', 'vlen_unicode'])
    # or 'Snn' for fixed string or 'vlen_bytes' for variable 
    def getRequestId(self):
        # request is in the form /datasets/<id>, return <id>
        uri = self.request.uri
        npos = uri.rfind('/')
        if npos < 0:
            raise HTTPError(500)  # should not get routed to ValueHandler in this case
        if npos == len(uri) - 1:
            raise HTTPError(400, message="missing id")
        id = uri[(npos+1):]
        logging.info('got id: [' + id + ']')
    
        return id
        
    def get(self):
        logging.info('DatasetHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        #todo - use the real object creation times
        ctime = op.getctime(filePath)
        mtime = ctime
        response = { }
        links = []
        rootUUID = None
        item = None
        with Hdf5db(filePath) as db:
            item = db.getDatasetItemByUuid(reqUuid)
            if item == None:
                httpError = 404  # not found
                if db.httpStatus != 200:
                    httpError = db.httpStatus # library may have more specific error code
                logging.info("dataset: [" + reqUuid + "] not found");
                raise HTTPError(httpError)
            rootUUID = db.getUUIDByPath('/')
                         
        # got everything we need, put together the response
        href = self.request.protocol + '://' + domain + '/'
        links.append({'rel:': 'self',       'href': href + 'datasets/' + reqUuid})
        links.append({'rel:': 'root',       'href': href + 'groups/' + rootUUID}) 
        links.append({'rel:': 'attributes', 'href': href + 'datasets/' + reqUuid + '/attributes'})        
        response['id'] = reqUuid
        response['type'] = item['type']
        response['shape'] = item['shape']
        response['created'] = ctime
        response['lastModified'] = mtime
        response['attributeCount'] = item['attributeCount']
        response['links'] = links
        
        self.write(response)
        
    def post(self):
        logging.info('DatasetHandler.post host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        if self.request.uri != '/datasets/':
            logging.info('bad datasets post request')
            raise HTTPError(405)  # Method not allowed
               
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        
        body = json.loads(self.request.body)
        
        if "shape" not in body:
            logging.info("Shape not supplied")
            raise HTTPError(400)  # missing shape
            
        if "type" not in body:
            logging.info("Type not supplied")
            raise HTTPError(400)  # missing type
            
        shape = body["shape"]
        datatype = body["type"]
        if type(shape) == int:
            dim1 = shape
            shape = []
            shape = [dim1]
        elif type(shape) == list or type(shape) == tuple: 
            pass # can use as is
        else:
            logging.info("invalid shape argument")
            raise HTTPError(400)
            
        # validate type
        isValid = False 
        if datatype in DatasetHandler._dtypes:
            isValid = True
        elif len(datatype) > 1 and datatype[0] == 'S':
            # Fixed ascii datatype, very the text after 'S' is a positive int
            try:
                nwidth = int(datatype[1:])
                if nwidth > 0:
                    isValid = True              
            except ValueError:
                logging.info("can't convert text after 'S' in: " + datatype + " to int")           
        else:
            logging.info("invalid type argument: " + datatype);
            raise HTTPError(400)
            
        # validate shape
        for extent in shape:
            if type(extent) != int:
                logging.info("invalid shape type")
                raise HTTPError(400)
            if extent < 0:
                logging.info("invalid shape (negative extent)")
                raise HTTPError(400)           
        
        with Hdf5db(filePath) as db:
            rootUUID = db.getUUIDByPath('/')
            dsetUUID = db.createDataset(shape, datatype)
                
        ctime = time.time()
        mtime = ctime
         
        response = { }
      
        # got everything we need, put together the response
        links = [ ]
        href = self.request.protocol + '://' + domain + '/'
        links.append({'rel:': 'self',       'href': href + 'datasets/' + dsetUUID})
        links.append({'rel:': 'root',       'href': href + 'groups/' + rootUUID}) 
        links.append({'rel:': 'attributes', 'href': href + 'datasets/' + dsetUUID + '/attributes'})        
        response['id'] = dsetUUID
        response['created'] = ctime
        response['lastModified'] = mtime
        response['attributeCount'] = 0
        response['linkCount'] = 0
        response['links'] = links
        
        self.write(response)  
        
    def delete(self): 
        logging.info('DatasetHandler.delete ' + self.request.host)   
        uuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        with Hdf5db(filePath) as db:
            ok = db.deleteObjectByUuid(uuid)
            if not ok:
                httpStatus = db.httpStatus
                if httpStatus == 200:
                    httpStatus = 500
                raise HTTPError(httpStatus)  
                
class ValueHandler(RequestHandler):
    """
    Helper method - return slice for dim based on query params
    """
    def getSliceQueryParam(self, dim, extent):
        # Get optional query parameters for given dim
        dimQuery = 'dim' + str(dim + 1)
        try:
            start = int(self.get_query_argument(dimQuery + '_start', 0))
            stop =  int(self.get_query_argument(dimQuery + '_stop', extent))
            step =  int(self.get_query_argument(dimQuery + '_step', 1))
        except ValueError:
            logging.info("invalid selection parameter (can't convert to int)");
            raise HTTPError(400)
        if start < 0 or start > extent:
            logging.info("bad selection start parameter for dimension: " + dimQuery)
            raise HTTPError(400)
        if stop > extent:
            logging.info("bad selection stop parameter for dimension: " + dimQuery)
            raise HTTPError(400)
        if step == 0:
            logging.info("bad selection step parameter for dimension: " + dimQuery)
            raise HTTPError(400)
        s = slice(start, stop, step)
        logging.info(dimQuery + " start: " + str(start) + " stop: " + str(stop) + " step: " + 
            str(step)) 
        return s
        
    """
    Helper method - get uuid for the dataset
    """    
    def getRequestId(self):
        # request is in the form /datasets/<id>/value?xxx, return <id>
        uri = self.request.uri
        if uri[:len('/datasets/')] != '/datasets/':
            # should not get here!
            logging.error("unexpected uri: " + uri)
            raise HTTPError(500)
        uri = uri[len('/datasets/'):]  # get stuff after /datasets/
        npos = uri.find('/')
        if npos <= 0:
            logging.info("bad uri")
            raise HTTPError(400)  
        id = uri[:npos]
         
        logging.info('got id: [' + id + ']')
    
        return id
        
    def get(self):
        logging.info('ValueHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        #todo - use the real object creation times
        ctime = op.getctime(filePath)
        mtime = ctime
        response = { }
        links = []
        rootUUID = None
        item = None
        values = None
        with Hdf5db(filePath) as db:
            item = db.getDatasetItemByUuid(reqUuid)
            if item == None:
                httpError = 404  # not found
                if db.httpStatus != 200:
                    httpError = db.httpStatus # library may have more specific error code
                logging.info("dataset: [" + reqUuid + "] not found");
                raise HTTPError(httpError)
            shape = item['shape']
            rank = len(shape)
            slices = []
            for dim in range(rank):
                slice = self.getSliceQueryParam(dim, shape[dim])
                slices.append(slice)
         
            values = db.getDatasetValuesByUuid(reqUuid, tuple(slices))  
            rootUUID = db.getUUIDByPath('/')
                         
        # got everything we need, put together the response
        href = self.request.protocol + '://' + domain + '/'
        links.append({'rel:': 'self',       'href': href + 'datasets/' + reqUuid})
        links.append({'rel:': 'root',       'href': href + 'groups/' + rootUUID}) 
        links.append({'rel:': 'attributes', 'href': href + 'datasets/' + reqUuid + '/attributes'})        
        response['id'] = reqUuid
        response['type'] = item['type']
        response['shape'] = item['shape']
        response['created'] = ctime
        response['lastModified'] = mtime
        response['values'] = values
        response['links'] = links
        
        self.write(response)   
         
class GroupHandler(RequestHandler):
    def getRequestId(self):
        uri = self.request.uri
        npos = uri.rfind('/')
        if npos < 0:
            raise HTTPError(500)  # should not get routed to GroupHandler in this case
        if npos == len(uri) - 1:
            raise HTTPError(400, message="missing id")
        id = uri[(npos+1):]
        logging.info('got id: [' + id + ']')
    
        return id
            
    def get(self):
        logging.info('GroupHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        print self.request
        print "uri: ", self.request.uri    
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        #todo - use the real object creation times
        ctime = op.getctime(filePath)
        mtime = ctime
        response = { }
             
        links = []
        rootUUID = None
        item = None
        with Hdf5db(filePath) as db:
            item = db.getGroupItemByUuid(reqUuid)
            if item == None:
                httpError = 404  # not found
                if db.httpStatus != 200:
                    httpError = db.httpStatus # library may have more specific error code
                logging.info("group: [" + reqUuid + "] not found");
                raise HTTPError(httpError)
            rootUUID = db.getUUIDByPath('/')
                         
        # got everything we need, put together the response
        href = self.request.protocol + '://' + domain + '/'
        links.append({'rel:': 'self',       'href': href + 'groups/' + reqUuid})
        links.append({'rel:': 'links',      'href': href + 'groups/' + reqUuid + 'links'})
        links.append({'rel:': 'root',       'href': href + 'groups/' + rootUUID}) 
        links.append({'rel:': 'attributes', 'href': href + 'groups/' + reqUuid + '/attributes'})        
        response['id'] = reqUuid
        response['created'] = ctime
        response['lastModified'] = mtime
        response['attributeCount'] = item['attributeCount']
        response['linkCount'] = item['linkCount']
        response['links'] = links
        
        self.write(response)
        
    def post(self):
        logging.info('GroupHandler.post host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        print self.request
        print "uri: ", self.request.uri 
        if self.request.uri != '/groups/':
            logging.info('bad group post request')
            raise HTTPError(405)  # Method not allowed
               
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        
        with Hdf5db(filePath) as db:
            rootUUID = db.getUUIDByPath('/')
            grpUUID = db.createGroup()
                
        ctime = time.time()
        mtime = ctime
         
        response = { }
      
        # got everything we need, put together the response
        links = [ ]
        href = self.request.protocol + '://' + domain + '/'
        links.append({'rel:': 'self',       'href': href + 'groups/' + grpUUID})
        links.append({'rel:': 'links',      'href': href + 'groups/' + grpUUID + '/links'})
        links.append({'rel:': 'root',       'href': href + 'groups/' + rootUUID}) 
        links.append({'rel:': 'attributes', 'href': href + 'groups/' + grpUUID + '/attributes'})        
        response['id'] = grpUUID
        response['created'] = ctime
        response['lastModified'] = mtime
        response['attributeCount'] = 0
        response['linkCount'] = 0
        response['links'] = links
        
        self.write(response)  
        
    def delete(self): 
        logging.info('GroupHandler.delete ' + self.request.host)   
        print "uri: ", self.request.uri    
        uuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        with Hdf5db(filePath) as db:
            ok = db.deleteObjectByUuid(uuid)
            if not ok:
                httpStatus = db.httpStatus
                if httpStatus == 200:
                    httpStatus = 500
                raise HTTPError(httpStatus)     
        
class RootHandler(RequestHandler):
    def getRootResponse(self, filePath):
        # used by GET / and PUT /
        domain = self.request.host
        filePath = getFilePath(domain)
        with Hdf5db(filePath) as db:
            rootUUID = db.getUUIDByPath('/')
            datasetCount = db.getNumberOfDatasets()
            groupCount = db.getNumberOfGroups()
            datatypeCount = db.getNumberOfDatatypes()
         
        # generate response 
        links = [ ]
        href = self.request.protocol + '://' + domain + '/'
        links.append({'rel:': 'self', 'href': href})
        links.append({'rel:': 'database', 'href': href + 'datasets'})
        links.append({'rel:': 'linkbase', 'href': href + 'groups'})
        links.append({'rel:': 'typebase', 'href': href + 'datatypes' })
        links.append({'rel:': 'root',     'href': href + 'groups/' + rootUUID})
            
        response = {  }
        response['created'] = op.getctime(filePath)
        response['lastModified'] = op.getmtime(filePath)
        response['datasetCount'] = datasetCount
        response['groupCount'] = groupCount
        response['typeCount'] = datatypeCount
        response['root'] = rootUUID
        response['links'] = links
      
        return response
        
    def get(self):
        logging.info('RootHandler.get ' + self.request.host)
        # get file path for the domain
        # will raise exception if not found
        filePath = getFilePath(self.request.host)
        verifyFile(filePath)
        response = self.getRootResponse(filePath)
        
        self.write(response) 
        
    def put(self): 
        logging.info('RootHandler.put ' + self.request.host)  
        filePath = getFilePath(self.request.host)
        logging.info("put filePath: " + filePath)
        if op.isfile(filePath):
            logging.info("path exists")
            raise HTTPError(409)  # Conflict - is this the correct code?
        # create directories as needed
        makeDirs(op.dirname(filePath))
        logging.info("creating file: [" + filePath + "]")
        if not Hdf5db.createHDF5File(filePath):
            logging.error("unexpected error creating HDF5: " + filePath)
            raise HTTPError(500)
        response = self.getRootResponse(filePath)
        
        self.write(response)
          
    def delete(self): 
        logging.info('RootHandler.delete ' + self.request.host)   
        filePath = getFilePath(self.request.host)
        verifyFile(filePath, True)
        
        if not op.isfile(filePath):
            # file not there
            raise HTTPError(404)  # Not found
             
        if not os.access(filePath, os.W_OK):
            # file is read-only
            raise HTTPError(403) # Forbidden
            
        os.remove(filePath)    
        
def sig_handler(sig, frame):
    logging.warning('Caught signal: %s', sig)
    IOLoop.instance().add_callback(shutdown)
 
def shutdown():
    MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 2
    logging.info('Stopping http server')
    server.stop()
 
    logging.info('Will shutdown in %s seconds ...', MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
    io_loop = tornado.ioloop.IOLoop.instance()
 
    deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN
 
    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
            logging.info('Shutdown')
    stop_loop() 
    
    logging.info("closing db")

def make_app():
    isDebug = False 
    if config.get('debug'):
        isDebug = True
    app = Application( [
        url(r"/datasets/.*/value", ValueHandler),
        url(r"/datasets/.*/value\?.*", ValueHandler),
        url(r"/datasets/.*", DatasetHandler),
        url(r"/datasets/", DatasetHandler),
        url(r"/groups/.*/links", LinkHandler),
        url(r"/groups/.*/links/.*", LinkHandler),
        url(r"/groups/", GroupHandler), 
        url(r"/groups/.*", GroupHandler), 
        url(r"/", RootHandler),
        url(r".*", DefaultHandler)
    ],
    debug=isDebug)
    return app

def main():
    # os.chdir(config.get('datapath'))
    logging.basicConfig(level=logging.DEBUG)
    port = config.get('port')
    global server
    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(port)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    logging.info("INITIALIZING...")
    print "Starting event loop on port: ", port
    IOLoop.current().start()

main()
