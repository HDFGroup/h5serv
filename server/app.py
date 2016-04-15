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
    
import time
import signal
import logging
import logging.handlers
import os
import os.path as op
import json
import tornado.httpserver
import sys
import ssl
import base64
import binascii
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url, HTTPError
from tornado.escape import json_encode, json_decode, url_escape, url_unescape

from h5json import Hdf5db
import h5json

import config
from querydb import Querydb
from timeUtil import unixTimeToUTC
import fileUtil  
import tocUtil  
from httpErrorUtil import errNoToHttpStatus
from passwordUtil import getUserId, getUserName, validateUserPassword

def to_bytes(a_string):
    if type(a_string) is unicode:
        return a_string.encode('utf-8')
    else:
        return a_string
        
def to_str(a_string):
    if type(a_string) is bytes:
        return a_string.decode('utf-8')
    else:
        return a_string

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


class BaseHandler(tornado.web.RequestHandler):

    """
    Enable CORS
    """
    def set_default_headers(self):
        cors_domain = config.get('cors_domain')
        if cors_domain:
            self.set_header('Access-Control-Allow-Origin', cors_domain)
     
    """
    Set allows heards per CORS policy
    """        
    def options(self):
        cors_domain = config.get('cors_domain')
        if cors_domain:
            self.set_header('Access-Control-Allow-Headers', 'Content-type,')

    """
    Override of Tornado get_current_user
    """
    def get_current_user(self):
        user = None
        pswd = None
        #print(self.request.headers.get('Authorization', ''))
        scheme, _, token = auth_header = self.request.headers.get(
            'Authorization', '').partition(' ')
        if scheme and token and scheme.lower() == 'basic':
            try:
                if six.PY3:
                    token_decoded = base64.decodebytes(to_bytes(token))
                else:
                    token_decoded = base64.decodestring(token)
            except binascii.Error:
                raise HTTPError(400, "Malformed authorization header")
            if token_decoded.index(b':') < 0:
                raise HTTPError(400, "Malformed authorization header")
            user, _, pswd = token_decoded.partition(b':')
        if user and pswd:
            validateUserPassword(user, pswd)  # throws exception if passwd is not valid
            self.userid = getUserId(user)
            return self.userid
        else:
            self.userid = -1
            return None

    def verifyAcl(self, acl, action):
        """Verify ACL for given action. Raise exception if not
        authorized.

        """
        if acl[action]:
            return
        if self.userid <= 0:
            self.set_status(401)
            self.set_header('WWW-Authenticate', 'basic realm="h5serv"')
            raise HTTPError(401, "Unauthorized")
            # raise HTTPError(401, message="provide  password")
        # validated user, but doesn't have access
        log = logging.getLogger("h5serv")
        log.info("unauthorized access for userid: " + str(self.userid))
        raise HTTPError(403, "Access is not permitted")

    def getDomain(self):
        """Helper method - return domain auth based on either query
        param or host header

        """
        domain = self.get_query_argument("host", default=None)
        if not domain:
            domain = self.request.host
        return domain
        
    def setDefaultAcl(self):
        """ Set default ACL for user TOC file.
        """
        log = logging.getLogger("h5serv")
        log.info("setDeaultAcl -- userid: " + str(self.userid))
        if self.userid <= 0:
            raise HTTPError(500, "Expected userid")
        username = getUserName(self.userid)
        filePath = tocUtil.getTocFilePath(username)
        try:
            fileUtil.verifyFile(filePath)
        except HTTPError:
            log.info("toc file doesn't exist, returning")
            return
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                current_user_acl = db.getAcl(rootUUID, self.userid)
                acl = db.getDefaultAcl()
                acl['userid'] = userid
                fields = ('create', 'read', 'update', 'delete', 'readACL', 'updateACL')  
                for field in fields:
                    acl[field] = True 
                db.setAcl(obj_uuid, acl)
                     
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)
         
        
    def getFilePath(self, domain, checkExists=True):
        """ Helper method - return file path for given domain.
        """
         
        log = logging.getLogger("h5serv")
        log.info("getFilePath: " + domain)
        tocFilePath = fileUtil.getTocFilePathForDomain(domain)
        log.info("tocFilePath: " + tocFilePath)
        if not fileUtil.isFile(tocFilePath):
            tocUtil.createTocFile(tocFilePath)
            if self.userid > 0:
                # setup the permision to grant this user exclusive write access
                # and public read for everyone
                self.setDefaultAcl()
            
        filePath = fileUtil.getFilePath(domain)
        if checkExists:
            fileUtil.verifyFile(filePath)  # throws exception if not found  
        
        return filePath
        
    def isWritable(self, filePath):
        """Helper method - raise 403 error if given file path is not writable
        """
        fileUtil.verifyFile(filePath, writable=True)
        
    def isTocFilePath(self, filePath):
        """Helper method - return True if this is a TOC file apth
        """
        if tocUtil.isTocFilePath(filePath):
            return True
        else:
            return False
            

    def getRequestId(self):
        """
        Helper method - return request uuid from request URI
        URI' are of the form:
            /groups/<uuid>/xxx
            /datasets/<uuid>/xxx
            /datatypes/<uuid>/xxx
        extract the <uuid> and return it.
        Throw 500 error is the URI is not in the above form
        """
        log = logging.getLogger("h5serv")

        uri = self.request.uri

        # strip off any query params
        npos = uri.find('?')
        if npos > 0:
            uri = uri[:npos]

        if uri.startswith('/groups/'):
            uri = uri[len('/groups/'):]  # get stuff after /groups/
        elif uri.startswith('/datasets/'):
            uri = uri[len('/datasets/'):]  # get stuff after /datasets/
        elif uri.startswith('/datatypes/'):
            uri = uri[len('/datatypes/'):]  # get stuff after /datatypes/
        else:

            msg = "unexpected uri: " + uri
            log.error(msg)
            raise HTTPError(500, reason=msg)

            return None
        npos = uri.find('/')
        if npos < 0:
            uuid = uri
        elif npos == 0:
            msg = "Bad Request: uri is invalid"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        else:
            uuid = uri[:npos]

        log.info('got uuid: [' + uuid + ']')

        return uuid
        
    """
    Get requested content type.  Returns either "binary" if the accept header is 
    octet stream, otherwise json.
    Currently does not support q fields.
    """
    def getAcceptType(self):
        log = logging.getLogger("h5serv")
        content_type = self.request.headers.get('Accept')
        if content_type:
            log.info("CONTENT_TYPE:" + content_type)
        if content_type == "application/octet-stream":
            return "binary"
        else:
            return "json"
            

class LinkCollectionHandler(BaseHandler):
    def get(self):
        log = logging.getLogger("h5serv")
        log.info(
            'LinkCollectionHandler.get host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        reqUuid = self.getRequestId()
        domain = self.getDomain()
        filePath = self.getFilePath(domain)

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

        response = {}

        items = None
        rootUUID = None
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                current_user_acl = db.getAcl(reqUuid, self.userid)
                self.verifyAcl(current_user_acl, 'read')  # throws exception is unauthorized
                items = db.getLinkItems(reqUuid, marker=marker, limit=limit)

        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        # got everything we need, put together the response
        links = []
        hrefs = []
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({
            'rel': 'self',
            'href': href + 'groups/' + reqUuid + '/links' + hostQuery
        })
        for item in items:
            link_item = {}
            link_item['class'] = item['class']
            link_item['title'] = item['title']
            link_item['href'] = item['href'] = href + 'groups/' + reqUuid + '/links/' + item['title'] + hostQuery
            if item['class'] == 'H5L_TYPE_HARD':
                link_item['id'] = item['id']
                link_item['collection'] = item['collection']
                link_item['target'] = href + item['collection'] + '/' + item['id'] + hostQuery
            elif item['class'] == 'H5L_TYPE_SOFT':
                link_item['h5path'] = item['h5path']
            elif item['class'] == 'H5L_TYPE_EXTERNAL':
                link_item['h5path'] = item['h5path']
                link_item['h5domain'] = item['file']
                if link_item['h5domain'].endswith(config.get('domain')):
                    target = self.request.protocol + '://'
                    targetHostQuery = ''
                    if hostQuery or self.isTocFilePath(filePath):
                        target += self.request.host
                        targetHostQuery = '?host=' + link_item['h5domain']
                    else:
                        target += link_item['h5domain']
                    if item['h5path'] == '/':
                        target += '/'
                    else:
                        target += '/#h5path(' + link_item['h5path'] + ')'
                    target += targetHostQuery
                    link_item['target'] = target

            links.append(link_item)

        response['links'] = links

        hrefs.append({
            'rel': 'root',
            'href': href + 'groups/' + rootUUID + hostQuery
        })
        home_dir = config.get("home_dir")
        hrefs.append({'rel': home_dir, 'href': href + hostQuery})
        hrefs.append({
            'rel': 'owner',
            'href': href + 'groups/' + reqUuid + hostQuery
        })
        response['hrefs'] = hrefs
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))


