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
from httpErrorUtil import errNoToHttpStatus

    
class DefaultHandler(RequestHandler):
    def put(self):
        log = logging.getLogger("h5serv")
        log.warning("got default PUT request")
        log.info('remote_ip: ' + self.request.remote_ip)
        log.warning(self.request)
        raise HTTPError(400, reason="No route matches") 
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.warning("got default GET request")
        log.info('remote_ip: ' + self.request.remote_ip)
        log.warning(self.request)
        raise HTTPError(400, reason="No route matches") 
        
    def post(self):
        log = logging.getLogger("h5serv") 
        log.warning("got default POST request")
        log.info('remote_ip: ' + self.request.remote_ip)
        log.warning(self.request)
        raise HTTPError(400, reason="No route matches") 
        
    def delete(self):
        log = logging.getLogger("h5serv")
        log.warning("got default DELETE request")
        log.info('remote_ip: ' + self.request.remote_ip)
        log.warning(self.request)
        raise HTTPError(400, reason="No route matches") 
        
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
            msg = "Bad Request: uri is invalid"
            log.info(msg)
            raise HTTPError(400, reason=msg)  
        id = uri[:npos]
         
        log.info('got id: [' + id + ']')
    
        return id
        
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('LinkCollectionHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']') 
        log.info('remote_ip: ' + self.request.remote_ip)      
        
        reqUuid = self.getRequestId(self.request.uri)
        domain = self.request.host
        filePath = getFilePath(domain) 
        
        # Get optional query parameters
        limit = self.get_query_argument("Limit", 0)
        if type(limit) is not int:
            try:
                limit = int(limit)
            except ValueError:
                msg = "Bad Request: Expected into type for limit"
                log.info(msg)
                raise HTTPError(400, reason=msg) 
        marker = self.get_query_argument("Marker", None)
                
        response = { }
        
        verifyFile(filePath)
        items = None
        rootUUID = None
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                items = db.getLinkItems(reqUuid, marker=marker, limit=limit)
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
                             
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
            msg = "Internal Server Error: Unexpected uri"
            log.error(msg)
            raise HTTPError(500, reason=msg)
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
            msg = "Internal Server Error: Unexpected uri"
            log.error(msg)
            raise HTTPError(500, reason=msg)
        if npos+len('/links/') >= len(uri):
            # no name specified
            msg = "Bad Request: no name specified"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        linkName = uri[npos+len('/links/'):]
        if linkName.find('/') >= 0:
            # can't have '/' in link name
            msg = "Bad Request: invalid linkname, '/' not allowed"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        return linkName
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('LinkHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')  
        log.info('remote_ip: ' + self.request.remote_ip)     
        
        reqUuid = self.getRequestId(self.request.uri)
        domain = self.request.host
        filePath = getFilePath(domain) 
        linkName = self.getName(self.request.uri)
        
        response = { }
        
        verifyFile(filePath)
        items = None
        rootUUID = None
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                item = db.getLinkItemByUuid(reqUuid, linkName)
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)
                         
        # got everything we need, put together the response
        targethref = ''
        if 'href' in item:
            targethref = item['href']
            
        response['lastModified'] = unixTimeToUTC(item['mtime'])
        response['created'] = unixTimeToUTC(item['ctime'])
        for key in ('mtime', 'ctime', 'href'):
            if key in item:
                del item[key]
                
        # replace 'file' key by 'h5domain' if present
        if 'file' in item:
            h5domain = item['file']
            del item['file']
            item['h5domain'] = h5domain
             
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
                link_href = self.request.protocol + '://' +  getDomain(item['h5domain'])
                hrefs.append({'rel': 'target', 'href': link_href + targethref})
        response['hrefs'] = hrefs      
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
    
    def put(self):
        log = logging.getLogger("h5serv")
        log.info('LinkHandler.put host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        # put - create a new link
        # patterns are:
        # PUT /group/<id>/links/<name> {id: <id> } 
        # PUT /group/<id>/links/<name> {h5path: <path> } 
        # PUT /group/<id>/links/<name> {h5path: <path>, h5domain: <href> }
        uri = self.request.uri
        reqUuid = self.getRequestId(self.request.uri)
        
        linkName = url_unescape(self.getName(self.request.uri))
        
        body = None
        try:
            body = json.loads(self.request.body)
        except ValueError as e:
            msg = "JSON Parser Error: " + e.message
            log.info(msg)
            raise HTTPError(400, reason=msg )
        
        childUuid = None
        h5path = None
        h5domain = None
        filename = None   # fake filename
        
        if "id" in body:
            childUuid = body["id"]
            if childUuid == None or len(childUuid) == 0:
                msg = "Bad Request: id not specified"
                log.info(msg)
                raise HTTPError(400, reason=msg)
        elif "h5path" in body:
            # todo
            h5path = body["h5path"]
            if h5path == None or len(h5path) == 0 or not h5path.startswith('/'):
                raise HTTPError(400)
             
            # if h5domain is present, this will be an external link     
            if "h5domain" in body:
                h5domain = body["h5domain"]
                    
        else: 
            msg = "Bad request: put syntax: [" + self.request.body + "]"
            log.info(msg)
            raise HTTPError(400, reasoln=msg)                      
        
        domain = self.request.host
        filePath = getFilePath(domain) 
        
        response = { }
        
        verifyFile(filePath)
        items = None
        rootUUID = None
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                if childUuid:
                    db.linkObject(reqUuid, childUuid, linkName)
                elif filename:
                    db.createExternalLink(reqUuid, h5domain, h5path, linkName)
                elif h5path:
                    db.createSoftLink(reqUuid, h5path, linkName)
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)   
            
        hrefs = []     
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',       'href': href + 'groups/' + reqUuid + 
            '/links/' + url_escape(linkName)})
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'home',       'href': href }) 
        hrefs.append({'rel': 'owner', 'href': href + 'groups/' + reqUuid})  
        response['hrefs'] = hrefs
        
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        self.set_status(201) 
        
    def delete(self): 
        log = logging.getLogger("h5serv")
        log.info('LinkHandler.delete ' + self.request.host)   
        log.info('remote_ip: ' + self.request.remote_ip)
        reqUuid = self.getRequestId(self.request.uri)
        
        linkName = self.getName(self.request.uri)
        
        log.info( " delete link  name[: " + linkName + "] parentUuid: " + reqUuid)
           
        domain = self.request.host
        response = { }
        rootUUID = None
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                db.unlinkItem(reqUuid, linkName)
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
            
        hrefs = []     
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'home',       'href': href }) 
        hrefs.append({'rel': 'owner', 'href': href + 'groups/' + reqUuid})  
        
        response['hrefs'] = hrefs      
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
                
