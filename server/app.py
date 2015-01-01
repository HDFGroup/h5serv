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
import json
import tornado.httpserver
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url, HTTPError
from tornado.escape import json_encode, json_decode, url_escape, url_unescape
from urlparse import urlparse
from sets import Set
import config
from hdf5db import Hdf5db
import hdf5dtype
from timeUtil import unixTimeToUTC
from fileUtil import getFilePath, getDomain, getFileModCreateTimes, makeDirs, verifyFile

    
class DefaultHandler(RequestHandler):
    def put(self):
        log = logging.getLogger("h5serv")
        log.warning("got default PUT request")
        log.warning(self.request)
        raise HTTPError(400) 
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.warning("got default GET request")
        log.warning(self.request)
        raise HTTPError(400) 
        
    def post(self):
        log = logging.getLogger("h5serv")
        log.warning("got default POST request")
        log.warning(self.request)
        raise HTTPError(400) 
        
    def delete(self):
        log = logging.getLogger("h5serv")
        log.warning("got default DELETE request")
        log.warning(self.request)
        raise HTTPError(400) 
        
class LinkCollectionHandler(RequestHandler):
    def getRequestId(self, uri):
        log = logging.getLogger("h5serv")
        # helper method
        # uri should be in the form: /groups/<uuid>/links
        # extract the <uuid>
        uri = self.request.uri
        if uri[:len('/groups/')] != '/groups/':
            # should not get here!
            log.error("unexpected uri: " + uri)
            raise HTTPError(500)
        uri = uri[len('/groups/'):]  # get stuff after /groups/
        npos = uri.find('/')
        if npos <= 0:
            log.info("bad uri")
            raise HTTPError(400)  
        id = uri[:npos]
         
        log.info('got id: [' + id + ']')
    
        return id
        
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('LinkCollectionHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')       
        
        reqUuid = self.getRequestId(self.request.uri)
        domain = self.request.host
        filePath = getFilePath(domain) 
        
        # Get optional query parameters
        limit = self.get_query_argument("Limit", 0)
        if type(limit) is not int:
            try:
                limit = int(limit)
            except ValueError:
                log.info("expected int type for limit")
                raise HTTPError(400) 
        marker = self.get_query_argument("Marker", None)
                
        response = { }
        
        verifyFile(filePath)
        items = None
        rootUUID = None
        with Hdf5db(filePath, app_logger=log) as db:
            items = db.getLinkItems(reqUuid, marker=marker, limit=limit)
            if items == None:
                httpError = 404  # not found
                #todo: return 410 if the group was recently deleted
                log.info("group: [" + reqUuid + "] not found")
                raise HTTPError(httpError)
            rootUUID = db.getUUIDByPath('/')
                         
        # got everything we need, put together the response
        links = []
        hrefs = []
        for item in items:
            for key in ('mtime', 'ctime', 'type', 'href'):
                if key in item:
                    del item[key]
            links.append(item)
             
        response['links'] = links
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',       'href': href + 'groups/' + reqUuid + '/links'})
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'home',       'href': href }) 
        hrefs.append({'rel': 'owner', 'href': href + 'groups/' + reqUuid})  
        response['hrefs'] = hrefs      
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
    
        
class LinkHandler(RequestHandler):
    def getRequestId(self, uri):
        log = logging.getLogger("h5serv")
        # helper method
        # uri should be in the form: /groups/<uuid>/links/<name>
        # extract the <uuid>
        uri = self.request.uri
        if uri[:len('/groups/')] != '/groups/':
            # should not get here!
            log.error("unexpected uri: " + uri)
            raise HTTPError(500)
        uri = uri[len('/groups/'):]  # get stuff after /groups/
        npos = uri.find('/')
        if npos <= 0:
            log.info("bad uri")
            raise HTTPError(400)  
        id = uri[:npos]
         
        log.info('got id: [' + id + ']')
    
        return id
        
    def getName(self, uri):
        log = logging.getLogger("h5serv")
        # helper method
        # uri should be in the form: /group/<uuid>/links/<name>
        # this method returns name
        npos = uri.find('/links/')
        if npos < 0:
            # shouldn't be possible to get here
            log.info("unexpected uri")
            raise HTTPError(500)
        if npos+len('/links/') >= len(uri):
            # no name specified
            log.info("no name specified")
            raise HTTPError(400)
        linkName = uri[npos+len('/links/'):]
        if linkName.find('/') >= 0:
            # can't have '/' in link name
            log.info("invalid linkname")
            raise HTTPError(400)
        return linkName
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('LinkHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')       
        
        reqUuid = self.getRequestId(self.request.uri)
        domain = self.request.host
        filePath = getFilePath(domain) 
        linkName = self.getName(self.request.uri)
        
        response = { }
        
        verifyFile(filePath)
        items = None
        rootUUID = None
        with Hdf5db(filePath, app_logger=log) as db:
            item = db.getLinkItemByUuid(reqUuid, linkName)
            if item == None:
                log.info("group: [" + reqUuid + "], link: [" + linkName + "] not found")
                raise HTTPError(db.httpStatus)
            rootUUID = db.getUUIDByPath('/')
                         
        # got everything we need, put together the response
        targethref = ''
        if 'href' in item:
            targethref = item['href']
            
        response['lastModified'] = unixTimeToUTC(item['mtime'])
        response['created'] = unixTimeToUTC(item['ctime'])
        for key in ('mtime', 'ctime', 'href'):
            if key in item:
                del item[key]
        response['link'] = item
        
         
        hrefs = []     
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',       'href': href + 'groups/' + reqUuid + 
            '/links/' + url_escape(linkName)})
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'home',       'href': href }) 
        hrefs.append({'rel': 'owner', 'href': href + 'groups/' + reqUuid})  
        
        if targethref:
            if item['class'] == 'H5L_TYPE_HARD' or item['class'] == 'H5L_TYPE_SOFT':
                hrefs.append({'rel': 'target', 'href': href + targethref})
            elif item['class'] == 'H5L_TYPE_EXTERNAL':
                link_href = self.request.protocol + '://' +  getDomain(item['file'])
                hrefs.append({'rel': 'target', 'href': link_href + targethref})
        response['hrefs'] = hrefs      
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
    
    def put(self):
        log = logging.getLogger("h5serv")
        log.info('LinkHandler.put host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        # put - create a new link
        # patterns are:
        # PUT /group/<id>/links/<name> {id: <id> } 
        # PUT /group/<id>/links/<name> {h5path: <path> } 
        # PUT /group/<id>/links/<name> {href: <href> }
        uri = self.request.uri
        reqUuid = self.getRequestId(self.request.uri)
        
        linkName = url_unescape(self.getName(self.request.uri))
        
        body = json.loads(self.request.body)
        
        childUuid = None
        h5path = None
        filename = None   # fake filename
        
        if "id" in body:
            childUuid = body["id"]
            if childUuid == None or len(childUuid) == 0:
                raise HTTPError(400)
        elif "h5path" in body:
            # todo
            h5path = body["h5path"]
            if h5path == None or len(h5path) == 0 or not h5path.startswith('/'):
                raise HTTPError(400)
                 
        elif "href" in body:
            href = body["href"]
            if href == None or len(href) == 0 or not href.startswith('http'):
                raise HTTPError(400)
            o = urlparse(href)
            if len(o.scheme) == 0 or len(o.netloc) == 0:
                raise HTTPError(400)
            if len(o.query) > 0:
                raise HTTPError(400)  # no query param
            filename = o.scheme + "://" + o.netloc
            if len(o.fragment) > 0:
                # url should be in the form: /#h5path(<path>)
                if (o.path != "/" or not o.fragment.startswith("h5path(/") or
                    not  o.fragment.endswith(")")):
                    raise HTTPError(400)
                h5path = o.fragment[len("h5path("):-1]
                h5path = h5path.strip()
            else:
                # url should be in the form:  /(datasets|datatypes|groups)/<id>
                if (o.path.startswith("/datasets/") or   o.path.startswith("/groups/") or 
                     o.path.startswith("/datatypes/")):
                    h5path = o.path
                else:
                    raise HTTPError(400)
                
            
        else: 
            log.info("bad put syntax: [" + self.request.body + "]")
            raise HTTPError(400)                      
        
        domain = self.request.host
        filePath = getFilePath(domain) 
        
        response = { }
        
        verifyFile(filePath)
        items = None
        rootUUID = None
        with Hdf5db(filePath, app_logger=log) as db:
            if childUuid:
                ok = db.linkObject(reqUuid, childUuid, linkName)
            elif filename:
                ok = db.createExternalLink(reqUuid, filename, h5path, linkName)
            elif h5path:
                ok = db.createSoftLink(reqUuid, h5path, linkName)
            else:
                raise HTTPError(500)
            if not ok:
                httpStatus = 500
                if db.httpStatus != 201:
                    httpStatus = db.httpStatus
                raise HTTPError(httpStatus)
            rootUUID = db.getUUIDByPath('/')
            
        self.set_status(201) 
        
    def delete(self): 
        log = logging.getLogger("h5serv")
        log.info('LinkHandler.delete ' + self.request.host)   
        reqUuid = self.getRequestId(self.request.uri)
        
        linkName = self.getName(self.request.uri)
        
        log.info( " delete link  name[: " + linkName + "] parentUuid: " + reqUuid)
           
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        with Hdf5db(filePath, app_logger=log) as db:
            ok = db.unlinkItem(reqUuid, linkName)
            if not ok:
                httpStatus = db.httpStatus
                if httpStatus == 200:
                    httpStatus = 500
                raise HTTPError(httpStatus)  
                
class TypeHandler(RequestHandler):
    
    # or 'Snn' for fixed string or 'vlen_bytes' for variable 
    def getRequestId(self):
        log = logging.getLogger("h5serv")
        # request is in the form /datatypes/<id>, return <id>
        uri = self.request.uri
        npos = uri.rfind('/')
        if npos < 0:
            raise HTTPError(500)  # should not get routed to TypeHandler in this case
        if npos == len(uri) - 1:
            raise HTTPError(400, message="missing id")
        id = uri[(npos+1):]
        log.info('got id: [' + id + ']')
    
        return id
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('TypeHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        response = { }
        hrefs = []
        rootUUID = None
        item = None
        with Hdf5db(filePath, app_logger=log) as db:
            item = db.getCommittedTypeItemByUuid(reqUuid)
            if item == None:
                httpError = 404  # not found
                if db.httpStatus != 200:
                    httpError = db.httpStatus # library may have more specific error code
                log.info("dataset: [" + reqUuid + "] not found")
                raise HTTPError(httpError)
            rootUUID = db.getUUIDByPath('/')
                         
        # got everything we need, put together the response
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',       'href': href + 'datatypes/' + reqUuid})
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'attributes', 'href': href + 'datatypes/' + reqUuid + '/attributes'}) 
        hrefs.append({'rel': 'home',       'href': href })        
        response['id'] = reqUuid
        typeItem = item['type']
        response['type'] = hdf5dtype.getTypeResponse(typeItem)
        response['created'] = unixTimeToUTC(item['ctime'])
        response['lastModified'] = unixTimeToUTC(item['mtime'])
        response['attributeCount'] = item['attributeCount']
        response['hrefs'] = hrefs
        
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        
    def post(self):
        log = logging.getLogger("h5serv")
        log.info('TypeHandler.post host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        if self.request.uri != '/datatypes/':
            log.info('bad datatypes post request')
            raise HTTPError(405)  # Method not allowed
               
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        
        body = json.loads(self.request.body)
            
        if "type" not in body:
            log.info("Type not supplied")
            raise HTTPError(400)  # missing type
            
        datatype = body["type"]     
        
        with Hdf5db(filePath, app_logger=log) as db:
            rootUUID = db.getUUIDByPath('/')
            typeUUID = db.createCommittedType(datatype)
            if typeUUID == None:
                httpError = 500
                if db.httpStatus != 200:
                    httpError = db.httpStatus # library may have more specific error code
                log.info("failed to create type (httpError: " + str(httpError) + ")")
                raise HTTPError(httpError)
         
        response = { }
      
        # got everything we need, put together the response
        hrefs = [ ]
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',       'href': href + 'datatypes/' + typeUUID})
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'attributes', 'href': href + 'datatypes/' + typeUUID + '/attributes'})   
        response['id'] = typeUUID
        response['attributeCount'] = 0
        response['hrefs'] = hrefs
        
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response)) 
        self.set_status(201)  # resource created
        
    def delete(self): 
        log = logging.getLogger("h5serv")
        log.info('TypeHandler.delete ' + self.request.host)   
        uuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        with Hdf5db(filePath, app_logger=log) as db:
            ok = db.deleteObjectByUuid(uuid)
            if not ok:
                httpStatus = db.httpStatus
                if httpStatus == 200:
                    httpStatus = 500
                raise HTTPError(httpStatus)  
                