class LinkHandler(BaseHandler):
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
        npos = linkName.rfind('?')
        if npos >= 0:
            # trim off the query params
            linkName = linkName[:npos]
        
        linkName = url_unescape(linkName)
        return linkName

    def get(self):
        log = logging.getLogger("h5serv")
        log.info(
            'LinkHandler.get host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        reqUuid = self.getRequestId()
        domain = self.getDomain()
        filePath = self.getFilePath(domain)
        linkName = self.getName(self.request.uri)
        log.info("linkName:["+linkName+"]")

        response = {}

        rootUUID = None
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(reqUuid, self.userid)
                self.verifyAcl(acl, 'read')  # throws exception is unauthorized
                item = db.getLinkItemByUuid(reqUuid, linkName)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

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
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({
            'rel': 'self',
            'href': href + 'groups/' + reqUuid + '/links/' + url_escape(linkName) + hostQuery
        })
        hrefs.append({
            'rel': 'root',
            'href': href + 'groups/' + rootUUID + hostQuery
        })
        hrefs.append({
            'rel': 'home', 'href': href + hostQuery
        })
        hrefs.append({
            'rel': 'owner',
            'href': href + 'groups/' + reqUuid + hostQuery
        })

        target = None
        if item['class'] == 'H5L_TYPE_HARD':
            target = href + item['collection'] + '/' + item['id'] + hostQuery
        elif item['class'] == 'H5L_TYPE_SOFT':
            target = href + '/#h5path(' + item['h5path'] + ')' + hostQuery
        elif item['class'] == 'H5L_TYPE_EXTERNAL':
            if item['h5domain'].endswith(config.get('domain')):
                target = self.request.protocol + '://'
                targetHostQuery = ''
                if hostQuery or self.isTocFilePath(filePath):
                    target += self.request.host
                    targetHostQuery = '?host=' + item['h5domain']
                else:
                    target += item['h5domain']
                if item['h5path'] == '/':
                    target += '/'
                else:
                    target += '/#h5path(' + item['h5path'] + ')'
                target += targetHostQuery

        if target:
            hrefs.append({'rel': 'target', 'href': target})

        response['hrefs'] = hrefs
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))

    def put(self):
        log = logging.getLogger("h5serv")
        log.info(
            'LinkHandler.put host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()
        # put - create a new link
        # patterns are:
        # PUT /groups/<id>/links/<name> {id: <id> }
        # PUT /groups/<id>/links/<name> {h5path: <path> }
        # PUT /groups/<id>/links/<name> {h5path: <path>, h5domain: <href> }
        reqUuid = self.getRequestId()

        linkName = self.getName(self.request.uri)

        body = None
        try:
            body = json_decode(self.request.body)
        except ValueError as e:
            msg = "JSON Parser Error: " + e.message
            log.info(msg)
            raise HTTPError(400, reason=msg)

        childUuid = None
        h5path = None
        h5domain = None
        filename = None   # fake filename

        if "id" in body:
            childUuid = body["id"]
            if childUuid is None or len(childUuid) == 0:
                msg = "Bad Request: id not specified"
                log.info(msg)
                raise HTTPError(400, reason=msg)
        elif "h5path" in body:
            # todo
            h5path = body["h5path"]
            if h5path is None or len(h5path) == 0:
                raise HTTPError(400)

            # if h5domain is present, this will be an external link
            if "h5domain" in body:
                h5domain = body["h5domain"]
        else:
            msg = "Bad request: missing required body keys"
            log.info(msg)
            raise HTTPError(400, reasoln=msg)

        domain = self.getDomain()
        filePath = self.getFilePath(domain)
        if self.isTocFilePath(filePath):
            msg = "Forbidden: links can not be directly created in TOC domain"
            log.info(msg)
            raise HTTPError(403, reason=msg)

        response = {}

        rootUUID = None
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(reqUuid, self.userid)
                self.verifyAcl(acl, 'create')  # throws exception is unauthorized
                if childUuid:
                    db.linkObject(reqUuid, childUuid, linkName)
                elif h5domain:
                    db.createExternalLink(reqUuid, h5domain, h5path, linkName)
                elif h5path:
                    db.createSoftLink(reqUuid, h5path, linkName)

        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        hrefs = []
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({
            'rel': 'self',
            'href': href + 'groups/' + reqUuid + '/links/' + url_escape(linkName) + hostQuery
        })
        hrefs.append({
            'rel': 'root',
            'href': href + 'groups/' + rootUUID + hostQuery
        })
        hrefs.append({
            'rel': 'home',
            'href': href + hostQuery
        })
        hrefs.append({
            'rel': 'owner', 'href': href + 'groups/' + reqUuid + hostQuery})
        response['hrefs'] = hrefs

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        self.set_status(201)

    def delete(self):
        log = logging.getLogger("h5serv")
        log.info('LinkHandler.delete ' + self.request.host)
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()
        reqUuid = self.getRequestId()

        linkName = self.getName(self.request.uri)

        log.info(
            "delete link  name[: " + linkName + "] parentUuid: " + reqUuid)

        domain = self.getDomain()
        response = {}
        rootUUID = None
        filePath = self.getFilePath(domain)
        self.isWritable(filePath)
        if self.isTocFilePath(filePath):
            msg = "Forbidden: links can not be directly modified in TOC domain"
            log.info(msg)
            raise HTTPError(403, reason=msg)
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(reqUuid, self.userid)
                self.verifyAcl(acl, 'delete')  # throws exception is unauthorized
                db.unlinkItem(reqUuid, linkName)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        hrefs = []
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({
            'rel': 'root',
            'href': href + 'groups/' + rootUUID + hostQuery
        })
        hrefs.append({'rel': 'home', 'href': href + hostQuery})
        hrefs.append({
            'rel': 'owner', 'href': href + 'groups/' + reqUuid + hostQuery})

        response['hrefs'] = hrefs
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))


class AclHandler(BaseHandler):
    def getRequestCollectionName(self):
        log = logging.getLogger("h5serv")
        # request is in the form /(datasets|groups|datatypes)/<id>/acls(/<username>),
        # or /acls(/<username>) for domain acl
        # return datasets | groups | datatypes
        uri = self.request.uri

        npos = uri.find('/')
        if npos < 0:
            log.info("bad uri")
            raise HTTPError(400)
        if uri.startswith('/acls/'):
            # domain request - return group collection
            return 'groups'

        uri = uri[(npos+1):]

        npos = uri.find('/')  # second '/'
        if npos < 0:
            # uri is "/acls"
            return "groups"
        col_name = uri[:npos]

        log.info('got collection name: [' + col_name + ']')
        if col_name not in ('datasets', 'groups', 'datatypes'):
            msg = "Internal Server Error: collection name unexpected"
            log.error(msg)
            raise HTTPError(500, reason=msg)   # shouldn't get routed here in this case

        return col_name

    def getName(self):
        log = logging.getLogger("h5serv")
        uri = self.request.uri

        if uri == '/acls':
            return None  # default domain acl
        # helper method
        # uri should be in the form: /group/<uuid>/acl/<username>
        # this method returns name
        npos = uri.find('/acls/')
        if npos < 0:
            # shouldn't be possible to get here
            msg = "Internal Server Error: Unexpected uri"
            log.error(msg)
            raise HTTPError(500, reason=msg)
        if npos+len('/acls/') >= len(uri):
            # no name specified
            msg = "Bad Request: no name specified"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        userName = uri[npos+len('/acls/'):]
        if userName.find('/') >= 0:
            # can't have '/' in link name
            msg = "Bad Request: invalid linkname, '/' not allowed"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        npos = userName.rfind('?')
        if npos >= 0:
            # trim off the query params
            userName = userName[:npos]
        return userName

    def convertUserIdToUserName(self, acl_in):
        """
        convertUserIdToUserName - replace userids with username
        """
        log = logging.getLogger("h5serv")
        acl_out = None
        if type(acl_in) in (list, tuple):
            # convert list to list
            acl_out = []
            for item in acl_in:
                acl_out.append(self.convertUserIdToUserName(item))
        else:
            acl_out = {}
            for key in acl_in.keys():
                if key == 'userid':
                    # convert userid to username
                    userid = acl_in['userid']

                    user_name = '???'
                    if userid == 0:
                        user_name = 'default'
                    else:
                        user_name = getUserName(userid)
                        if user_name is None:
                            log.warning(
                                "user not found for userid: " + str(userid))
                    acl_out['userName'] = user_name
                else:
                    value = acl_in[key]
                    acl_out[key] = True if value else False
        return acl_out

    def get(self):
        log = logging.getLogger("h5serv")
        log.info(
            'AclHandler.get host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)

        self.get_current_user()
        req_uuid = None
        if not self.request.uri.startswith("/acls"):
            # get UUID for object unless this is a get on domain acl
            req_uuid = self.getRequestId()

        domain = self.getDomain()

        rootUUID = None
        filePath = self.getFilePath(domain)
        userName = self.getName()

        col_name = self.getRequestCollectionName()

        req_userid = None
        if userName:
            if userName == 'default':
                req_userid = 0
            else:
                req_userid = getUserId(userName)
                if req_userid is None:
                    # username not found
                    msg = "username does not exist"
                    log.info(msg)
                    raise HTTPError(404, reason=msg)

        request = {}
        acl = None
        current_user_acl = None
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                if req_uuid:
                    obj_uuid = req_uuid
                else:
                    obj_uuid = rootUUID

                current_user_acl = db.getAcl(obj_uuid, self.userid)
                self.verifyAcl(current_user_acl, 'readACL')  # throws exception is unauthorized
                if req_userid is None:
                    acl = db.getAcls(obj_uuid)
                else:
                    acl = db.getAcl(obj_uuid, req_userid)

        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        response = {}
        acl = self.convertUserIdToUserName(acl)

        if userName is None:
            userName = ''  # for string concat in the hrefs
            response['acls'] = acl
        else:
            response['acl'] = acl

        hrefs = []
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        if current_user_acl:
            hrefs.append({
                'rel': 'self',
                'href': href + col_name + '/' + obj_uuid + '/acls/' + url_escape(userName) + hostQuery
            })
        else:
            hrefs.append({
                'rel': 'self',
                'href': href + col_name + '/' + obj_uuid + '/acls' + hostQuery
            })
        hrefs.append({
            'rel': 'root',
            'href': href + 'groups/' + rootUUID + hostQuery
        })
        hrefs.append({'rel': 'home', 'href': href + hostQuery})
        hrefs.append({
            'rel': 'owner',
            'href': href + col_name + '/' + obj_uuid + hostQuery
        })

        response['hrefs'] = hrefs
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))

    def put(self):
        log = logging.getLogger("h5serv")
        log.info(
            'AclHandler.put host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.current_user = self.get_current_user()
        # put - create/update an acl
        # patterns are:
        # PUT /group/<id>/acls/<name> {'read': True, 'write': False }
        # PUT /acls/<name> {'read'... }

        req_uuid = None
        if not self.request.uri.startswith("/acls/"):
            req_uuid = self.getRequestId()
        col_name = self.getRequestCollectionName()
        userName = url_unescape(self.getName())

        if userName is None or len(userName) == 0:
            msg = "Bad Request: username not provided"
            log.info(msg)
            raise HTTPError(400, reason=msg)

        req_userid = None   # this is the userid of the acl we'll be updating
        # self.userid is the userid of the requestor
        if userName == 'default':
            req_userid = 0
        else:
            req_userid = getUserId(userName)

        if req_userid is None:
            msg = "Bad Request: username not found"
            log.info(msg)
            raise HTTPError(400, reason=msg)

        body = None
        try:
            body = json_decode(self.request.body)
        except ValueError as e:
            msg = "JSON Parser Error: " + e.message
            log.info(msg)
            raise HTTPError(400, reason=msg)

        if 'perm' not in body:
            msg = "Bad Request: acl not found in request body"
            log.info(msg)
            raise HTTPError(400, reason=msg)

        perm = body['perm']
        acl = {}
        acl['userid'] = req_userid
        for key in ('create', 'read', 'update',
                    'delete', 'readACL', 'updateACL'):
            if key in perm:
                acl[key] = 1 if perm[key] else 0
        if len(acl) == 1:
            msg = "Bad Request: no acl permissions found in request body"
            log.info(msg)
            raise HTTPError(400, reason=msg)

        domain = self.getDomain()
        filePath = self.getFilePath(domain)

        response = {}

        rootUUID = None
        obj_uuid = None
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                if req_uuid is None:
                    obj_uuid = rootUUID
                else:
                    obj_uuid = req_uuid
                current_user_acl = db.getAcl(obj_uuid, self.userid)
                self.verifyAcl(current_user_acl, 'updateACL')  # throws exception is unauthorized
                db.setAcl(obj_uuid, acl)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        hrefs = []
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({
            'rel': 'self',
            'href': href + col_name + '/' + obj_uuid + '/acls/' + url_escape(userName) + hostQuery
        })
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID + hostQuery})
        hrefs.append({'rel': 'home', 'href': href + hostQuery})
        hrefs.append({
            'rel': 'owner',
            'href': href + col_name + '/' + obj_uuid + hostQuery
        })

        response['hrefs'] = hrefs

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        self.set_status(201)