class TypeHandler(RequestHandler):
    
    # or 'Snn' for fixed string or 'vlen_bytes' for variable 
    def getRequestId(self):
        log = logging.getLogger("h5serv")
        # request is in the form /datatypes/<id>, return <id>
        uri = self.request.uri
        npos = uri.rfind('/')
        if npos < 0:
            msg = "Internal Server Error: Unexpected routing"
            log.error(msg)
            raise HTTPError(500, reason=msg)  # should not get routed to TypeHandler in this case
        if npos == len(uri) - 1:
            msg = "Bad Request: id is not specified"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        id = uri[(npos+1):]
        log.info('got id: [' + id + ']')
    
        return id
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('TypeHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        response = { }
        hrefs = []
        rootUUID = None
        item = None
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                item = db.getCommittedTypeItemByUuid(reqUuid)
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
                         
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
        
    
        
    def delete(self): 
        log = logging.getLogger("h5serv")
        log.info('TypeHandler.delete ' + self.request.host)   
        log.info('remote_ip: ' + self.request.remote_ip)
        uuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                db.deleteObjectByUuid('datatype', uuid)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
                
class DatatypeHandler(RequestHandler):
    def getRequestId(self):
        log = logging.getLogger("h5serv")
        # request is in the form /datasets/<id>/type, return <id>
        uri = self.request.uri
        npos = uri.rfind('/type')
        if npos < 0:
            msg = "Internal Server Error: Unexpected routing"
            log.error(msg)
            raise HTTPError(500, reason=msg)  # should not get routed to DatatypeHandler in this case
        id_part = uri[:npos]
        npos = id_part.rfind('/')
        if npos < 0:
            msg = "Internal Server Error: Unexpected routing"
            log.error(msg)
            raise HTTPError(500, reason=msg)  # should not get routed to DatatypeHandler in this case
        
        if npos == len(id_part) - 1:
            msg = "Bad Request: id is not specified"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        id = id_part[(npos+1):]
        log.info('got id: [' + id + ']')
    
        return id
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('DatatypeHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        response = { }
        hrefs = []
        rootUUID = None
        item = None
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                item = db.getDatasetTypeItemByUuid(reqUuid)
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
                         
        # got everything we need, put together the response
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',  'href': href + 'datasets/' + reqUuid + '/type'})
        hrefs.append({'rel': 'owner', 'href': href + 'datasets/' + reqUuid })
        hrefs.append({'rel': 'root',  'href': href + 'groups/' + rootUUID})
        response['type'] = item['type']
       
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
            msg = "Internal Server Error: Unexpected routing"
            log.error(msg)
            raise HTTPError(500, reason=msg)  # should not get routed to ShapeHandler in this case
        id_part = uri[:npos]
        npos = id_part.rfind('/')
        if npos < 0:
            msg = "Internal Server Error: Unexpected routing"
            log.error(msg)
            raise HTTPError(500, reason=msg)  # should not get routed to ShapeHandler in this case
        
        if npos == len(id_part) - 1:
            msg = "Bad Request: id is not specified"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        id = id_part[(npos+1):]
        log.info('got id: [' + id + ']')
    
        return id
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('ShapeHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        response = { }
        hrefs = []
        rootUUID = None
        item = None
        
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                item = db.getDatasetItemByUuid(reqUuid)
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
                         
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
        log.info('remote_ip: ' + self.request.remote_ip)
        reqUuid = self.getRequestId()       
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        
        response = { }
        hrefs = []
        rootUUID = None
        body = None
        try:
            body = json.loads(self.request.body)
        except ValueError as e:
            msg = "JSON Parser Error: " + e.message
            log.info(msg)
            raise HTTPError(400, reason=msg )
        
        if "shape" not in body:
            msg = "Bad Request: Shape not specified"
            log.info(msg)
            raise HTTPError(400, reason=msg)  # missing shape
            
        shape = body["shape"]
        if type(shape) == int:
            dim1 = shape
            shape = [dim1]
        elif type(shape) == list or type(shape) == tuple: 
            pass # can use as is
        else:
            msg = "Bad Request: invalid shape argument"
            log.info(msg)
            raise HTTPError(400, reason=msg)
            
        # validate shape
        for extent in shape:
            if type(extent) != int:
                msg = "Bad Request: invalid shape type (expecting int)"
                log.info(msg)
                raise HTTPError(400, reason=msg)
            if extent < 0:
                msg = "Bad Request: invalid shape (negative extent)"
                log.info(msg)
                raise HTTPError(400, reason=msg) 
        
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                db.resizeDataset(reqUuid, shape)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
                
        log.info("resize OK")   
        # put together the response
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',  'href': href + 'datasets/' + reqUuid})
        hrefs.append({'rel': 'owner', 'href': href + 'datasets/' + reqUuid })
        hrefs.append({'rel': 'root',  'href': href + 'groups/' + rootUUID})    
        response['hrefs'] = hrefs
        
        self.set_status(201)  # resource created    
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response)) 
                
class DatasetHandler(RequestHandler):
   
    def getRequestId(self):
        log = logging.getLogger("h5serv")
        # request is in the form /datasets/<id>, return <id>
        uri = self.request.uri
        npos = uri.rfind('/')
        if npos < 0:
            msg = "Internal Server Error: unexpected routing"
            log.error(msg)
            raise HTTPError(500, reason=msg)  # should not get routed to TypeHandler in this case
        if npos == len(uri) - 1:
            msg = "Bad Request: id not specified"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        id = uri[(npos+1):]
        log.info('got id: [' + id + ']')
    
        return id
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('DatasetHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        response = { }
        hrefs = []
        rootUUID = None
        item = None
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                item = db.getDatasetItemByUuid(reqUuid)
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
            
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
        
        
    def delete(self): 
        log = logging.getLogger("h5serv")
        log.info('DatasetHandler.delete host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        uuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        
        response = {}        
        hrefs = []
        rootUUID = None
        
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                db.deleteObjectByUuid('dataset', uuid)
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)     
                        
        # write the response
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',       'href': href + 'datasets' })
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'home',       'href': href }) 
        response['hrefs'] = hrefs
         
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response)) 
            
                
class ValueHandler(RequestHandler):
     
    
    """
    Helper method - return slice for dim based on query params
    
    Query arg should be in the form: [<dim1>, <dim2>, ... , <dimn>]
     brackets are optional for one dimensional arrays.
     Each dimension, valid formats are:
        single integer: n
        start and end: n:m
        start, end, and stride: n:m:s
    """

    def getSliceQueryParam(self, dim, extent):
        log = logging.getLogger("h5serv")
        # Get optional query parameters for given dim
        log.info("getSliceQueryParam: " + str(dim) + ", " + str(extent))
        query = self.get_query_argument("select", default='ALL') 
        if query == 'ALL':
            # just return a slice for the entire dimension
            log.info("getSliceQueryParam: return default")
            return slice(0, extent)
            
        log.info("select query value: [" + query + "]");
            
        if not query.startswith('['):
            msg = "Bad Request: selection query missing start bracket"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        if not query.endswith(']'):
            msg = "Bad Request: selection query missing end bracket"
            log.info(msg)
            raise HTTPError(400, reason=msg)
            
        # now strip out brackets
        query = query[1:-1]
        
        query_array = query.split(',')
        if dim > len(query_array):
            msg = "Not enough dimensions supplied to query argument"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        dim_query = query_array[dim].strip()
        start = 0
        stop = extent
        step = 1
        if dim_query.find(':') < 0:
            # just a number - return start = stop for this value
            try:
                start = int(dim_query)
            except ValueError:
                msg ="Bad Request: invalid selection parameter (can't convert to int) for dimension: " + str(dim)
                log.info(msg)
                raise HTTPError(400, reason=msg)
            stop = start
        elif dim_query == ':':
            # select everything
            pass
        else:
            fields = dim_query.split(":")
            if len(fields) > 3:
                msg ="Bad Request: Too many ':' seperators for dimension: " + str(dim)
                log.info(msg)
                raise HTTPError(400, reason=msg)       
            try:
                if fields[0]:
                    start = int(fields[0])
                if fields[1]:
                    stop = int(fields[1])
                if len(fields) > 2 and fields[2]:
                    step = int(fields[2])
            except ValueError:
                msg ="Bad Request: invalid selection parameter (can't convert to int) for dimension: " + str(dim)
                log.info(msg)
                raise HTTPError(400, reason=msg)
        
        if start < 0 or start > extent:
            msg = "Bad Request: Invalid selection start parameter for dimension: " + str(dim)
            log.info(msg)
            raise HTTPError(400, reason=msg)
        if stop > extent:
            msg = "Bad Request: Invalid selection stop parameter for dimension: " + str(dim)
            log.info(msg)
            raise HTTPError(400, reason=msg)
        if step <= 0:
            msg = "Bad Request: invalid selection step parameter for dimension: " + str(dim)
            log.info(msg)
            raise HTTPError(400, reason=msg)
        s = slice(start, stop, step)
        log.info("dim query[" + str(dim) + "] returning: start: " + str(start) + " stop: " +
             str(stop) + " step: " +  str(step)) 
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
                msg = "Bad Request: start array length not equal to dataset rank"
                log.info(msg)
                raise HTTPError(400, reason=msg)
            for dim in range(rank):
                if start[dim] < 0 or start[dim] >= dsetshape[dim]:
                    msg = "Bad Request: start index invalid for dim: " + str(dim)
                    log.info(msg)
                    raise HTTPError(400, reason=msg)
        else:
            start = []
            for dim in range(rank):
                start.append(0)
        
        if stop:
            if type(stop) is not list:
                stop = [stop,]
            if len(stop) != rank:
                msg = "Bad Request: stop array length not equal to dataset rank"
                log.info(msg)
                raise HTTPError(400, reason=msg)
            for dim in range(rank):
                if stop[dim] <= start[dim] or stop[dim] > dsetshape[dim]:
                    msg = "Bad Request: stop index invalid for dim: " + str(dim)
                    log.info(msg)
                    raise HTTPError(400, reason=msg)
        else:
            stop = []
            for dim in range(rank):
                stop.append(dsetshape[dim])
        
        if step:
            if type(step) is not list:
                step = [step,]
            if len(step) != rank:
                msg = "Bad Request: step array length not equal to dataset rank"
                log.info(msg)
                raise HTTPError(400, reason=msg)
            for dim in range(rank):
                if step[dim] <= 0 or step[dim] > dsetshape[dim]:
                    msg = "Bad Request: step index invalid for dim: " + str(dim)
                    log.info(msg)
                    raise HTTPError(400, reason=msg)
        else:
            step = []
            for dim in range(rank):
                step.append(1)
            
        slices = []
        for dim in range(rank):
            try:
                s = slice(int(start[dim]), int(stop[dim]), int(step[dim]))
            except ValueError:
                msg = "Bad Request: invalid start/stop/step value"
                log.info(msg)
                raise HTTPError(400, reason=msg)
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
            msg = "Bad Request: uri is invalid"
            log.info(msg)
            raise HTTPError(400, reason=msg)  
        id = uri[:npos]
         
        log.info('got id: [' + id + ']')
    
        return id
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('ValueHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        response = { }
        hrefs = []
        rootUUID = None
        item = None
        values = None
        
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                item = db.getDatasetItemByUuid(reqUuid)
                itemType = item['type']
                
                if itemType['class'] == 'H5T_OPAQUE':
                    #todo - support for returning OPAQUE data...
                    msg = "Not Implemented: GET OPAQUE data not supported"
                    log.info(msg)
                    raise HTTPError(501, reason=msg)  # Not implemented
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
                    msg = "Internal Server Error: unexpected shape class: " + shape['class']
                    log.error(msg)
                    raise HTTPError(500, reason=msg)
                
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
                         
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
        log.info('remote_ip: ' + self.request.remote_ip)
        
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        body = None
        try:
            body = json.loads(self.request.body)
        except ValueError as e:
            msg = "JSON Parser Error: " + e.message
            log.info(msg)
            raise HTTPError(400, reason=msg )
        
        if "points" not in body:
            msg = "Bad Request: value post request without points in body"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        points = body['points']
        if type(points) != list:
            msg = "Bad Request: expecting list of points"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        
        
        response = { }
        hrefs = []
        rootUUID = None
        item = None
        values = None
        
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                item = db.getDatasetItemByUuid(reqUuid)
                shape = item['shape']
                if shape['class'] == 'H5S_SCALAR':
                    msg = "Bad Request: point selection is not supported on scalar datasets"
                    log.info(msg)
                    raise HTTPError(400, reason=msg)
                rank = len(shape['dims'])
                
                for point in points:
                    if rank == 1 and type(point) != int:
                        msg = "Bad Request: elements of points should be int type for datasets of rank 1"
                        log.info(msg)
                        raise HTTPError(400, reason=msg)
                    elif rank > 1 and type(point) != list:
                        msg = "Bad Request: elements of points should be list type for datasets of rank >1"
                        log.info(msg)
                        raise HTTPError(400, reason=msg)
                        if len(point) != rank:
                            msg = "Bad Request: one or more points have a missing coordinate value"
                            log.info(msg)
                            raise HTTPError(400, reason=msg)
             
                values = db.getDatasetPointSelectionByUuid(reqUuid, points) 
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
                         
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
        log.info('remote_ip: ' + self.request.remote_ip)
        
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        points = None
        start = None
        stop = None
        step = None
        
        body = None
        try:
            body = json.loads(self.request.body)
        except ValueError as e:
            msg = "JSON Parser Error: " + e.message
            log.info(msg)
            raise HTTPError(400, reason=msg )
        
        if "value" not in body:
            msg = "Bad Request: Value not specified"
            log.info(msg)
            raise HTTPError(400, reason=msg) # missing data
            
        if "points" in body:
            points = body['points']
            if type(points) != list:
                msg = "Bad Request: expecting list of points"
                log.info(msg)
                raise HTTPError(400, reason=msg)
            if 'start' in body or 'stop' in body or 'step' in body:
                msg = "Bad Request: can use hyperslab selection and points selection in one request"
                log.info(msg)
                raise HTTPError(400, reason=msg)
            if len(points) > len(value):
                msg = "Bad Request: more points provided than values"
                log.info(msg)
                raise HTTPError(400, reason=msg)
        else:
            # hyperslab selection
            if 'start' in body:
                start = body['start']
            if 'stop' in body:
                stop = body['stop']
            if 'step' in body:
                step = body['step']
                            
        data = body["value"]
        
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                item = db.getDatasetItemByUuid(reqUuid)
                dsetshape = item['shape']
                dims = dsetshape['dims']
                rank = len(dims) 
                if points:
                    for point in points:
                        pass  # todo        
                else:
                    slices = self.getHyperslabSelection(dims, start, stop, step)
                    # todo - check that the types are compatible
                    db.setDatasetValuesByUuid(reqUuid, data, slices)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
        
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
            msg = "Internal Server Error: unexpected uri: " + uri
            log.error(msg)
            raise HTTPError(500, reason=msg)
        
        npos = idpart.find('/')
        if npos <= 0:
            msg = "Bad Request: URI is invalid"
            log.info(msg)
            raise HTTPError(400, reason=msg)  
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
            msg = "Bad Request: URI is invalid"
            log.info(msg)
            raise HTTPError(400, reason=msg)  
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
            msg = "Internal Server Error: collection name unexpected"
            log.error(msg)
            raise HTTPError(500, reason=msg)   # shouldn't get routed here in this case
    
        return col_name
        
        
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('AttrbiuteHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        
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
        
        
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                if attr_name != None:
                    item = db.getAttributeItem(col_name, reqUuid, attr_name)
                    items.append(item)
                else:
                    # get all attributes (but without data)
                    items = db.getAttributeItems(col_name, reqUuid, marker, limit)
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
                         
        
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
        log.info('remote_ip: ' + self.request.remote_ip)
        
        domain = self.request.host
        col_name = self.getRequestCollectionName()
        reqUuid = self.getRequestId()
        attr_name = self.getRequestName()
        if attr_name == None:
            msg = "Bad Request: attribute name not supplied"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        body = None
        try:
            body = json.loads(self.request.body)
        except ValueError as e:
            msg = "JSON Parser Error: " + e.message
            log.info(msg)
            raise HTTPError(400, reason=msg )
            
        if "type" not in body:
            log.info("Type not supplied")
            raise HTTPError(400)  # missing type
            
        if "value" not in body:
            msg = "Bad Request: value not specified"
            log.info(msg)
            raise HTTPError(400, reason=msg)  # missing value
          
        shape = () # default as empty tuple (will create a scalar attribute)
        if shape in body:    
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
            msg = "Bad Request: invalid shape argument"
            log.info(msg)
            raise HTTPError(400, reason=msg)
            
        # validate shape
        for extent in shape:
            if type(extent) != int:
                msg = "Bad Request: invalid shape type"
                log.info(msg)
                raise HTTPError(400, reason=msg)
            if extent < 0:
                msg = "Bad Request: invalid shape (negative extent)"
                log.info(msg)
                raise HTTPError(400, reason=msg)   
                
        # convert list values to tuples (otherwise h5py is not happy)
        data = self.convertToTuple(value)
                   
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                db.createAttribute(col_name, reqUuid, attr_name, shape, datatype, data)
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
                
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
        log.info('remote_ip: ' + self.request.remote_ip)
        obj_uuid = self.getRequestId()
        domain = self.request.host
        col_name = self.getRequestCollectionName()
        attr_name = self.getRequestName()
        if attr_name == None:
            msg = "Bad Request: attribute name not specified"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        
        response = { }
        hrefs = []
        rootUUID = None
        
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                db.deleteAttribute(col_name, obj_uuid, attr_name)
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
            
        # got everything we need, put together the response
        href = self.request.protocol + '://' + domain + '/' 
        root_href = href + 'groups/' + rootUUID
        owner_href = href + col_name + '/' + obj_uuid 
        self_href = owner_href + '/attributes'
            
        hrefs.append({'rel': 'self',       'href': self_href})
        hrefs.append({'rel': 'owner',      'href': owner_href })
        hrefs.append({'rel': 'root',       'href': root_href }) 
        hrefs.append({'rel': 'home',       'href': href }) 
        response['hrefs'] = hrefs 
        
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))  
        
        log.info("Attribute delete succeeded")
                
         