class DatatypeHandler(RequestHandler):
    def getRequestId(self):
        log = logging.getLogger("h5serv")
        # request is in the form /datasets/<id>/type, return <id>
        uri = self.request.uri
        npos = uri.rfind('/type')
        if npos < 0:
            raise HTTPError(500)  # should not get routed to DatatypeHandler in this case
        id_part = uri[:npos]
        npos = id_part.rfind('/')
        if npos < 0:
            raise HTTPError(500)  # should not get routed to DatatypeHandler in this case
        
        if npos == len(id_part) - 1:
            raise HTTPError(400, message="missing id")
        id = id_part[(npos+1):]
        log.info('got id: [' + id + ']')
    
        return id
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('DatatypeHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        response = { }
        hrefs = []
        rootUUID = None
        item = None
        with Hdf5db(filePath, app_logger=log) as db:
            item = db.getDatasetTypeItemByUuid(reqUuid)
            if item == None:
                httpError = 404  # not found
                if db.httpStatus != 200:
                    httpError = db.httpStatus # library may have more specific error code
                log.info("dataset: [" + reqUuid + "] not found")
                raise HTTPError(httpError)
            rootUUID = db.getUUIDByPath('/')
                         
        # got everything we need, put together the response
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',  'href': href + 'datasets/' + reqUuid + '/type'})
        hrefs.append({'rel': 'owner', 'href': href + 'datasets/' + reqUuid })
        hrefs.append({'rel': 'root',  'href': href + 'groups/' + rootUUID})
        response['type'] = item['type']
       
        response['created'] = unixTimeToUTC(item['ctime'])
        response['lastModified'] = unixTimeToUTC(item['mtime'])
        response['hrefs'] = hrefs
        
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
                
class ShapeHandler(RequestHandler):
    def getRequestId(self):
        log = logging.getLogger("h5serv")
        # request is in the form /datasets/<id>/shape, return <id>
        uri = self.request.uri
        npos = uri.rfind('/shape')
        if npos < 0:
            raise HTTPError(500)  # should not get routed to ShapeHandler in this case
        id_part = uri[:npos]
        npos = id_part.rfind('/')
        if npos < 0:
            raise HTTPError(500)  # should not get routed to ShapeHandler in this case
        
        if npos == len(id_part) - 1:
            raise HTTPError(400, message="missing id")
        id = id_part[(npos+1):]
        log.info('got id: [' + id + ']')
    
        return id
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('ShapeHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        response = { }
        hrefs = []
        rootUUID = None
        item = None
        with Hdf5db(filePath, app_logger=log) as db:
            item = db.getDatasetItemByUuid(reqUuid)
            if item == None:
                httpError = 404  # not found
                if db.httpStatus != 200:
                    httpError = db.httpStatus # library may have more specific error code
                log.info("dataset: [" + reqUuid + "] not found")
                raise HTTPError(httpError)
            rootUUID = db.getUUIDByPath('/')
                         
        # got everything we need, put together the response
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',  'href': href + 'datasets/' + reqUuid})
        hrefs.append({'rel': 'owner', 'href': href + 'datasets/' + reqUuid })
        hrefs.append({'rel': 'root',  'href': href + 'groups/' + rootUUID})   
        shape = item['shape']
        if 'fillvalue' in item:
            shape['fillvalue'] = item['fillvalue']
        response['shape'] = shape
        response['created'] = unixTimeToUTC(item['ctime'])
        response['lastModified'] = unixTimeToUTC(item['mtime'])
        response['hrefs'] = hrefs
        
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        
    def put(self):
        log = logging.getLogger("h5serv")
        log.info('ShapeHandler.put host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        reqUuid = self.getRequestId()       
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        
        body = json.loads(self.request.body)
        
        if "shape" not in body:
            log.info("Shape not supplied")
            raise HTTPError(400)  # missing shape
            
        shape = body["shape"]
        if type(shape) == int:
            dim1 = shape
            shape = [dim1]
        elif type(shape) == list or type(shape) == tuple: 
            pass # can use as is
        else:
            log.info("invalid shape argument")
            raise HTTPError(400)
            
        # validate shape
        for extent in shape:
            if type(extent) != int:
                log.info("invalid shape type")
                raise HTTPError(400)
            if extent < 0:
                log.info("invalid shape (negative extent)")
                raise HTTPError(400) 
        
        with Hdf5db(filePath, app_logger=log) as db:
            rootUUID = db.getUUIDByPath('/')
            db.resizeDataset(reqUuid, shape)
            
            if db.httpStatus != 200:
                httpError = db.httpStatus # library may have more specific error code
                log.info("failed to resize dataset (httpError: " + str(httpError) + ")")
                raise HTTPError(httpError)
        log.info("resize OK")    
        self.set_status(201)  # resource created    
                
class DatasetHandler(RequestHandler):
   
    def getRequestId(self):
        log = logging.getLogger("h5serv")
        # request is in the form /datasets/<id>, return <id>
        uri = self.request.uri
        npos = uri.rfind('/')
        if npos < 0:
            raise HTTPError(500)  # should not get routed to TypeHandler in this case
        if npos == len(uri) - 1:
            raise HTTPError(400, message="missing id")
        id = uri[(npos+1):]
        log.info('got id: [' + id + ']')
    
        return id
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('DatasetHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        response = { }
        hrefs = []
        rootUUID = None
        item = None
        with Hdf5db(filePath, app_logger=log) as db:
            item = db.getDatasetItemByUuid(reqUuid)
            if item == None:
                httpError = 404  # not found
                if db.httpStatus != 200:
                    httpError = db.httpStatus # library may have more specific error code
                log.info("dataset: [" + reqUuid + "] not found")
                raise HTTPError(httpError)
            rootUUID = db.getUUIDByPath('/')
            
        # got everything we need, put together the response
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',       'href': href + 'datasets/' + reqUuid})
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'attributes', 'href': href + 'datasets/' + reqUuid + '/attributes'}) 
        hrefs.append({'rel': 'data', 'href': href + 'datasets/' + reqUuid + '/value'}) 
        hrefs.append({'rel': 'home', 'href': href })       
        response['id'] = reqUuid
        typeItem = item['type']
        response['type'] = hdf5dtype.getTypeResponse(typeItem)
        response['shape'] = item['shape']
        if 'fillvalue' in item:
            response['fillvalue'] = item['fillvalue']
        response['created'] = unixTimeToUTC(item['ctime'])
        response['lastModified'] = unixTimeToUTC(item['mtime'])
        response['attributeCount'] = item['attributeCount']
        response['hrefs'] = hrefs
        
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        
    def post(self):
        log = logging.getLogger("h5serv")
        log.info('DatasetHandler.post host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        if self.request.uri != '/datasets/':
            log.info('bad datasets post request')
            raise HTTPError(405)  # Method not allowed
               
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        shape = None
        
        body = json.loads(self.request.body)
        
        if "type" not in body:
            log.info("Type not supplied")
            raise HTTPError(400)  # missing type
            
        if "shape" in body:
            shape = body["shape"]
            if type(shape) == int:
                dim1 = shape
                shape = [dim1]
            elif type(shape) == list or type(shape) == tuple: 
                pass # can use as is
            else:
                log.info("invalid shape argument")
                raise HTTPError(400)
        else:
            shape = ()  # empty tuple
            
        datatype = body["type"]
        
        maxshape = None
        if "maxshape" in body:
            maxshape = body["maxshape"]
            if type(maxshape) == int:
                dim1 = maxshape
                maxshape = [dim1]
            elif type(maxshape) == list or type(maxshape) == tuple: 
                pass # can use as is
            else:
                log.info("invalid maxshape argument")
                raise HTTPError(400)     
           
        # validate shape
        for extent in shape:
            if type(extent) != int:
                log.info("invalid shape type")
                raise HTTPError(400)
            if extent < 0:
                log.info("invalid shape (negative extent)")
                raise HTTPError(400) 
            
        if maxshape:
            if len(maxshape) != len(shape):
                log.info("invalid maxshape length")
                raise HTTPError(400)
            for i in range(len(shape)):
                maxextent = maxshape[i]
                if maxextent != 0 and maxextent < shape[i]:
                    log.info("invalid maxshape extent")
                    raise HTTPError(400)
                if maxextent == 0:
                    maxshape[i] = None  # this indicates unlimited
        
        with Hdf5db(filePath, app_logger=log) as db:
            rootUUID = db.getUUIDByPath('/')
            dsetUUID = db.createDataset(datatype, shape, maxshape)
            if dsetUUID == None:
                httpError = 500
                if db.httpStatus != 200:
                    httpError = db.httpStatus # library may have more specific error code
                log.info("failed to create dataset (httpError: " + str(httpError) + ")")
                raise HTTPError(httpError)
                
        response = { }
      
        # got everything we need, put together the response
        hrefs = [ ]
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',       'href': href + 'datasets/' + dsetUUID})
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'attributes', 'href': href + 'datasets/' + dsetUUID + '/attributes'})   
        hrefs.append({'rel': 'value', 'href': href + 'datasets/' + dsetUUID + '/value'})        
        response['id'] = dsetUUID
        response['attributeCount'] = 0
        response['hrefs'] = hrefs
        
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))  
        self.set_status(201)  # resource created
        
    def delete(self): 
        log = logging.getLogger("h5serv")
        log.info('DatasetHandler.delete host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        uuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        with Hdf5db(filePath, app_logger=log) as db:
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
        log = logging.getLogger("h5serv")
        # Get optional query parameters for given dim
        dimQuery = 'dim' + str(dim + 1)
        try:
            start = int(self.get_query_argument(dimQuery + '_start', 0))
            stop =  int(self.get_query_argument(dimQuery + '_stop', extent))
            step =  int(self.get_query_argument(dimQuery + '_step', 1))
        except ValueError:
            log.info("invalid selection parameter (can't convert to int)")
            raise HTTPError(400)
        if start < 0 or start > extent:
            log.info("bad selection start parameter for dimension: " + dimQuery)
            raise HTTPError(400)
        if stop > extent:
            log.info("bad selection stop parameter for dimension: " + dimQuery)
            raise HTTPError(400)
        if step == 0:
            log.info("bad selection step parameter for dimension: " + dimQuery)
            raise HTTPError(400)
        s = slice(start, stop, step)
        log.info(dimQuery + " start: " + str(start) + " stop: " + str(stop) + " step: " + 
            str(step)) 
        return s
        
    """
    Get slices given lists of start, stop, step values
    """
    def getHyperslabSelection(self, dsetshape, start, stop, step):
        log = logging.getLogger("h5serv")
        rank = len(dsetshape)
        if start:
            if type(start) is not list:
                start = [start,]
            if len(start) != rank:
                log.info("request start array length not equal to dataset rank")
                raise HTTPError(400)
            for dim in range(rank):
                if start[dim] < 0 or start[dim] >= dsetshape[dim]:
                    log.info("request start index invalid for dim: " + str(dim))
                    raise HTTPError(400)
        else:
            start = []
            for dim in range(rank):
                start.append(0)
        
        if stop:
            if type(stop) is not list:
                stop = [stop,]
            if len(stop) != rank:
                log.info("request stop array length not equal to dataset rank")
                raise HTTPError(400)
            for dim in range(rank):
                if stop[dim] <= start[dim] or stop[dim] > dsetshape[dim]:
                    log.info("request stop index invalid for dim: " + str(dim))
                    raise HTTPError(400)
        else:
            stop = []
            for dim in range(rank):
                stop.append(dsetshape[dim])
        
        if step:
            if type(step) is not list:
                step = [step,]
            if len(step) != rank:
                log.info("request step array length not equal to dataset rank")
                raise HTTPError(400)
            for dim in range(rank):
                if step[dim] <= 0 or step[dim] > dsetshape[dim]:
                    log.info("request step index invalid for dim: " + str(dim))
                    raise HTTPError(400)
        else:
            step = []
            for dim in range(rank):
                step.append(1)
            
        slices = []
        for dim in range(rank):
            try:
                s = slice(int(start[dim]), int(stop[dim]), int(step[dim]))
            except ValueError:
                log.info("invalid start/stop/step value")
                raise HTTPError(400)
            slices.append(s)
        return tuple(slices)
        
    """
    Helper method - get uuid for the dataset
    """    
    def getRequestId(self):
        log = logging.getLogger("h5serv")
        # request is in the form /datasets/<id>/value?xxx, return <id>
        uri = self.request.uri
        if uri[:len('/datasets/')] != '/datasets/':
            # should not get here!
            log.error("unexpected uri: " + uri)
            raise HTTPError(500)
        uri = uri[len('/datasets/'):]  # get stuff after /datasets/
        npos = uri.find('/')
        if npos <= 0:
            log.info("bad uri")
            raise HTTPError(400)  
        id = uri[:npos]
         
        log.info('got id: [' + id + ']')
    
        return id
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('ValueHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        response = { }
        hrefs = []
        rootUUID = None
        item = None
        values = None
        with Hdf5db(filePath, app_logger=log) as db:
            item = db.getDatasetItemByUuid(reqUuid)
            if item == None:
                httpError = 404  # not found
                if db.httpStatus != 200:
                    httpError = db.httpStatus # library may have more specific error code
                log.info("dataset: [" + reqUuid + "] not found")
                raise HTTPError(httpError)
            itemType = item['type']
            if itemType['class'] == 'H5T_VLEN':
                #todo - support for returning VLEN data...
                log.info("GET VLEN data not supported")
                # raise HTTPError(501)  # Not implemented
            if itemType['class'] == 'H5T_OPAQUE':
                #todo - support for returning OPAQUE data...
                log.info("GET OPAQUE data not supported")
                raise HTTPError(501)  # Not implemented
            shape = item['shape']
            if shape['class'] == 'H5S_NULL':
                pass   # don't return a value
            elif shape['class'] == 'H5S_SCALAR':
                values = db.getDatasetValuesByUuid(reqUuid, Ellipsis)
            elif shape['class'] == 'H5S_SIMPLE':
                dims = shape['dims']
                rank = len(dims)
                slices = []
                for dim in range(rank):
                    slice = self.getSliceQueryParam(dim, dims[dim])
                    slices.append(slice)
         
                values = db.getDatasetValuesByUuid(reqUuid, tuple(slices)) 
            else:
                log.error("unexpected shape class: " + shape['class'])
                raise HTTPError(500)
                
            rootUUID = db.getUUIDByPath('/')
                         
        # got everything we need, put together the response
        href = self.request.protocol + '://' + domain + '/'
        
        if values is not None:
            response['value'] = values
        
        hrefs.append({'rel': 'self',  'href': href + 'datasets/' + reqUuid + '/value'})
        hrefs.append({'rel': 'root',  'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'owner', 'href': href + 'datasets/' + reqUuid }) 
        hrefs.append({'rel': 'home',  'href': href })   
        response['hrefs'] = hrefs
        
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response)) 
        
    def post(self):
        log = logging.getLogger("h5serv")
        log.info('ValueHandler.post host=[' + self.request.host + '] uri=[' +
             self.request.uri + ']')
        
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        body = json.loads(self.request.body)
        if "points" not in body:
            log.info("value post request without points in body")
            raise HTTPError(400)
        points = body['points']
        if type(points) != list:
            log.info("expecting list of points")
            raise HTTPError(400)
        
        
        response = { }
        hrefs = []
        rootUUID = None
        item = None
        values = None
        with Hdf5db(filePath, app_logger=log) as db:
            item = db.getDatasetItemByUuid(reqUuid)
            if item == None:
                httpError = 404  # not found
                if db.httpStatus != 200:
                    httpError = db.httpStatus # library may have more specific error code
                log.info("dataset: [" + reqUuid + "] not found")
                raise HTTPError(httpError)
            shape = item['shape']
            if shape['class'] == 'H5S_SCALAR':
                log.info("point selection is not supported on scalar datasets")
                raise HTTPError(400)
            rank = len(shape['dims'])
                
            for point in points:
                if rank == 1 and type(point) != int:
                    log.info("elements of points to be int type for datasets of rank 1")
                    raise HTTPError(400)
                elif rank > 1 and type(point) != list:
                    log.info("elements of points to be list type for datasets of rank >1")
                    raise HTTPError(400)
                    if len(point) != rank:
                        log.info("one or more points have missing coordinate value")
                        raise HTTPError(400)
             
            values = db.getDatasetPointSelectionByUuid(reqUuid, points) 
            rootUUID = db.getUUIDByPath('/')
                         
        # got everything we need, put together the response
        href = self.request.protocol + '://' + domain + '/'
        response['value'] = values
        
        hrefs.append({'rel': 'self',  'href': href + 'datasets/' + reqUuid + '/value'})
        hrefs.append({'rel': 'root',  'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'owner', 'href': href + 'datasets/' + reqUuid }) 
        hrefs.append({'rel': 'home',  'href': href })   
        #response['hrefs'] = hrefs
        
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))     
    
    def put(self):
        log = logging.getLogger("h5serv")
        log.info('ValueHandler.put host=[' + self.request.host + '] uri=[' + 
            self.request.uri + ']')
        
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        points = None
        start = None
        stop = None
        step = None
        
        body = json.loads(self.request.body)
        
        if "value" not in body:
            log.info("Value not supplied")
            raise HTTPError(400) # missing data
            
        if "points" in body:
            points = body['points']
            if type(points) != list:
                log.info("expecting list of points")
                raise HTTPError(400)
            if 'start' in body or 'stop' in body or 'step' in body:
                log.info("can use hyperslab selection with points")
                raise HTTPError(400)
            if len(points) > len(value):
                log.info("more points provided than values")
                raise HTTPError(400)
        else:
            # hyperslab selection
            if 'start' in body:
                start = body['start']
            if 'stop' in body:
                stop = body['stop']
            if 'step' in body:
                step = body['step']
                            
        data = body["value"]
        
        with Hdf5db(filePath, app_logger=log) as db:
            item = db.getDatasetItemByUuid(reqUuid)
            if item == None:
                httpError = 404  # not found
                if db.httpStatus != 200:
                    httpError = db.httpStatus # library may have more specific error code
                log.info("dataset: [" + reqUuid + "] not found")
                raise HTTPError(httpError)
            dsetshape = item['shape']
            dims = dsetshape['dims']
            rank = len(dims) 
            if points:
                for point in points:
                    pass
                    
            else:
                slices = self.getHyperslabSelection(dims, start, stop, step)
                # todo - check that the types are compatible
                ok = db.setDatasetValuesByUuid(reqUuid, data, slices)
                if not ok:
                    httpError = 500  # internal error
                    if db.httpStatus != 200:
                        httpError = db.httpStatus # library may have more specific error code
                    log.info("dataset put error")
                    raise HTTPError(httpError)   
            log.info("value post succeeded")   
           
class AttributeHandler(RequestHandler):

    # convert embedded list (list of lists) to tuples
    def convertToTuple(self, data):
        if type(data) == list or type(data) == tuple:
            sublist = []
            for e in data:
                sublist.append(self.convertToTuple(e))
            return tuple(sublist)
        else:
            return data
    
    def getRequestId(self):
        log = logging.getLogger("h5serv")
        # request is in the form /(datasets|groups|datatypes)/<id>/attributes(/<name>), 
        # return <id>
        uri = self.request.uri
        idpart = None
        if uri[:len('/datasets/')] == '/datasets/':
            idpart = uri[len('/datasets/'):]  # get stuff after /datasets/
        elif uri[:len('/groups/')] == '/groups/':
            idpart = uri[len('/groups/'):]  # get stuff after /groups/
        elif uri[:len('/datatypes/')] == '/datatypes/':
            idpart = uri[len('/datatypes/'):]  # get stuff after /datatypes/
        else:
            # should not get here!
            log.error("unexpected uri: " + uri)
            raise HTTPError(500)
        
        npos = idpart.find('/')
        if npos <= 0:
            log.info("bad uri")
            raise HTTPError(400)  
        id = idpart[:npos]
         
        log.info('got id: [' + id + ']')
    
        return id
        
    def getRequestName(self):
        log = logging.getLogger("h5serv")
        # request is in the form /(datasets|groups|datatypes)/<id>/attributes(/<name>), 
        # return <name>
        # return None if the uri doesn't end with ".../<name>"
        uri = self.request.uri
        name = None
        npos = uri.rfind('/attributes')
        if npos <= 0:
            log.info("bad uri")
            raise HTTPError(400)  
        uri = uri[npos+len('/attributes'):]
        if uri[0:1] == '/':
            uri = uri[1:]
            if len(uri) > 0:
                name = url_unescape(uri)  # todo: handle possible query string?
                log.info('got name: [' + name + ']') 
    
        return name
        
    def getRequestCollectionName(self):
        log = logging.getLogger("h5serv")
        # request is in the form /(datasets|groups|datatypes)/<id>/attributes(/<name>), 
        # return datasets | groups | datatypes
        uri = self.request.uri
        
        npos = uri.find('/')
        if npos < 0:
            log.info("bad uri")
            raise HTTPError(400)  
        uri = uri[(npos+1):]
        npos = uri.find('/')  # second '/'
        col_name = uri[:npos]
         
        log.info('got collection name: [' + col_name + ']')
        if col_name not in ('datasets', 'groups', 'datatypes'):
            raise HTTPError(500)   # shouldn't get routed here in this case
    
        return col_name
        
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('AttrbiuteHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        
        reqUuid = self.getRequestId()
        domain = self.request.host
        col_name = self.getRequestCollectionName()
        attr_name = self.getRequestName()
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        response = { }
        hrefs = []
        rootUUID = None
        items = []
        # Get optional query parameters
        limit = self.get_query_argument("Limit", 0)
        if type(limit) is not int:
            try:
                limit = int(limit)
            except ValueError:
                log.info("expected int type for limit")
                raise HTTPError(400) 
        marker = self.get_query_argument("Marker", None)
        with Hdf5db(filePath, app_logger=log) as db:
            if attr_name != None:
                item = db.getAttributeItem(col_name, reqUuid, attr_name)
                if item == None:
                    httpError = 404  # not found
                    if db.httpStatus != 200:
                        httpError = db.httpStatus # library may have more specific error code
                    log.info("attribute: [" + reqUuid + "]/" + attr_name + " not found")
                    raise HTTPError(httpError)
                items.append(item)
            else:
                # get all attributes (but without data)
                items = db.getAttributeItems(col_name, reqUuid, marker, limit)
            rootUUID = db.getUUIDByPath('/')
                         
        
        # got everything we need, put together the response
        href = self.request.protocol + '://' + domain + '/' 
        root_href = href + 'groups/' + rootUUID
        owner_href = href + col_name + '/' + reqUuid 
        self_href = owner_href + '/attributes'
        if attr_name != None:
            self_href += '/' + url_escape(attr_name)
    
        responseItems = []
        for item in items:
            responseItem = {}
            responseItem['name'] = item['name']
            typeItem = item['type']
            responseItem['type'] = hdf5dtype.getTypeResponse(typeItem)
            responseItem['shape'] = item['shape']
            responseItem['created'] = unixTimeToUTC(item['ctime']) 
            responseItem['lastModified'] = unixTimeToUTC(item['mtime']) 
            if typeItem['class'] == 'H5T_OPAQUE':
                pass # todo - send data for H5T_OPAQUE's
            elif 'value' in item:
                responseItem['value'] = item['value']
            
            responseItems.append(responseItem)
            
        hrefs.append({'rel': 'self',       'href': self_href})
        hrefs.append({'rel': 'owner',      'href': owner_href })
        hrefs.append({'rel': 'root',       'href': root_href }) 
        hrefs.append({'rel': 'home',       'href': href }) 
        
            
        if attr_name == None:
            # specific attribute response
            response['attributes'] = responseItems
        else:
            if len(responseItems) == 0:
                # should have raised exception earlier
                log.error("attribute not found: " + attr_name) 
                raise HTTPError(404)
            responseItem = responseItems[0]
            for k in responseItem:
                response[k] = responseItem[k]
        response['hrefs'] = hrefs   
         
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        
    def put(self):
        log = logging.getLogger("h5serv")
        log.info('AttributeHandler.put host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        
        domain = self.request.host
        col_name = self.getRequestCollectionName()
        reqUuid = self.getRequestId()
        attr_name = self.getRequestName()
        if attr_name == None:
            log.info("Attribute name not supplied")
            raise HTTPError(400)
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        body = json.loads(self.request.body)
        
        if "shape" not in body:
            log.info("Shape not supplied")
            raise HTTPError(400)  # missing shape
            
        if "type" not in body:
            log.info("Type not supplied")
            raise HTTPError(400)  # missing type
            
        if "value" not in body:
            log.info("Value not supplied")
            raise HTTPError(400)  # missing value
            
        shape = body["shape"]
        datatype = body["type"]
        value = body["value"]
        if type(shape) == int:
            dim1 = shape
            shape = []
            shape = [dim1]
        elif type(shape) == list or type(shape) == tuple: 
            pass # can use as is
        else:
            log.info("invalid shape argument")
            raise HTTPError(400)
            
        # validate shape
        for extent in shape:
            if type(extent) != int:
                log.info("invalid shape type")
                raise HTTPError(400)
            if extent < 0:
                log.info("invalid shape (negative extent)")
                raise HTTPError(400)   
                
        # convert list values to tuples (otherwise h5py is not happy)
        data = self.convertToTuple(value)
                   
        
        with Hdf5db(filePath, app_logger=log) as db:
            db.createAttribute(col_name, reqUuid, attr_name, shape, datatype, data)
            if db.httpStatus != 200:
                raise HTTPError(db.httpStatus)
            rootUUID = db.getUUIDByPath('/')
                
        response = { }
      
        # got everything we need, put together the response
        href = self.request.protocol + '://' + domain + '/' 
        root_href = href + 'groups/' + rootUUID
        owner_href = href + col_name + '/' + reqUuid 
        self_href = owner_href + '/attributes'
        if attr_name != None:
            self_href += '/' + attr_name
            
        hrefs = [ ]
        hrefs.append({'rel': 'self',   'href': self_href})
        hrefs.append({'rel': 'owner',  'href': owner_href })
        hrefs.append({'rel': 'root',   'href': root_href }) 
        response['hrefs'] = hrefs 
        
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))  
        self.set_status(201)  # resource created
        
    def delete(self): 
        log = logging.getLogger("h5serv")
        log.info('AttributeHandler.delete ' + self.request.host)   
        obj_uuid = self.getRequestId()
        domain = self.request.host
        col_name = self.getRequestCollectionName()
        attr_name = self.getRequestName()
        if attr_name == None:
            log.info("Attribute name not supplied")
            raise HTTPError(400)
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        with Hdf5db(filePath, app_logger=log) as db:
            ok = db.deleteAttribute(col_name, obj_uuid, attr_name)
            if not ok:
                httpStatus = db.httpStatus
                if httpStatus == 200:
                    httpStatus = 500
                raise HTTPError(httpStatus) 
                
         
class GroupHandler(RequestHandler):
    def getRequestId(self):
        log = logging.getLogger("h5serv")
        uri = self.request.uri
        npos = uri.rfind('/')
        if npos < 0:
            raise HTTPError(500)  # should not get routed to GroupHandler in this case
        if npos == len(uri) - 1:
            raise HTTPError(400, message="missing id")
        id = uri[(npos+1):]
        log.info('got id: [' + id + ']')
    
        return id
            
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('GroupHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        response = { }
             
        hrefs = []
        rootUUID = None
        item = None
        with Hdf5db(filePath, app_logger=log) as db:
            item = db.getGroupItemByUuid(reqUuid)
            if item == None:
                httpError = 404  # not found
                if db.httpStatus != 200:
                    httpError = db.httpStatus # library may have more specific error code
                log.info("group: [" + reqUuid + "] not found")
                raise HTTPError(httpError)
            rootUUID = db.getUUIDByPath('/')
                         
        # got everything we need, put together the response
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',       'href': href + 'groups/' + reqUuid})
        hrefs.append({'rel': 'links',      'href': href + 'groups/' + reqUuid + '/links'})
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'home',       'href': href }) 
        hrefs.append({'rel': 'attributes', 'href': href + 'groups/' + reqUuid + '/attributes'})        
        response['id'] = reqUuid
        response['created'] = unixTimeToUTC(item['ctime'])
        response['lastModified'] = unixTimeToUTC(item['mtime'])
        response['attributeCount'] = item['attributeCount']
        response['linkCount'] = item['linkCount']
        response['hrefs'] = hrefs
        
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        
    def delete(self): 
        log = logging.getLogger("h5serv")
        log.info('GroupHandler.delete ' + self.request.host)   
        uuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        with Hdf5db(filePath, app_logger=log) as db:
            ok = db.deleteObjectByUuid(uuid)
            if not ok:
                httpStatus = db.httpStatus
                if httpStatus == 200:
                    httpStatus = 500
                raise HTTPError(httpStatus) 
            rootUUID = db.getUUIDByPath('/') 
         
        response = {}        
        hrefs = []
                        
        # write the response
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',       'href': href + 'groups' })
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'home',       'href': href }) 
        response['hrefs'] = hrefs
         
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response)) 
                