class TypeHandler(BaseHandler):
    def get(self):
        log = logging.getLogger("h5serv")
        log.info(
            'TypeHandler.get host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        reqUuid = self.getRequestId()

        if not reqUuid:
            msg = "Bad Request: id is not specified"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        domain = self.getDomain()
        filePath = self.getFilePath(domain)

        response = {}
        hrefs = []
        rootUUID = None
        item = None
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(reqUuid, self.userid)
                self.verifyAcl(acl, 'read')  # throws exception is unauthorized
                item = db.getCommittedTypeItemByUuid(reqUuid)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        # got everything we need, put together the response
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({
            'rel': 'self',
            'href': href + 'datatypes/' + reqUuid + hostQuery
        })
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID + hostQuery})
        hrefs.append({
            'rel': 'attributes',
            'href': href + 'datatypes/' + reqUuid + '/attributes' + hostQuery
        })
        hrefs.append({'rel': 'home', 'href': href + hostQuery})
        response['id'] = reqUuid
        typeItem = item['type']
        response['type'] = h5json.getTypeResponse(typeItem)
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
        self.get_current_user()

        req_uuid = self.getRequestId()
        domain = self.getDomain()
        filePath = self.getFilePath(domain)
        self.isWritable(filePath)
        response = {}
        hrefs = []
        rootUUID = None
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(req_uuid, self.userid)
                self.verifyAcl(acl, 'delete')  # throws exception is unauthorized
                db.deleteObjectByUuid('datatype', req_uuid)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        # got everything we need, put together the response
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({'rel': 'self', 'href': href + 'datatypes' + hostQuery})
        hrefs.append({'rel': 'home', 'href': href + hostQuery})
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID + hostQuery})

        response['hrefs'] = hrefs

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))


class DatatypeHandler(BaseHandler):
    def get(self):
        log = logging.getLogger("h5serv")
        log.info(
            'DatatypeHandler.get host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        reqUuid = self.getRequestId()
        domain = self.getDomain()
        filePath = self.getFilePath(domain)

        response = {}
        hrefs = []
        rootUUID = None
        item = None
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(reqUuid, self.userid)
                self.verifyAcl(acl, 'read')  # throws exception is unauthorized
                item = db.getDatasetTypeItemByUuid(reqUuid)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        # got everything we need, put together the response
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({
            'rel': 'self',
            'href': href + 'datasets/' + reqUuid + '/type' + hostQuery
        })
        hrefs.append({
            'rel': 'owner', 'href': href + 'datasets/' + reqUuid + hostQuery})
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID + hostQuery})
        response['type'] = item['type']

        response['hrefs'] = hrefs

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))


class ShapeHandler(BaseHandler):

    def get(self):
        log = logging.getLogger("h5serv")
        log.info(
            'ShapeHandler.get host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        reqUuid = self.getRequestId()
        domain = self.getDomain()
        filePath = self.getFilePath(domain)

        response = {}
        hrefs = []
        rootUUID = None
        item = None

        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(reqUuid, self.userid)
                self.verifyAcl(acl, 'read')  # throws exception is unauthorized
                item = db.getDatasetItemByUuid(reqUuid)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        # got everything we need, put together the response
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({
            'rel': 'self', 'href': href + 'datasets/' + reqUuid + hostQuery})
        hrefs.append({
            'rel': 'owner', 'href': href + 'datasets/' + reqUuid + hostQuery})
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID + hostQuery})
        shape = item['shape']
        response['shape'] = shape
        response['created'] = unixTimeToUTC(item['ctime'])
        response['lastModified'] = unixTimeToUTC(item['mtime'])
        response['hrefs'] = hrefs

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))

    def put(self):
        log = logging.getLogger("h5serv")
        log.info(
            'ShapeHandler.put host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        reqUuid = self.getRequestId()
        domain = self.getDomain()
        filePath = self.getFilePath(domain)
        self.isWritable(filePath)

        response = {}
        hrefs = []
        rootUUID = None
        body = None
        try:
            body = json_decode(self.request.body)
        except ValueError as e:
            msg = "JSON Parser Error: " + e.message
            log.info(msg)
            raise HTTPError(400, reason=msg)

        if "shape" not in body:
            msg = "Bad Request: Shape not specified"
            log.info(msg)
            raise HTTPError(400, reason=msg)  # missing shape

        shape = body["shape"]
        if type(shape) == int:
            dim1 = shape
            shape = [dim1]
        elif type(shape) == list or type(shape) == tuple:
            pass  # can use as is
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
                acl = db.getAcl(reqUuid, self.userid)
                self.verifyAcl(acl, 'update')  # throws exception is unauthorized
                db.resizeDataset(reqUuid, shape)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        log.info("resize OK")
        # put together the response
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({
            'rel': 'self', 'href': href + 'datasets/' + reqUuid + hostQuery})
        hrefs.append({
            'rel': 'owner', 'href': href + 'datasets/' + reqUuid + hostQuery})
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID + hostQuery})
        response['hrefs'] = hrefs

        self.set_status(201)  # resource created
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))