class GroupHandler(RequestHandler):
    def getRequestId(self):
        log = logging.getLogger("h5serv")
        uri = self.request.uri
        npos = uri.rfind('/')
        if npos < 0:
            msg = "Internal Server Error: unexpected routing"
            log.error(msg)
            raise HTTPError(500, reason=msg)  # should not get routed to GroupHandler in this case
        if npos == len(uri) - 1:
            msg = "Bad Request: id could not be found in URI"
            log.info(msg)
            raise HTTPError(400, message=msg)
        id = uri[(npos+1):]
        log.info('got id: [' + id + ']')
    
        return id
            
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('GroupHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        reqUuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        response = { }
             
        hrefs = []
        rootUUID = None
        item = None
        
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                item = db.getGroupItemByUuid(reqUuid)
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
                         
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
        log.info('remote_ip: ' + self.request.remote_ip)
        uuid = self.getRequestId()
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                db.deleteObjectByUuid('group', uuid)
                rootUUID = db.getUUIDByPath('/') 
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
         
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
        log.info('remote_ip: ' + self.request.remote_ip)
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
        
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                items = db.getCollection("groups", marker, limit)
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
                         
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
        log.info('remote_ip: ' + self.request.remote_ip)
        if self.request.uri != '/groups':
            msg = "Method Not Allowed: bad group post request"
            log.info(msg)
            raise HTTPError(405, reason=msg)  # Method not allowed
        
        parent_group_uuid = None
        link_name = None
        
        body = {}
        if self.request.body:
            try:
                body = json.loads(self.request.body)
            except ValueError as e:
                msg = "JSON Parser Error: " + e.message
                log.info(msg)
                raise HTTPError(400, reason=msg )
        
        if "link" in body:    
            link_options = body["link"]
            if "id" not in link_options or "name" not in link_options:
                msg = "Bad Request: missing link parameter"
                log.info(msg)
                raise HTTPError(400, reason=msg)
            parent_group_uuid = link_options["id"]
            link_name = link_options["name"]
            log.info("add link to: " + parent_group_uuid + " with name: " + link_name)
               
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
              
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                if parent_group_uuid:
                    parent_group_item = db.getGroupItemByUuid(parent_group_uuid)
                grpUUID = db.createGroup()
                item = db.getGroupItemByUuid(grpUUID)
                # if link info is provided, link the new group
                if parent_group_uuid:
                    # link the new dataset
                    db.linkObject(parent_group_uuid, grpUUID, link_name) 
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)      
           
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
        log.info('remote_ip: ' + self.request.remote_ip)
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        # Get optional query parameters
        limit = self.get_query_argument("Limit", 0)
        if type(limit) is not int:
            try:
                limit = int(limit)
            except ValueError:
                msg = "Bad Request: expected int type for limit"
                log.info(msg)
                raise HTTPError(400, reason=msg) 
        marker = self.get_query_argument("Marker", None)
        
        response = { }
        hrefs = []
        rootUUID = None
             
        items = None
        
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                items = db.getCollection("datasets", marker, limit)
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
                         
        # write the response
        response['datasets'] = items
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',       'href': href + 'datasets' })
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'home',       'href': href }) 
        response['hrefs'] = hrefs
         
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        
    def post(self):
        log = logging.getLogger("h5serv")
        log.info('DatasetHandler.post host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        if self.request.uri != '/datasets':
            msg = "Method not Allowed: invalid datasets post request"
            log.info(msg)
            raise HTTPError(405, reason=msg)  # Method not allowed
               
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        shape = None
        group_uuid = None
        link_name = None
        
        body = None
        try:
            body = json.loads(self.request.body)
        except ValueError as e:
            msg = "JSON Parser Error: " + e.message
            log.info(msg)
            raise HTTPError(400, reason=msg )
        
        if "type" not in body:
            msg = "Bad Request: Type not specified"
            log.info(msg)
            raise HTTPError(400, reason=msg)  # missing type
            
        if "shape" in body:
            shape = body["shape"]
            if type(shape) == int:
                dim1 = shape
                shape = [dim1]
            elif type(shape) == list or type(shape) == tuple: 
                pass # can use as is
            else:
                msg="Bad Request: shape is invalid"
                log.info(msg)
                raise HTTPError(400, reason=msg)
        else:
            shape = ()  # empty tuple
            
        if "link" in body:          
            link_options = body["link"]
            print link_options
            if "id" not in link_options or "name" not in link_options:
                msg="Bad Request: No 'name' or 'id' not specified"
                log.info(msg)
                raise HTTPError(400, reason=msg)
                
            group_uuid = link_options["id"]
            link_name = link_options["name"]
            log.info("add link to: " + group_uuid + " with name: " + link_name);
            
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
                msg="Bad Request: maxshape is invalid"
                log.info(msg)
                raise HTTPError(400, reason=msg)     
           
        # validate shape
        for extent in shape:
            if type(extent) != int:
                msg="Bad Request: Invalid shape type"
                log.info(msg)
                raise HTTPError(400, reason=msg)
            if extent < 0:
                msg="Bad Request: shape dimension is negative"
                log.info("msg")
                raise HTTPError(400, reason=msg) 
            
        if maxshape:
            if len(maxshape) != len(shape):
                msg="Bad Request: maxshape array length must equal shape array length"
                log.info(msg)
                raise HTTPError(400, reason=msg)
            for i in range(len(shape)):
                maxextent = maxshape[i]
                if maxextent != 0 and maxextent < shape[i]:
                    msg="Bad Request: Maxshape extent can't be smaller than shape extent"
                    log.info(msg)
                    raise HTTPError(400, reason=msg)
                if maxextent == 0:
                    maxshape[i] = None  # this indicates unlimited
        
        item = None
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                if group_uuid:
                    group_item = db.getGroupItemByUuid(group_uuid)
                rootUUID = db.getUUIDByPath('/')
                item = db.createDataset(datatype, shape, maxshape)
                if group_uuid:
                    # link the new dataset
                    db.linkObject(group_uuid, item['id'], link_name)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
                
        response = { }
      
        # got everything we need, put together the response
        hrefs = [ ]
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',       'href': href + 'datasets/' + item['id']})
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'attributes', 'href': href + 'datasets/' + item['id'] + '/attributes'})   
        hrefs.append({'rel': 'value', 'href': href + 'datasets/' + item['id'] + '/value'})        
        response['id'] = item['id']
        response['attributeCount'] = item['attributeCount']
        response['hrefs'] = hrefs
        response['created'] = unixTimeToUTC(item['ctime'])
        response['lastModified'] = unixTimeToUTC(item['mtime'])
        
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))  
        self.set_status(201)  # resource created
        