class GroupCollectionHandler(RequestHandler):
            
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('GroupCollectionHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        rootUUID = None
        
        # Get optional query parameters
        limit = self.get_query_argument("Limit", 0)
        if type(limit) is not int:
            try:
                limit = int(limit)
            except ValueError:
                log.info("expected int type for limit")
                raise HTTPError(400) 
        marker = self.get_query_argument("Marker", None)
        
        response = { }
             
        items = None
        hrefs = []
        with Hdf5db(filePath, app_logger=log) as db:
            items = db.getCollection("groups", marker, limit)
            rootUUID = db.getUUIDByPath('/')
                         
        # write the response
        response['groups'] = items
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',       'href': href + 'groups' })
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'home',       'href': href }) 
        response['hrefs'] = hrefs
         
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        
    def post(self):
        log = logging.getLogger("h5serv")
        log.info('GroupHandlerCollection.post host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        if self.request.uri != '/groups':
            log.info('bad group post request')
            raise HTTPError(405)  # Method not allowed
               
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        
        with Hdf5db(filePath, app_logger=log) as db:
            rootUUID = db.getUUIDByPath('/')
            grpUUID = db.createGroup()
            if grpUUID == None:
                raise HTTPError(db.httpStatus)
            item = db.getGroupItemByUuid(grpUUID)
            if item == None:
                # unexpected!
                raise HTTPError(500)          
           
        href = self.request.protocol + '://' + domain  
        self.set_header('Location', href + '/groups/' + grpUUID)
        self.set_header('Content-Location', href + '/groups/' + grpUUID)
        
        # got everything we need, put together the response
        href = self.request.protocol + '://' + domain + '/'
        response = { } 
        hrefs = []
        hrefs.append({'rel': 'self',       'href': href + 'groups/' + grpUUID})
        hrefs.append({'rel': 'links',      'href': href + 'groups/' + grpUUID + '/links'})
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'home',       'href': href }) 
        hrefs.append({'rel': 'attributes', 'href': href + 'groups/' + grpUUID + '/attributes'})        
        response['id'] = grpUUID
        response['created'] = unixTimeToUTC(item['ctime'])
        response['lastModified'] = unixTimeToUTC(item['mtime'])
        response['attributeCount'] = item['attributeCount']
        response['linkCount'] = item['linkCount']
        response['hrefs'] = hrefs
        
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))               
        self.set_status(201)  # resource created
        