class DatasetHandler(BaseHandler):

    def getPreviewQuery(self, shape_item):
        """Helper method - return query options for a "reasonable" size
        data preview selection. Return None if the dataset is small
        enough that a preview is not needed.

        """
        if shape_item['class'] != 'H5S_SIMPLE':
            return None
        dims = shape_item['dims']
        rank = len(dims)
        if rank == 0:
            return None

        count = 1
        for i in range(rank):
            count *= dims[i]

        if count <= 100:
            return None

        select = "?select=["

        ncols = dims[rank-1]
        if rank > 1:
            nrows = dims[rank-2]
        else:
            nrows = 1

        # use some rough heuristics to define the selection
        if ncols > 100:
            ncols = 100
        if nrows > 100:
            nrows = 100
        if nrows*ncols > 1000:
            nrows //= 10

        for i in range(rank):
            if i == rank-1:
                select += "0:" + str(ncols)
            elif i == rank-2:
                select += "0:" + str(nrows) + ","
            else:
                select += "0:1,"
        select += "]"
        return select

    def get(self):
        log = logging.getLogger("h5serv")
        log.info(
            'DatasetHandler.get host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        reqUuid = self.getRequestId()
        domain = self.getDomain()
        filePath = self.getFilePath(domain)

        response = {}
        hrefs = []
        rootUUID = None
        item = None
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(reqUuid, self.userid)
                self.verifyAcl(acl, 'read')  # throws exception is unauthorized
                item = db.getDatasetItemByUuid(reqUuid)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        # got everything we need, put together the response
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        previewQuery = self.getPreviewQuery(item['shape'])
        if hostQuery and previewQuery:
            previewQuery += "&host=" + self.get_query_argument("host")

        hrefs.append({
            'rel': 'self', 'href': href + 'datasets/' + reqUuid + hostQuery})
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID + hostQuery})
        hrefs.append({
            'rel': 'attributes',
            'href': href + 'datasets/' + reqUuid + '/attributes' + hostQuery
        })
        hrefs.append({
            'rel': 'data',
            'href': href + 'datasets/' + reqUuid + '/value' + hostQuery
        })
        if previewQuery:
            hrefs.append({
                'rel': 'preview',
                'href': href + 'datasets/' + reqUuid + '/value' + previewQuery
            })
        hrefs.append({'rel': 'home', 'href': href + hostQuery})
        response['id'] = reqUuid
        typeItem = item['type']
        response['type'] = h5json.getTypeResponse(typeItem)
        response['shape'] = item['shape']

        if 'creationProperties' in item:
            response['creationProperties'] = item['creationProperties']
        response['created'] = unixTimeToUTC(item['ctime'])
        response['lastModified'] = unixTimeToUTC(item['mtime'])
        response['attributeCount'] = item['attributeCount']
        response['hrefs'] = hrefs

        self.set_header('Content-Type', 'application/json')

        json_rsp = json_encode(response)

        self.write(json_rsp)

    def delete(self):
        log = logging.getLogger("h5serv")
        log.info(
            'DatasetHandler.delete host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        req_uuid = self.getRequestId()
        domain = self.getDomain()
        filePath = self.getFilePath(domain)
        self.isWritable(filePath)

        response = {}
        hrefs = []
        rootUUID = None

        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(req_uuid, self.userid)
                self.verifyAcl(acl, 'delete')  # throws exception is unauthorized
                db.deleteObjectByUuid('dataset', req_uuid)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        # write the response
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({'rel': 'self', 'href': href + 'datasets' + hostQuery})
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID + hostQuery})
        hrefs.append({'rel': 'home', 'href': href + hostQuery})
        response['hrefs'] = hrefs

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))