class TypeCollectionHandler(RequestHandler):
            
    def get(self):
        log = logging.getLogger("h5serv")
        log.info('TypeCollectionHandler.get host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        domain = self.request.host
        filePath = getFilePath(domain) 
        verifyFile(filePath)
        
        # Get optional query parameters
        limit = self.get_query_argument("Limit", 0)
        if type(limit) is not int:
            try:
                limit = int(limit)
            except ValueError:
                msg = "Bad Request: expected int type for Limit"
                log.info(msg)
                raise HTTPError(400, reason=msg) 
        marker = self.get_query_argument("Marker", None)
        
        response = { }
        hrefs = []
        rootUUID = None
             
        items = None
        try:
            with Hdf5db(filePath) as db:
                items = db.getCollection("datatypes", marker, limit)
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
                         
        # write the response
        response['datatypes'] = items
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',       'href': href + 'datatypes' })
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'home',       'href': href }) 
        response['hrefs'] = hrefs
        
         
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        
    def post(self):
        log = logging.getLogger("h5serv")
        log.info('TypeHandler.post host=[' + self.request.host + '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        if self.request.uri != '/datatypes':
            msg = "Method not Allowed: invalid URI"
            log.info(msg)
            raise HTTPError(405, reason=msg)  # Method not allowed
               
        domain = self.request.host
        filePath = getFilePath(domain)
        verifyFile(filePath, True)
        
        body = None
        try:
            body = json.loads(self.request.body)
        except ValueError as e:
            msg = "JSON Parser Error: " + e.message
            log.info(msg)
            raise HTTPError(400, reason=msg )
            
        parent_group_uuid = None
        link_name = None
        
        if "type" not in body:
            msg = "Type not specified"
            log.info(msg)
            raise HTTPError(400, reason=msg)  # missing type
            
        if "link" in body:    
            link_options = body["link"]
            if "id" not in link_options or "name" not in link_options:
                msg = "Bad Request: missing link parameter"
                log.info(msg)
                raise HTTPError(400, reason=msg)
            parent_group_uuid = link_options["id"]
            link_name = link_options["name"]
            log.info("add link to: " + parent_group_uuid + " with name: " + link_name)
            
        datatype = body["type"]     
        
        item = None
        rootUUID = None

        
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                if parent_group_uuid:
                    parent_group_item = db.getGroupItemByUuid(parent_group_uuid)
                item = db.createCommittedType(datatype)
                # if link info is provided, link the new group
                if parent_group_uuid:
                    # link the new dataset
                    db.linkObject(parent_group_uuid, item['id'], link_name) 
                            
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
            
        response = { }
      
        # got everything we need, put together the response
        hrefs = [ ]
        href = self.request.protocol + '://' + domain + '/'
        hrefs.append({'rel': 'self',       'href': href + 'datatypes/' + item['id']})
        hrefs.append({'rel': 'root',       'href': href + 'groups/' + rootUUID}) 
        hrefs.append({'rel': 'attributes', 'href': href + 'datatypes/' + item['id'] + '/attributes'})   
        response['id'] = item['id']
        response['attributeCount'] = 0
        response['hrefs'] = hrefs
        response['created'] = unixTimeToUTC(item['ctime'])
        response['lastModified'] = unixTimeToUTC(item['mtime'])
        
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response)) 
        self.set_status(201)  # resource created
          
        