class DatasetCollectionHandler(RequestHandler):
            
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('DatasetCollectionHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        # Get optional query parameters
        limit = self.get_query_argument("Limit", 0)
        if type(limit) is not int:
            try:
                limit = int(limit)
            except ValueError:
                log.info("expected int type for limit")
                raise HTTPError(400) 
        marker = self.get_query_argument("Marker", None)
        
        response = { }
        hrefs = []
        rootUUID = None
             
        items = None
        with Hdf5db(filePath, app_logger=log) as db:
            items = db.getCollection("datasets", marker, limit)
            rootUUID = db.getUUIDByPath('/')
                         
        # write the response
        response['datasets'] = items
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',       'href': href + 'datasets' })
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'home',       'href': href }) 
        response['hrefs'] = hrefs
         
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        
class TypeCollectionHandler(RequestHandler):
            
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('TypeCollectionHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        # Get optional query parameters
        limit = self.get_query_argument("Limit", 0)
        if type(limit) is not int:
            try:
                limit = int(limit)
            except ValueError:
                log.info("expected int type for limit")
                raise HTTPError(400) 
        marker = self.get_query_argument("Marker", None)
        
        response = { }
        hrefs = []
        rootUUID = None
             
        items = None
        with Hdf5db(filePath) as db:
            items = db.getCollection("datatypes", marker, limit)
            rootUUID = db.getUUIDByPath('/')
                         
        # write the response
        response['datatypes'] = items
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',       'href': href + 'datatypes' })
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'home',       'href': href }) 
        response['hrefs'] = hrefs
         
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
          
        
class RootHandler(RequestHandler):

    def getRootResponse(self, filePath):
        log = logging.getLogger("h5serv")
        # used by GET / and PUT /
        domain = self.request.host
        filePath = getFilePath(domain)
        with Hdf5db(filePath, app_logger=log) as db:
            rootUUID = db.getUUIDByPath('/')
            datasetCount = db.getNumberOfDatasets()
            groupCount = db.getNumberOfGroups()
            datatypeCount = db.getNumberOfDatatypes()
         
        # generate response 
        hrefs = [ ]
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self', 'href': href})
        hrefs.append({'rel': 'database', 'href': href + 'datasets'})
        hrefs.append({'rel': 'groupbase', 'href': href + 'groups'})
        hrefs.append({'rel': 'typebase', 'href': href + 'datatypes' })
        hrefs.append({'rel': 'root',     'href': href + 'groups/' + rootUUID})
            
        response = {  }
        response['created'] = unixTimeToUTC(op.getctime(filePath))
        response['lastModified'] = unixTimeToUTC(op.getmtime(filePath))
        response['root'] = rootUUID
        response['hrefs'] = hrefs
        
      
        return response
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('RootHandler.get ' + self.request.host)
        # get file path for the domain
        # will raise exception if not found
        filePath = getFilePath(self.request.host)
        verifyFile(filePath)
        # print 'content-type:', self.request.headers['accept']
        accept_type = ''
        if 'accept' in self.request.headers:
            accept= self.request.headers['accept']
            # just extract the first type and not worry about q values for now...
            accept_values = accept.split(',')
            accept_types = accept_values[0].split(';')
            accept_type = accept_types[0]
            # print 'accept_type:', accept_type
        if False and accept_type == 'text/html':  # disable for now
            self.set_header('Content-Type', 'text/html') 
            self.write("<html><body>Hello world!</body></html>")
        else:
            response = self.getRootResponse(filePath)
            self.set_header('Content-Type', 'application/json') 
            self.write(json_encode(response)) 
        
    def put(self): 
        log = logging.getLogger("h5serv")
        log.info('RootHandler.put ' + self.request.host)  
        filePath = getFilePath(self.request.host)
        log.info("put filePath: " + filePath)
        if op.isfile(filePath):
            log.info("path exists")
            raise HTTPError(409)  # Conflict - is this the correct code?
        # create directories as needed
        makeDirs(op.dirname(filePath))
        log.info("creating file: [" + filePath + "]")
        if not Hdf5db.createHDF5File(filePath):
            log.error("unexpected error creating HDF5: " + filePath)
            raise HTTPError(500)
        response = self.getRootResponse(filePath)
        
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        self.set_status(201)  # resource created
          
    def delete(self): 
        log = logging.getLogger("h5serv")
        log.info('RootHandler.delete ' + self.request.host)   
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
    log = logging.getLogger("h5serv")
    log.warning('Caught signal: %s', sig)
    IOLoop.instance().add_callback(shutdown)
 