class ValueHandler(BaseHandler):

    def getSliceQueryParam(self, dim, extent):
        """
        Helper method - return slice for dim based on query params

        Query arg should be in the form: [<dim1>, <dim2>, ... , <dimn>]
         brackets are optional for one dimensional arrays.
         Each dimension, valid formats are:
            single integer: n
            start and end: n:m
            start, end, and stride: n:m:s
        """
        log = logging.getLogger("h5serv")
        # Get optional query parameters for given dim
        log.info("getSliceQueryParam: " + str(dim) + ", " + str(extent))
        query = self.get_query_argument("select", default='ALL')
        if query == 'ALL':
            # just return a slice for the entire dimension
            log.info("getSliceQueryParam: return default")
            return slice(0, extent)

        log.info("select query value: [" + query + "]")

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
                msg = "Bad Request: invalid selection parameter (can't convert to int) for dimension: " + str(dim)
                log.info(msg)
                raise HTTPError(400, reason=msg)
            stop = start
        elif dim_query == ':':
            # select everything
            pass
        else:
            fields = dim_query.split(":")
            if len(fields) > 3:
                msg = "Bad Request: Too many ':' seperators for dimension: " + str(dim)
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
                msg = "Bad Request: invalid selection parameter (can't convert to int) for dimension: " + str(dim)
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
        log.info(
            "dim query[" + str(dim) + "] returning: start: " +
            str(start) + " stop: " + str(stop) + " step: " + str(step))
        return s

    def getHyperslabSelection(self, dsetshape, start, stop, step):
        """
        Get slices given lists of start, stop, step values
        """
        log = logging.getLogger("h5serv")
        rank = len(dsetshape)
        if start:
            if type(start) is not list:
                start = [start]
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
                stop = [stop]
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
                step = [step]
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

    def get(self):
        log = logging.getLogger("h5serv")
        log.info(
            'ValueHandler.get host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        request_content_type = self.getAcceptType()
        response_content_type = "json"
        log.info("contenttype:" + request_content_type)
        self.get_current_user()

        reqUuid = self.getRequestId()
        domain = self.getDomain()
        filePath = self.getFilePath(domain)

        response = {}
        hrefs = []
        rootUUID = None
        item = None
        item_shape = None
        rank = None
        item_type = None
        values = None
        slices = []
        query_selection = self.get_query_argument("query", default=None)
        if query_selection:
            log.info("query: " + query_selection)

        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(reqUuid, self.userid)
                self.verifyAcl(acl, 'read')  # throws exception is unauthorized
                item = db.getDatasetItemByUuid(reqUuid)
                item_type = item['type']
                
                if item_type['class'] == 'H5T_OPAQUE':
                    # TODO - support for returning OPAQUE data...
                    msg = "Not Implemented: GET OPAQUE data not supported"
                    log.info(msg)
                    raise HTTPError(501, reason=msg)  # Not implemented
                item_shape = item['shape']
                if item_shape['class'] == 'H5S_NULL':
                    pass   # don't return a value
                elif item_shape['class'] == 'H5S_SCALAR':
                    if query_selection:
                        msg = "Bad Request: query selection not valid with scalar dataset"
                        log.info(msg)
                        raise HTTPError(400, reason=msg)
                    values = db.getDatasetValuesByUuid(reqUuid, Ellipsis)
                elif item_shape['class'] == 'H5S_SIMPLE':
                    dims = item_shape['dims']
                    rank = len(dims)
                    nelements = 1
                    for dim in range(rank):
                        dim_slice = self.getSliceQueryParam(dim, dims[dim])
                        nelements *= (dim_slice.stop - dim_slice.start)
                        slices.append(dim_slice)
                    if not query_selection:
                        if request_content_type == "binary":
                            log.info("nelements:" + str(nelements))
                            itemSize = h5json.getItemSize(item_type)
                            if itemSize != "H5T_VARIABLE" and nelements > 1:
                                response_content_type = "binary"
                       
                        log.info("response_content_type: " + response_content_type)
                        values = db.getDatasetValuesByUuid(
                            reqUuid, tuple(slices), format=response_content_type) 
                        log.info("values type: " + str(type(values)))       
                         
                else:
                    msg = "Internal Server Error: unexpected shape class: " + shape['class']
                    log.error(msg)
                    raise HTTPError(500, reason=msg)

                rootUUID = db.getUUIDByPath('/')
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        if query_selection:
            if item_type['class'] != 'H5T_COMPOUND':
                msg = "Bad Request: query selection is only supported for compound types"
                log.info(msg)
                raise HTTPError(400, reason=msg)
            if rank != 1:
                msg = "Bad Request: query selection is only supported for "
                msg += "one dimensional datasets"
                log.info(msg)
                raise HTTPError(400, reason=msg)
            if 'alias' not in item or len(item['alias']) == 0:
                msg = "Bad Request: query selection is not valid for "
                msg += "anonymous datasets"
                log.info(msg)
                raise HTTPError(400, reason=msg)

            dims = item_shape['dims']
            start = 0
            stop = dims[0]
            step = 1
            limit = self.get_query_argument("Limit", default=None)
            if limit:
                try:
                    limit = int(limit)  # convert to int
                except ValueError as e:
                    msg = "Query error, invalid Limit: " + e.message
                    log.info(msg)
                    raise HTTPError(400, msg)
            if slices:
                start = slices[0].start
                stop = slices[0].stop
                step = slices[0].step
            try:
                #from querydb import Querydb
                with Querydb(filePath, app_logger=log) as db:
                    path = item['alias'][0]
                    rsp = db.doQuery(
                        item_type, path, query_selection,
                        start=start, stop=stop, step=step, limit=limit)
                    values = rsp['values']
                
                    response['index'] = rsp['indexes']
            except NameError as e:
                
                msg = "Query error"
                try: 
                    msg += ": " + e.message
                except AttributeError:
                    pass  # no message attribute
                log.info(msg)
                raise HTTPError(400, msg)

        # got everything we need, put together the response
        
        if response_content_type == "binary":
            # binary transfer, just write the bytes and return
            log.info("writing binary stream")
            self.set_header('Content-Type', 'application/octet-stream')
            self.write(values)
            return
            
        if request_content_type == "binary":
            #unable to return binary data
            log.info("requested binary response, but returning JSON instead")
            
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=''):
            hostQuery = "?host=" + self.get_query_argument("host")
        selfQuery = ''
        if self.get_query_argument("select", default=''):
            selfQuery = '?select=' + self.get_query_argument("select")
        if self.get_query_argument("query", default=''):
            if selfQuery:
                selfQuery += '&'
            else:
                selfQuery += '?'
            selfQuery += 'query=' + self.get_query_argument(
                "select", default='')
        if self.get_query_argument("host", default=''):
            if selfQuery:
                selfQuery += '&'
            else:
                selfQuery += '?'
            selfQuery += 'host=' + self.get_query_argument("host", default='')

        if values is not None:
            response['value'] = values
        else:
            response['value'] = None

        hrefs.append({
            'rel': 'self',
            'href': href + 'datasets/' + reqUuid + '/value' + selfQuery
        })
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID + hostQuery})
        hrefs.append({
            'rel': 'owner', 'href': href + 'datasets/' + reqUuid + hostQuery})
        hrefs.append({
            'rel': 'home', 'href': href + hostQuery})
        response['hrefs'] = hrefs

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))

    def post(self):
        log = logging.getLogger("h5serv")
        log.info(
            'ValueHandler.post host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        reqUuid = self.getRequestId()
        domain = self.getDomain()
        filePath = self.getFilePath(domain)

        body = None
        try:
            body = json_decode(self.request.body)
        except ValueError as e:
            msg = "JSON Parser Error: " + e.message
            log.info(msg)
            raise HTTPError(400, reason=msg)

        if "points" not in body:
            msg = "Bad Request: value post request without points in body"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        points = body['points']
        if type(points) != list:
            msg = "Bad Request: expecting list of points"
            log.info(msg)
            raise HTTPError(400, reason=msg)

        response = {}
        hrefs = []
        rootUUID = None
        item = None
        values = None

        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(reqUuid, self.userid)
                self.verifyAcl(acl, 'read')  # throws exception is unauthorized
                item = db.getDatasetItemByUuid(reqUuid)
                shape = item['shape']
                if shape['class'] == 'H5S_SCALAR':
                    msg = "Bad Request: point selection is not supported on scalar datasets"
                    log.info(msg)
                    raise HTTPError(400, reason=msg)
                if shape['class'] == 'H5S_NULL':
                    msg = "Bad Request: point selection is not supported on Null Space datasets"
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

        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        # got everything we need, put together the response
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        response['value'] = values

        hrefs.append({
            'rel': 'self',
            'href': href + 'datasets/' + reqUuid + '/value' + hostQuery
        })
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID + hostQuery})
        hrefs.append({
            'rel': 'owner', 'href': href + 'datasets/' + reqUuid + hostQuery})
        hrefs.append({'rel': 'home',  'href': href + hostQuery})

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))

    def put(self):
        log = logging.getLogger("h5serv")
        log.info(
            'ValueHandler.put host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        
        self.get_current_user()

        reqUuid = self.getRequestId()
        domain = self.getDomain()
        filePath = self.getFilePath(domain)
        points = None
        start = None
        stop = None
        step = None
        body = None
        format = "json"
        data = None
        
        try:
            body = json_decode(self.request.body)
        except ValueError as e:
            try:
                msg = "JSON Parser Error: " + e.message
            except AttributeError:
                msg = "JSON Parser Error"
            log.info(msg)
            raise HTTPError(400, reason=msg)

        if "value" in body:
            data = body["value"]
            format = "json"
        elif "value_base64" in body:
            base64_data = body["value_base64"]
            base64_data = base64_data.encode("ascii")
            data = base64.b64decode(base64_data)
            format = "binary"
            
        else:
            msg = "Bad Request: Value not specified"
            log.info(msg)
            raise HTTPError(400, reason=msg)  # missing data     

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
            if len(points) > len(data):
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
         

        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(reqUuid, self.userid)
                self.verifyAcl(acl, 'update')  # throws exception is unauthorized
                item = db.getDatasetItemByUuid(reqUuid)
                item_type = item['type']
               
                dims = None
                if 'shape' not in item:
                    msg = "Unexpected error, shape information not found"
                    log.info(msg)
                    raise HTTPError(500, reason=msg)
                datashape = item['shape']
                if datashape['class'] == 'H5S_NULL':
                    msg = "Bad Request: PUT value can't be used with Null Space datasets"
                    log.info(msg)
                    raise HTTPError(400, reason=msg)  # missing data
                    
                if format == "binary":
                    item_size = h5json.getItemSize(item_type)
                    if item_size == "H5T_VARIABLE":
                        msg = "binary data cannot be used with variable length types"
                        log.info(msg)
                        raise HTTPError(400, reason=msg)  # need to use json
                         
                if datashape['class'] == 'H5S_SIMPLE':
                    dims = datashape['dims']
                elif datashape['class'] == 'H5S_SCALAR':
                    if start is not None or stop is not None or step is not None:
                        msg = "Bad Request: start/stop/step option can't be used with Scalar Space datasets"
                        log.info(msg)
                        raise HTTPError(400, reason=msg)  # missing data           
                    elif points:
                        msg = "Bad Request: Point selection can't be used with scalar datasets"
                        log.info(msg)
                        raise HTTPError(400, reason=msg)  # missing data
                  
                if points is not None:
                    # write point selection
                    db.setDatasetValuesByPointSelection(reqUuid, data, points, format=format)
                     
                else:
                    slices = None
                    if dims is not None:          
                        slices = self.getHyperslabSelection(
                            dims, start, stop, step)
                    # todo - check that the types are compatible
                    db.setDatasetValuesByUuid(reqUuid, data, slices, format=format)
                     
                    
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        log.info("value put succeeded")


class AttributeHandler(BaseHandler):

    # convert embedded list (list of lists) to tuples
    def convertToTuple(self, data):
        if type(data) == list or type(data) == tuple:
            sublist = []
            for e in data:
                sublist.append(self.convertToTuple(e))
            return tuple(sublist)
        else:
            return data

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
                # strip off any query param
                npos = uri.rfind('?')
                if npos > 0:
                    uri = uri[:npos]
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
        log.info(
            'AttributeHandler.get host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        reqUuid = self.getRequestId()
        domain = self.getDomain()
        col_name = self.getRequestCollectionName()
        attr_name = self.getRequestName()
        filePath = self.getFilePath(domain)

        response = {}
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
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(reqUuid, self.userid)
                self.verifyAcl(acl, 'read')  # throws exception is unauthorized
                if attr_name is not None:
                    item = db.getAttributeItem(col_name, reqUuid, attr_name)
                    items.append(item)
                else:
                    # get all attributes (but without data)
                    items = db.getAttributeItems(col_name, reqUuid, marker, limit)

        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        # got everything we need, put together the response
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        root_href = href + 'groups/' + rootUUID
        owner_href = href + col_name + '/' + reqUuid
        self_href = owner_href + '/attributes'
        if attr_name is not None:
            self_href += '/' + url_escape(attr_name)

        responseItems = []
        for item in items:
            responseItem = {}
            responseItem['name'] = item['name']
            typeItem = item['type']
            responseItem['type'] = h5json.getTypeResponse(typeItem)
            responseItem['shape'] = item['shape']
            responseItem['created'] = unixTimeToUTC(item['ctime'])
            responseItem['lastModified'] = unixTimeToUTC(item['mtime'])
            if not attr_name or typeItem['class'] == 'H5T_OPAQUE':
                pass  # TODO - send data for H5T_OPAQUE's
            elif 'value' in item:
                responseItem['value'] = item['value']
            else:
                responseItem['value'] = None
            if attr_name is None:
                # add an href to the attribute
                responseItem['href'] = self_href + '/' + url_escape(item['name']) + hostQuery

            responseItems.append(responseItem)

        hrefs.append({'rel': 'self', 'href': self_href + hostQuery})
        hrefs.append({'rel': 'owner', 'href': owner_href + hostQuery})
        hrefs.append({'rel': 'root', 'href': root_href + hostQuery})
        hrefs.append({'rel': 'home', 'href': href + hostQuery})

        if attr_name is None:
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
        log.info(
            'AttributeHandler.put host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        domain = self.getDomain()
        col_name = self.getRequestCollectionName()
        reqUuid = self.getRequestId()
        attr_name = self.getRequestName()
        if attr_name is None:
            msg = "Bad Request: attribute name not supplied"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        filePath = self.getFilePath(domain)

        body = None
        try:
            body = json_decode(self.request.body)
        except ValueError as e:
            msg = "JSON Parser Error"
            try:
                msg += ": " + e.message
            except AttributeError:
                pass # no message property
          
            log.info(msg)
            raise HTTPError(400, reason=msg)

        if "type" not in body:
            log.info("Type not supplied")
            raise HTTPError(400)  # missing type

        dims = ()  # default as empty tuple (will create a scalar attribute)
        if "shape" in body:
            shape = body["shape"]
            if type(shape) == int:
                dims = [shape]
            elif type(shape) == list or type(shape) == tuple:
                dims = shape  # can use as is
            elif type(shape) in (str, unicode) and shape == 'H5S_NULL':
                dims = None
            else:
                msg = "Bad Request: shape is invalid!"
                log.info(msg)
                raise HTTPError(400, reason=msg)
        datatype = body["type"]

        # validate shape
        if dims:
            for extent in dims:
                if type(extent) != int:
                    msg = "Bad Request: invalid shape type"
                    log.info(msg)
                    raise HTTPError(400, reason=msg)
                if extent < 0:
                    msg = "Bad Request: invalid shape (negative extent)"
                    log.info(msg)
                    raise HTTPError(400, reason=msg)

        # convert list values to tuples (otherwise h5py is not happy)
        data = None

        if dims is not None:
            if "value" not in body:
                msg = "Bad Request: value not specified"
                log.info(msg)
                raise HTTPError(400, reason=msg)  # missing value
            value = body["value"]

            data = self.convertToTuple(value)

        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(reqUuid, self.userid)
                self.verifyAcl(acl, 'create')  # throws exception is unauthorized
                db.createAttribute(
                    col_name, reqUuid, attr_name, dims, datatype, data)
                rootUUID = db.getUUIDByPath('/')

        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        response = {}

        # got everything we need, put together the response
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        root_href = href + 'groups/' + rootUUID
        owner_href = href + col_name + '/' + reqUuid
        self_href = owner_href + '/attributes'
        if attr_name is not None:
            self_href += '/' + attr_name

        hrefs = []
        hrefs.append({'rel': 'self',   'href': self_href + hostQuery})
        hrefs.append({'rel': 'owner',  'href': owner_href + hostQuery})
        hrefs.append({'rel': 'root',   'href': root_href + hostQuery})
        response['hrefs'] = hrefs

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        self.set_status(201)  # resource created

    def delete(self):
        log = logging.getLogger("h5serv")
        log.info('AttributeHandler.delete ' + self.request.host)
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        obj_uuid = self.getRequestId()
        domain = self.getDomain()
        col_name = self.getRequestCollectionName()
        attr_name = self.getRequestName()
        if attr_name is None:
            msg = "Bad Request: attribute name not specified"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        filePath = self.getFilePath(domain)
        self.isWritable(filePath)

        response = {}
        hrefs = []
        rootUUID = None

        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(obj_uuid, self.userid)
                self.verifyAcl(acl, 'delete')  # throws exception is unauthorized
                db.deleteAttribute(col_name, obj_uuid, attr_name)

        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        # got everything we need, put together the response
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        root_href = href + 'groups/' + rootUUID
        owner_href = href + col_name + '/' + obj_uuid
        self_href = owner_href + '/attributes'

        hrefs.append({'rel': 'self', 'href': self_href + hostQuery})
        hrefs.append({'rel': 'owner', 'href': owner_href + hostQuery})
        hrefs.append({'rel': 'root', 'href': root_href + hostQuery})
        hrefs.append({'rel': 'home', 'href': href + hostQuery})
        response['hrefs'] = hrefs

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))

        log.info("Attribute delete succeeded")


class GroupHandler(BaseHandler):

    def get(self):
        log = logging.getLogger("h5serv")
        log.info(
            'GroupHandler.get host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        reqUuid = self.getRequestId()

        domain = self.getDomain()
        filePath = self.getFilePath(domain)

        response = {}

        hrefs = []
        rootUUID = None
        item = None

        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(reqUuid, self.userid)
                self.verifyAcl(acl, 'read')  # throws exception is unauthorized
                item = db.getGroupItemByUuid(reqUuid)

        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        # got everything we need, put together the response
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({
            'rel': 'self',
            'href': href + 'groups/' + reqUuid + hostQuery
        })
        hrefs.append({
            'rel': 'links',
            'href': href + 'groups/' + reqUuid + '/links' + hostQuery
        })
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID + hostQuery})
        hrefs.append({
            'rel': 'home', 'href': href + hostQuery})
        hrefs.append({
            'rel': 'attributes',
            'href': href + 'groups/' + reqUuid + '/attributes' + hostQuery
        })
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
        self.get_current_user()

        req_uuid = self.getRequestId()
        domain = self.getDomain()
        filePath = self.getFilePath(domain)
        self.isWritable(filePath)
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(req_uuid, self.userid)
                self.verifyAcl(acl, 'delete')  # throws exception is unauthorized
                db.deleteObjectByUuid('group', req_uuid)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        response = {}
        hrefs = []

        # write the response
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({'rel': 'self', 'href': href + 'groups' + hostQuery})
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID + hostQuery})
        hrefs.append({'rel': 'home', 'href': href + hostQuery})
        response['hrefs'] = hrefs

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))