class RootHandler(RequestHandler):

    def getRootResponse(self, filePath):
        log = logging.getLogger("h5serv")
        # used by GET / and PUT /
        domain = self.request.host
        filePath = getFilePath(domain)
        
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror) 
         
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
        log.info('remote_ip: ' + self.request.remote_ip)
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
        log.info('remote_ip: ' + self.request.remote_ip)
        filePath = getFilePath(self.request.host)
        log.info("put filePath: " + filePath)
        if op.isfile(filePath):
            msg = "Conflict: resource exists"
            log.info(msg)    
            raise HTTPError(409, reason=msg)  # Conflict - is this the correct code?
        # create directories as needed
        makeDirs(op.dirname(filePath))
        log.info("creating file: [" + filePath + "]")
        
        try:
            Hdf5db.createHDF5File(filePath)
        except IOError as e:
            log.info("IOError creating new HDF5 file: " + str(e.errno) + " " + e.strerror)
            raise HTTPError(500, "Unexpected error: unable to create collection") 
            
        response = self.getRootResponse(filePath)
        
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        self.set_status(201)  # resource created
          
    def delete(self): 
        log = logging.getLogger("h5serv")
        log.info('RootHandler.delete ' + self.request.host)  
        log.info('remote_ip: ' + self.request.remote_ip) 
        filePath = getFilePath(self.request.host)
        verifyFile(filePath, True)
        
        if not op.isfile(filePath):
            # file not there
            msg = "Not found: resource does not exist"
            log.info(msg)
            raise HTTPError(404, reason=msg)  # Not found
             
        if not os.access(filePath, os.W_OK):
            # file is read-only
            msg = "Forbidden: Resource is read-only"
            log.info(msg)
            raise HTTPError(403, reason=msg) # Forbidden
        
        try:    
            os.remove(filePath)  
        except IOError as ioe:
            log.info("IOError deleting HDF5 file: " + str(e.errno) + " " + e.strerror)
            raise HTTPError(500, "Unexpected error: unable to delete collection") 
              
        
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
