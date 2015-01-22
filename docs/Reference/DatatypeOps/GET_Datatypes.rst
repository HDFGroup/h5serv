**********************************************
GET Datatypes
**********************************************

Description
===========
Gets all the committed datatypes in a domain.

Requests
========

Syntax
------
.. code-block:: http

    GET /datatypes HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
Request Parameters
------------------
This implementation of the operation uses the following request parameters (both 
optional):

Limit
^^^^^
If provided, a positive integer value specifying the maximum number of UUID's to return.

Marker
^^^^^^
If provided, a string value indicating that only UUID's that occur after the
marker value will be returned.


Request Headers
---------------
This implementation of the operation uses only the request headers that are common
to most requests.  See :doc:`../CommonRequestHeaders`

Responses
=========

Response Headers
----------------

This implementation of the operation uses only response headers that are common to 
most responses.  See :doc:`../CommonResponseHeaders`.

Response Elements
-----------------

On success, a JSON response will be returned with the following elements:

hrefs
^^^^^
An array of links to related resources.  See :doc:`../Hypermedia`.

Special Errors
--------------

The implementation of the operation does not return special errors.  For general 
information on standard error codes, see :doc:`../CommonErrorResponses`.

Examples
========

Sample Request
--------------

.. code-block:: http

    GET /datatypes HTTP/1.1
    host: namedtype.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Wed, 21 Jan 2015 22:42:30 GMT
    Content-Length: 350
    Etag: "e01f56869a9a919b1496c463f3569a2a7c319f11"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json

    {
    "datatypes": [
        "f54542e6-a1b4-11e4-90bf-3c15c2da029e", 
        "f545543d-a1b4-11e4-8fa4-3c15c2da029e"
    ], 
    "hrefs": [
        {"href": "http://namedtype.test.hdfgroup.org/datatypes", "rel": "self"}, 
        {"href": "http://namedtype.test.hdfgroup.org/groups/f545103d-a1b4-11e4-b4a1-3c15c2da029e", "rel": "root"}, 
        {"href": "http://namedtype.test.hdfgroup.org/", "rel": "home"}
      ]
    }
    
Sample Request with Marker and Limit
------------------------------------

This example uses the "Marker" request parameter to return only UUIDs after the given
Marker value.
Also the "Limit" request parameter is used to limit the number of UUIDs in the response to 5.

.. code-block:: http

    GET /datatypes?Marker=d779cd5e-a1e6-11e4-8fc5-3c15c2da029e&Limit=5 HTTP/1.1
    host: type1k.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
 
Sample Response with Marker and Limit
-------------------------------------

 .. code-block:: http
 
    HTTP/1.1 200 OK
    Date: Thu, 22 Jan 2015 03:32:13 GMT
    Content-Length: 461
    Etag: "a2e2d5a3ae63cd504d02b51d99f27b30d17b75b5"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
   
 .. code-block:: json
      
    {
    "datatypes": [
        "d779ddd9-a1e6-11e4-89e5-3c15c2da029e", 
        "d779ef11-a1e6-11e4-8837-3c15c2da029e", 
        "d77a008a-a1e6-11e4-8840-3c15c2da029e", 
        "d77a121e-a1e6-11e4-b2b0-3c15c2da029e", 
        "d77a2523-a1e6-11e4-aa6d-3c15c2da029e"
      ], 
    "hrefs": [
        {"href": "http://type1k.test.hdfgroup.org/datatypes", "rel": "self"}, 
        {"href": "http://type1k.test.hdfgroup.org/groups/d7742c14-a1e6-11e4-b2a8-3c15c2da029e", "rel": "root"}, 
        {"href": "http://type1k.test.hdfgroup.org/", "rel": "home"}
      ]
    }
        
    
Related Resources
=================

* :doc:`DELETE_Datatype`
* :doc:`GET_Datatype`
* :doc:`POST_Datatype`
* :doc:`../DatasetOps/POST_Dataset`
* :doc:`../AttrOps/PUT_Attribute`
 

 