class GroupCollectionHandler(BaseHandler):

    def get(self):
        log = logging.getLogger("h5serv")
        log.info(
            'GroupCollectionHandler.get host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        domain = self.getDomain()
        filePath = self.getFilePath(domain)
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

        response = {}

        items = None
        hrefs = []

        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(rootUUID, self.userid)
                self.verifyAcl(acl, 'read')  # throws exception is unauthorized
                items = db.getCollection("groups", marker, limit)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        # write the response
        response['groups'] = items
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({
            'rel': 'self', 'href': href + 'groups' + hostQuery})
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID + hostQuery})
        hrefs.append({
            'rel': 'home', 'href': href + hostQuery})
        response['hrefs'] = hrefs

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))

    def post(self):
        log = logging.getLogger("h5serv")
        log.info(
            'GroupHandlerCollection.post host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        if self.request.uri != '/groups':
            msg = "Method Not Allowed: bad group post request"
            log.info(msg)
            raise HTTPError(405, reason=msg)  # Method not allowed
        self.get_current_user()

        parent_group_uuid = None
        link_name = None

        body = {}
        if self.request.body:
            try:
                body = json_decode(self.request.body)
            except ValueError as e:
                msg = "JSON Parser Error: " + e.message
                log.info(msg)
                raise HTTPError(400, reason=msg)

        if "link" in body:
            link_options = body["link"]
            if "id" not in link_options or "name" not in link_options:
                msg = "Bad Request: missing link parameter"
                log.info(msg)
                raise HTTPError(400, reason=msg)
            parent_group_uuid = link_options["id"]
            link_name = link_options["name"]
            log.info(
                "add link to: " + parent_group_uuid + " with name: " + link_name)

        domain = self.getDomain()
        filePath = self.getFilePath(domain)
        self.isWritable(filePath)

        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                current_user_acl = db.getAcl(rootUUID, self.userid)

                self.verifyAcl(current_user_acl, 'create')  # throws exception is unauthorized
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
        response = {}
        hrefs = []
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({
            'rel': 'self', 'href': href + 'groups/' + grpUUID + hostQuery})
        hrefs.append({
            'rel': 'links',
            'href': href + 'groups/' + grpUUID + '/links' + hostQuery
        })
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID + hostQuery})
        hrefs.append({
            'rel': 'home', 'href': href + hostQuery})
        hrefs.append({
            'rel': 'attributes',
            'href': href + 'groups/' + grpUUID + '/attributes' + hostQuery
        })
        response['id'] = grpUUID
        response['created'] = unixTimeToUTC(item['ctime'])
        response['lastModified'] = unixTimeToUTC(item['mtime'])
        response['attributeCount'] = item['attributeCount']
        response['linkCount'] = item['linkCount']
        response['hrefs'] = hrefs

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        self.set_status(201)  # resource created


class DatasetCollectionHandler(BaseHandler):

    def get(self):
        log = logging.getLogger("h5serv")
        log.info(
            'DatasetCollectionHandler.get host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        domain = self.getDomain()
        filePath = self.getFilePath(domain)

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

        response = {}
        hrefs = []
        rootUUID = None

        items = None

        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(rootUUID, self.userid)
                self.verifyAcl(acl, 'read')  # throws exception is unauthorized
                items = db.getCollection("datasets", marker, limit)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        # write the response
        response['datasets'] = items
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({'rel': 'self', 'href': href + 'datasets' + hostQuery})
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID + hostQuery})
        hrefs.append({'rel': 'home', 'href': href + hostQuery})
        response['hrefs'] = hrefs

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))

    def post(self):
        log = logging.getLogger("h5serv")
        log.info(
            'DatasetHandler.post host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        if self.request.uri != '/datasets':
            msg = "Method not Allowed: invalid datasets post request"
            log.info(msg)
            raise HTTPError(405, reason=msg)  # Method not allowed

        domain = self.getDomain()
        filePath = self.getFilePath(domain)
        self.isWritable(filePath)
        dims = None
        group_uuid = None
        link_name = None

        body = {}
        if self.request.body:
            try:
                body = json_decode(self.request.body)
            except ValueError as e:
                msg = "JSON Parser Error: " + e.message
                log.info(msg)
                raise HTTPError(400, reason=msg)
                

        if "type" not in body:
            msg = "Bad Request: Type not specified"
            log.info(msg)
            raise HTTPError(400, reason=msg)  # missing type

        if "shape" in body:
            shape = body["shape"]
            if type(shape) == int:
                dims = [shape]
            elif type(shape) == list or type(shape) == tuple:
                dims = shape  # can use as is
            elif type(shape) in (str, unicode) and shape == 'H5S_NULL':
                dims = None
            else:
                msg = "Bad Request: shape is invalid"
                log.info(msg)
                raise HTTPError(400, reason=msg)
        else:
            dims = ()  # empty tuple

        if "link" in body:
            link_options = body["link"]
            if "id" not in link_options or "name" not in link_options:
                msg = "Bad Request: No 'name' or 'id' not specified"
                log.info(msg)
                raise HTTPError(400, reason=msg)

            group_uuid = link_options["id"]
            link_name = link_options["name"]
            log.info("add link to: " + group_uuid + " with name: " + link_name)

        datatype = body["type"]

        maxdims = None
        if "maxdims" in body:
            maxdims = body["maxdims"]
            if type(maxdims) == int:
                dim1 = maxdims
                maxdims = [dim1]
            elif type(maxdims) == list or type(maxdims) == tuple:
                pass  # can use as is
            else:
                msg = "Bad Request: maxdims is invalid"
                log.info(msg)
                raise HTTPError(400, reason=msg)

        # validate shape
        if dims:
            for extent in dims:
                if type(extent) != int:
                    msg = "Bad Request: Invalid shape type"
                    log.info(msg)
                    raise HTTPError(400, reason=msg)
                if extent < 0:
                    msg = "Bad Request: shape dimension is negative"
                    log.info("msg")
                    raise HTTPError(400, reason=msg)

        if maxdims:
            if dims is None:
                # can't use maxdims with null_space dataset
                msg = "Bad Request: maxdims not valid for H5S_NULL dataspace"
                log.info(msg)
                raise HTTPError(400, reason=msg)

            if len(maxdims) != len(dims):
                msg = "Bad Request: maxdims array length must equal shape array length"
                log.info(msg)
                raise HTTPError(400, reason=msg)
            for i in range(len(dims)):
                maxextent = maxdims[i]
                if maxextent != 0 and maxextent < dims[i]:
                    msg = "Bad Request: maxdims extent can't be smaller than shape extent"
                    log.info(msg)
                    raise HTTPError(400, reason=msg)
                if maxextent == 0:
                    maxdims[i] = None  # this indicates unlimited

        creationProps = None
        if "creationProperties" in body:
            creationProps = body["creationProperties"]
        item = None
        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(rootUUID, self.userid)
                self.verifyAcl(acl, 'create')  # throws exception is unauthorized
                # verify the link perm as well
                if group_uuid and group_uuid != rootUUID:
                    acl = db.getAcl(group_uuid, self.userid)
                    self.verifyAcl(acl, 'create')  # throws exception is unauthorized

                item = db.createDataset(datatype, dims, maxdims, creation_props=creationProps)
                if group_uuid:
                    # link the new dataset
                    db.linkObject(group_uuid, item['id'], link_name)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        response = {}

        # got everything we need, put together the response
        hrefs = []
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({
            'rel': 'self',
            'href': href + 'datasets/' + item['id'] + hostQuery
        })
        hrefs.append({
            'rel': 'root',
            'href': href + 'groups/' + rootUUID + hostQuery
        })
        hrefs.append({
            'rel': 'attributes',
            'href': href + 'datasets/' + item['id'] + '/attributes' + hostQuery
        })
        hrefs.append({
            'rel': 'value',
            'href': href + 'datasets/' + item['id'] + '/value' + hostQuery})
        response['id'] = item['id']
        response['attributeCount'] = item['attributeCount']
        response['hrefs'] = hrefs
        response['created'] = unixTimeToUTC(item['ctime'])
        response['lastModified'] = unixTimeToUTC(item['mtime'])

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        self.set_status(201)  # resource created


class TypeCollectionHandler(BaseHandler):
    def get(self):
        log = logging.getLogger("h5serv")
        log.info(
            'TypeCollectionHandler.get host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        domain = self.getDomain()
        filePath = self.getFilePath(domain)

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

        response = {}
        hrefs = []
        rootUUID = None

        items = None
        try:
            with Hdf5db(filePath) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(rootUUID, self.userid)
                self.verifyAcl(acl, 'read')  # throws exception is unauthorized
                items = db.getCollection("datatypes", marker, limit)
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        # write the response
        response['datatypes'] = items

        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({
            'rel': 'self',
            'href': href + 'datatypes' + hostQuery
        })
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID + hostQuery})
        hrefs.append({'rel': 'home', 'href': href + hostQuery})
        response['hrefs'] = hrefs

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))

    def post(self):
        log = logging.getLogger("h5serv")
        log.info(
            'TypeHandler.post host=[' + self.request.host +
            '] uri=[' + self.request.uri + ']')
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        if self.request.uri != '/datatypes':
            msg = "Method not Allowed: invalid URI"
            log.info(msg)
            raise HTTPError(405, reason=msg)  # Method not allowed

        domain = self.getDomain()
        filePath = self.getFilePath(domain)
        self.isWritable(filePath)

        body = None
        try:
            body = json_decode(self.request.body)
        except ValueError as e:
            msg = "JSON Parser Error: " + e.message
            log.info(msg)
            raise HTTPError(400, reason=msg)

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
            log.info(
                "add link to: " + parent_group_uuid + " with name: " + link_name)

        datatype = body["type"]

        item = None
        rootUUID = None

        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(rootUUID, self.userid)
                self.verifyAcl(acl, 'create')  # throws exception is unauthorized
                item = db.createCommittedType(datatype)
                # if link info is provided, link the new group
                if parent_group_uuid:
                    # link the new dataset
                    db.linkObject(parent_group_uuid, item['id'], link_name)

        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        response = {}

        # got everything we need, put together the response
        hrefs = []
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({
            'rel': 'self',
            'href': href + 'datatypes/' + item['id'] + hostQuery
        })
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID})
        hrefs.append({
            'rel': 'attributes',
            'href': href + 'datatypes/' + item['id'] + '/attributes' + hostQuery
        })
        response['id'] = item['id']
        response['attributeCount'] = 0
        response['hrefs'] = hrefs
        response['created'] = unixTimeToUTC(item['ctime'])
        response['lastModified'] = unixTimeToUTC(item['mtime'])

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        self.set_status(201)  # resource created