def shutdown():
    log = logging.getLogger("h5serv")
    MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 2
    log.info('Stopping http server')
    server.stop()
 
    log.info('Will shutdown in %s seconds ...', MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
    io_loop = tornado.ioloop.IOLoop.instance()
 
    deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN
 
    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
            log.info('Shutdown')
    stop_loop() 
    
    log.info("closing db")

def make_app():
    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "../static"),
        # "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        # "login_url": "/login",
        # "xsrf_cookies": True,
        "debug": config.get('debug')
    }
    print 'static_path:', settings['static_path']
    print 'isdebug:', settings['debug']
    
    app = Application( [
        url(r"/datasets/.*/type", DatatypeHandler),
        url(r"/datasets/.*/shape", ShapeHandler),
        url(r"/datasets/.*/attributes/.*", AttributeHandler),
        url(r"/groups/.*/attributes/.*", AttributeHandler),
        url(r"/datatypes/.*/attributes/.*", AttributeHandler),
        url(r"/datasets/.*/attributes", AttributeHandler),
        url(r"/groups/.*/attributes", AttributeHandler),
        url(r"/datatypes/.*/attributes", AttributeHandler),
        url(r"/datatypes/.*", TypeHandler),
        url(r"/datatypes/", TypeHandler),
        url(r"/datatypes\?.*", TypeCollectionHandler),
        url(r"/datatypes", TypeCollectionHandler),
        url(r"/datasets/.*/value", ValueHandler),
        url(r"/datasets/.*/value\?.*", ValueHandler),
        url(r"/datasets/.*", DatasetHandler),
        url(r"/datasets/", DatasetHandler),
        url(r"/datasets\?.*", DatasetCollectionHandler),
        url(r"/datasets", DatasetCollectionHandler),
        url(r"/groups/.*/links/.*", LinkHandler),
        url(r"/groups/.*/links\?.*", LinkCollectionHandler),
        url(r"/groups/.*/links", LinkCollectionHandler),
        url(r"/groups/", GroupHandler), 
        url(r"/groups/.*", GroupHandler), 
        url(r"/groups\?.*", GroupCollectionHandler),
        url(r"/groups", GroupCollectionHandler),
        url(r"/static/(.*)", tornado.web.StaticFileHandler, {'path', '../static/'}),
        url(r"/", RootHandler),
        url(r".*", DefaultHandler)
    ],  **settings)
    return app

def main():
    # os.chdir(config.get('datapath'))
    
    # create logger
    log = logging.getLogger("h5serv")
    log.setLevel(logging.INFO)
    # set daily rotating log
    handler = logging.handlers.TimedRotatingFileHandler('../log/h5serv.log',
                                       when="midnight",
                                       interval=1,
                                       backupCount=0,
                                       utc=True)
    
    # create formatter
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(filename)s:%(lineno)d::%(message)s")
    # add formatter to handler
    handler.setFormatter(formatter)
    # add handler to logger
    log.addHandler(handler)
    port = int(config.get('port'))
    global server
    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(port)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    log.info("INITIALIZING...")
    print "Starting event loop on port: ", port
    IOLoop.current().start()

main()