class RootHandler(BaseHandler):
    def getSubgroupId(self, db, group_uuid, link_name):
        """
        Helper method - get group uuid of hardlink, or None if no link
        """
        subgroup_uuid = None
        try:
            item = db.getLinkItemByUuid(group_uuid, link_name)
            if item['class'] != 'H5L_TYPE_HARD':
                return None
            if item['collection'] != 'groups':
                return None
            subgroup_uuid = item['id']
        except IOError:
            # link_name doesn't exist, return None
            pass

        return subgroup_uuid

    def addTocEntry(self, domain, filePath, validateOnly=False):
        """
        Helper method - update TOC when a domain is created
          If validateOnly is true, then the acl is checked to verify that create is
          enabled, but doesn't update the .toc
        """
        log = logging.getLogger("h5serv")
        hdf5_ext = config.get('hdf5_ext')
        dataPath = config.get('datapath')
        log.info("addTocEntry - domain: " + domain + " filePath: " + filePath)
        if not filePath.startswith(dataPath):
            log.error("unexpected filepath: " + filePath)
            raise HTTPError(500)
        filePath = fileUtil.getUserFilePath(filePath)   
        tocFile = fileUtil.getTocFilePathForDomain(domain)
        log.info("addTocEntry, filePath: " + filePath)
        acl = None

        try:
            with Hdf5db(tocFile, app_logger=log) as db:
                group_uuid = db.getUUIDByPath('/')
                pathNames = filePath.split('/')
                for linkName in pathNames:
                    if not linkName:
                        continue
                    log.info("linkName: " + linkName)
                    if linkName.endswith(hdf5_ext):
                        linkName = linkName[:-(len(hdf5_ext))]
                        acl = db.getAcl(group_uuid, self.userid)
                        self.verifyAcl(acl, 'create')  # throws exception is unauthorized
                        db.createExternalLink(group_uuid, domain, '/', linkName)
                    else:
                        subgroup_uuid = self.getSubgroupId(db, group_uuid, linkName)
                        if subgroup_uuid is None:
                            acl = db.getAcl(group_uuid, self.userid)
                            self.verifyAcl(acl, 'create')  # throws exception is unauthorized
                            # create subgroup and link to parent group
                            subgroup_uuid = db.createGroup()
                            # link the new group
                            db.linkObject(group_uuid, subgroup_uuid, linkName)
                        group_uuid = subgroup_uuid

        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            raise e

    """
    Helper method - update TOC when a domain is deleted
    """
    def removeTocEntry(self, domain, filePath):
        log = logging.getLogger("h5serv")
        hdf5_ext = config.get('hdf5_ext')
        dataPath = config.get('datapath')

        if not filePath.startswith(dataPath):
            log.error("unexpected filepath: " + filePath)
            raise HTTPError(500)
        filePath = fileUtil.getUserFilePath(filePath)   
        tocFile = fileUtil.getTocFilePathForDomain(domain)
        log.info(
            "removeTocEntry - domain: " + domain + " filePath: " + filePath + " tocfile: " + tocFile)
        pathNames = filePath.split('/')
        log.info("pathNames: " + str(pathNames))

        try:
            with Hdf5db(tocFile, app_logger=log) as db:
                group_uuid = db.getUUIDByPath('/')
                log.info("group_uuid:" + group_uuid)
                           
                for linkName in pathNames:
                    if not linkName:
                        continue
                    log.info("linkName:" + linkName)
                    if linkName.endswith(hdf5_ext):
                        linkName = linkName[:-(len(hdf5_ext))]
                        log.info("unklink " + group_uuid + ", " + linkName)
                        db.unlinkItem(group_uuid, linkName)
                    else:
                        subgroup_uuid = self.getSubgroupId(
                            db, group_uuid, linkName)
                        if subgroup_uuid is None:
                            msg = "Didn't find expected subgroup: " + group_uuid
                            log.error(msg)
                            raise HTTPError(500, reason=msg)
                        group_uuid = subgroup_uuid

        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            raise e

    def getRootResponse(self, filePath):
        log = logging.getLogger("h5serv")
        acl = None
        # used by GET / and PUT /

        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(rootUUID, self.userid)

        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)
        domain = self.getDomain()

        self.verifyAcl(acl, 'read')  # throws exception is unauthorized

        # generate response
        hrefs = []
        href = self.request.protocol + '://' + self.request.host + '/'
        hostQuery = ''
        if self.get_query_argument("host", default=None):
            hostQuery = "?host=" + self.get_query_argument("host")
        hrefs.append({
            'rel': 'self', 'href': href + hostQuery})
        hrefs.append({
            'rel': 'database', 'href': href + 'datasets' + hostQuery})
        hrefs.append({'rel': 'groupbase', 'href': href + 'groups' + hostQuery})
        hrefs.append({
            'rel': 'typebase', 'href': href + 'datatypes' + hostQuery})
        hrefs.append({
            'rel': 'root', 'href': href + 'groups/' + rootUUID + hostQuery})

        response = {}
        response['created'] = unixTimeToUTC(op.getctime(filePath))
        response['lastModified'] = unixTimeToUTC(op.getmtime(filePath))
        response['root'] = rootUUID
        response['hrefs'] = hrefs

        return response

    def get(self):
        log = logging.getLogger("h5serv")
        log.info('RootHandler.get ' + self.request.host)
        log.info('remote_ip: ' + self.request.remote_ip)
        self.current_user = self.get_current_user()
        domain = self.getDomain()
        filePath = self.getFilePath(domain)
        try:
            response = self.getRootResponse(filePath)
        except HTTPError as e:
            if e.status_code == 401:
                # no user provied, just return 401 response
                return
            raise e  # re-throw the exception

        root_uuid = response['root']

        filePath = self.getFilePath(domain)
        log.info("filepath: " + filePath)

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))

    def put(self):
        log = logging.getLogger("h5serv")
        log.info('RootHandler.put ' + self.request.host)
        log.info('remote_ip: ' + self.request.remote_ip)
        self.current_user = self.get_current_user()

        domain = self.getDomain()
        filePath = None
        log.info("domain: " + domain)
        
        filePath = self.getFilePath(domain, checkExists=False)
        
        if filePath is not None and fileUtil.isFile(filePath):
            # the file already exists
            msg = "Conflict: resource exists: " + filePath
            log.info(msg)
            raise HTTPError(409, reason=msg)  # Conflict - is this the correct code?
             
        
        if filePath is not None and self.isTocFilePath(filePath):
            msg = "Forbidden: invalid resource"
            log.info(msg)
            raise HTTPError(403, reason=msg)  # Forbidden - TOC file
        
        if filePath is None:
            msg = "domain not valid"
            log.info(msg)
            raise HTTPError(400, reason=msg)
        
        log.info("FilePath: " + filePath)     
        # create directories as needed
        fileUtil.makeDirs(op.dirname(filePath))
        log.info("creating file: [" + filePath + "]")

        try:
            Hdf5db.createHDF5File(filePath)
        except IOError as e:
            log.info(
                "IOError creating new HDF5 file: " + str(e.errno) + " " + e.strerror)
            raise HTTPError(
                500, "Unexpected error: unable to create collection")

        response = self.getRootResponse(filePath)

        self.addTocEntry(domain, filePath)

        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(response))
        self.set_status(201)  # resource created

    def delete(self):
        log = logging.getLogger("h5serv")
        log.info('RootHandler.delete ' + self.request.host)
        log.info('remote_ip: ' + self.request.remote_ip)
        self.get_current_user()

        domain = self.getDomain()
        filePath = self.getFilePath(domain)
        log.info("delete filePath: " + filePath)
        self.isWritable(filePath)

        if not op.isfile(filePath):
            # file not there
            msg = "Not found: resource does not exist"
            log.info(msg)
            raise HTTPError(404, reason=msg)  # Not found

        # don't use os.access since it will always return OK if uid is root
        if not os.stat(filePath).st_mode & 0o200:
            # file is read-only
            msg = "Forbidden: Resource is read-only"
            log.info(msg)
            raise HTTPError(403, reason=msg)  # Forbidden

        if self.isTocFilePath(filePath):
            msg = "Forbidden: Resource is read-only"
            log.info(msg)
            raise HTTPError(403, reason=msg)  # Forbidden - TOC file

        try:
            with Hdf5db(filePath, app_logger=log) as db:
                rootUUID = db.getUUIDByPath('/')
                acl = db.getAcl(rootUUID, self.userid)
                self.verifyAcl(acl, 'delete')  # throws exception is unauthorized
        except IOError as e:
            log.info("IOError: " + str(e.errno) + " " + e.strerror)
            status = errNoToHttpStatus(e.errno)
            raise HTTPError(status, reason=e.strerror)

        try:
            self.removeTocEntry(domain, filePath)
        except IOError as ioe:
            # This exception may happen if the file has been imported directly
            # after toc creation
            log.warn("IOError removing toc entry")

        try:
            os.remove(filePath)
        except IOError as ioe:
            log.info(
                "IOError deleting HDF5 file: " + str(ioe.errno) + " " + ioe.strerror)
            raise HTTPError(
                500, "Unexpected error: unable to delete collection")


class InfoHandler(RequestHandler):

    def get(self):
        log = logging.getLogger("h5serv")
        log.info('InfoHandler.get ' + self.request.host)
        log.info('remote_ip: ' + self.request.remote_ip)

        greeting = "Welcome to h5serv!"
        about = "h5serv is a webservice for HDF5 data"
        doc_href = "http://h5serv.readthedocs.org"
        h5serv_version = "0.1"
        response = Hdf5db.getVersionInfo()
        response['name'] = "h5serv"
        response['greeting'] = greeting
        response['about'] = about
        response['documentation'] = doc_href
        response['h5serv_version'] = h5serv_version

        accept_type = ''
        if 'accept' in self.request.headers:
            accept = self.request.headers['accept']
            # just extract the first type and not worry about q values for now...
            accept_values = accept.split(',')
            accept_types = accept_values[0].split(';')
            accept_type = accept_types[0]
            # print 'accept_type:', accept_type
        if accept_type == 'text/html':
            self.set_header('Content-Type', 'text/html')
            htmlText = "<html><body><h1>" + response['greeting'] + "</h1>"
            htmlText += "<h2>" + response['about'] + "</h2>"
            htmlText += "<h2>Documentation: <a href=" + response['documentation'] + "> h5serv documentation </a></h2>"
            htmlText += "<h2>server version: " + response['h5serv_version'] + "</h2>"
            htmlText += "<h2>h5py version: " + response['h5py_version'] + "</h2>"
            htmlText += "<h2>hdf5 version: " + response['hdf5_version'] + "</h2>"
            htmlText += "</body></html>"
            self.write(htmlText)
        else:
            self.set_header('Content-Type', 'application/json')
            self.write(json_encode(response))


def sig_handler(sig, frame):
    log = logging.getLogger("h5serv")
    log.warning('Caught signal: %s', sig)
    IOLoop.instance().add_callback(shutdown)


def shutdown():
    log = logging.getLogger("h5serv")
    MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 2
    log.info('Stopping http server')

    log.info(
        'Will shutdown in %s seconds ...', MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
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
    static_url = config.get('static_url')
    static_path = config.get('static_path')
    settings = {
        # "static_path": os.path.join(os.path.dirname(__file__), 'static'),
        "static_path": 'static',
        # "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        # "login_url": "/login",
        # "xsrf_cookies": True,
        "debug": config.get('debug')
    }

    favicon_path = "favicon.ico"
    print("dirname path:", os.path.dirname(__file__))
    print("favicon_path:", favicon_path)
    print('Static content in the path:' + static_path +
          " will be displayed via the url: " + static_url)
    print('isdebug:', settings['debug'])

    app = Application([
        url(r"/datasets/.*/type", DatatypeHandler),
        url(r"/datasets/.*/shape", ShapeHandler),
        url(r"/datasets/.*/attributes/.*", AttributeHandler),
        url(r"/datasets/.*/acls/.*", AclHandler),
        url(r"/groups/.*/attributes/.*", AttributeHandler),
        url(r"/groups/.*/acls/.*", AclHandler),
        url(r"/datatypes/.*/attributes/.*", AttributeHandler),
        url(r"/datasets/.*/attributes", AttributeHandler),
        url(r"/groups/.*/attributes", AttributeHandler),
        url(r"/datatypes/.*/attributes", AttributeHandler),
        url(r"/datatypes/.*/acls/.*", AclHandler),
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
        url(r"/info", InfoHandler),
        url(static_url, tornado.web.StaticFileHandler, {'path': static_path}),
        url(r"/(favicon\.ico)", tornado.web.StaticFileHandler, {'path': favicon_path}),
        url(r"/acls/.*", AclHandler),
        url(r"/acls", AclHandler),
        url(r"/", RootHandler),
        url(r".*", DefaultHandler)
    ],  **settings)
    return app


def main():
    # os.chdir(config.get('datapath'))
    
    app_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    os.chdir(app_dir)

    # create logger
    log = logging.getLogger("h5serv")
    log_file = config.get("log_file")
    log_level = config.get("log_level")
    
     
     
    # add file handler if given in config
    if log_file:
        print("Using logfile: ", log_file)
        # set daily rotating log
        
        handler = logging.handlers.TimedRotatingFileHandler(
            log_file,
            when="midnight",
            interval=1,
            backupCount=0,
            utc=True)
  
        # add formatter to handler
        # create formatter
        formatter = logging.Formatter(
            "%(asctime)s:%(levelname)s:%(filename)s:%(lineno)d::%(message)s")
        handler.setFormatter(formatter)
        # add handler to logger
        log.addHandler(handler)
    else:
        print("No logfile")
        
    # add default logger (to stdout)
    handler = logging.StreamHandler(sys.stdout)
    # create formatter
    formatter = logging.Formatter(
        "%(levelname)s:%(filename)s:%(lineno)d::%(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.propagate = False  # otherwise, we'll get repeated lines
    
    # log levels: ERROR, WARNING, INFO, DEBUG, or NOTSET
    if not log_level or log_level == "NOTSET":
        log.setLevel(logging.NOTSET)
    if log_level == "ERROR":
        print("Setting log level to: ERROR")
        log.setLevel(logging.ERROR)
    elif log_level == "WARNING":
        print("Setting log level to: WARNING")
        log.setLevel(logging.WARNING)
    elif log_level == "INFO":
        print("Setting log level to: INFO")
        log.setLevel(logging.INFO)
    elif log_level == "DEBUG":
        print("Setting log level to: DEBUG")
        log.setLevel(logging.DEBUG)
    else:
        print("No logging!")
        log.setLevel(logging.NOTSET)  
    
    log.info("log test")
    

    global server
    app = make_app()
    domain = config.get("domain")
    print("domain:", domain)
    
    
    ssl_cert = config.get('ssl_cert')
    if ssl_cert:
        print("ssl_cert:", ssl_cert)
    ssl_key = config.get('ssl_key')
    if ssl_key:
        print("ssl_key:", ssl_key)
    ssl_port = config.get('ssl_port')
    if ssl_port:
        print("ssl_port:", ssl_port)
    

    if ssl_cert and op.isfile(ssl_cert) and ssl_key and op.isfile(ssl_key) and ssl_port:
        ssl_cert_pwd = config.get('ssl_cert_pwd')
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(ssl_cert, keyfile=ssl_key, password=ssl_cert_pwd)
        ssl_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_ctx)
        ssl_server.listen(ssl_port)
        msg += " and port: " + str(ssl_port) + " (SSL)"
    else:
        server = tornado.httpserver.HTTPServer(app)
        port = int(config.get('port'))
        server.listen(port)
        msg = "Starting event loop on port: " + str(port)

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    log.info("INITIALIZING...")
    log.info(msg)
    print(msg)

    IOLoop.current().start()

if __name__ == "__main__":
    main()
