**********************************************
GET Groups
**********************************************

Description
===========
Returns UUIDs for all the groups in a domain (other than the root group).

Requests
========

Syntax
------
.. code-block:: http

    GET /groups HTTP/1.1
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

groups
^^^^^^
An array of UUIDs - one for each group (including the root group) in the domain.
If the "Marker" and/or "Limit" request parameters are used, a subset of the UUIDs
may be returned.

hrefs
^^^^^
An array of hypertext links to related resources.  See :doc:`../Hypermedia`.

Special Errors
--------------

The implementation of the operation does not return special errors.  For general 
information on standard error codes, see :doc:`../CommonErrorResponses`.

Examples
========

Sample Request
--------------

.. code-block:: http

    GET /groups HTTP/1.1
    host: tall.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Fri, 16 Jan 2015 21:53:48 GMT
    Content-Length: 449
    Etag: "83575a7865761b6d4eaf5d285ab1de062c49250b"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
    
    {
    "groups": [
        "052e001e-9d33-11e4-9a3d-3c15c2da029e", 
        "052e13bd-9d33-11e4-91a6-3c15c2da029e", 
        "052e5ae8-9d33-11e4-888d-3c15c2da029e", 
        "052e700a-9d33-11e4-9fe4-3c15c2da029e", 
        "052e89c7-9d33-11e4-b9bc-3c15c2da029e"
        ],
    "hrefs": [
        {"href": "http://tall.test.hdfgroup.org/groups", "rel": "self"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/052dcbbd-9d33-11e4-86ce-3c15c2da029e", "rel": "root"}, 
        {"href": "http://tall.test.hdfgroup.org/", "rel": "home"}
        ] 
    }
    
Sample Request with Marker and Limit
------------------------------------

This example uses the "Marker" request parameter to return only UUIDs after the given
Marker value.
The "Limit" request parameter is used to limit the number of UUIDs in the response to 5.

.. code-block:: http

    GET /groups?Marker=cba6e3fd-9dbd-11e4-bf4a-3c15c2da029e&Limit=5 HTTP/1.1
    host: group1k.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
 
Sample Response with Marker and Limit
-------------------------------------

 .. code-block:: http
 
    HTTP/1.1 200 OK
    Date: Fri, 16 Jan 2015 22:02:46 GMT
    Content-Length: 458
    Etag: "49221af3436fdaca7e26c74b491ccf8698555f08"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
   
 .. code-block:: json
    
    {
    "groups": [
        "cba6fc19-9dbd-11e4-846e-3c15c2da029e", 
        "cba71842-9dbd-11e4-abd0-3c15c2da029e", 
        "cba73442-9dbd-11e4-a6e9-3c15c2da029e", 
        "cba74fc5-9dbd-11e4-bc15-3c15c2da029e", 
        "cba77c2e-9dbd-11e4-9c71-3c15c2da029e"
        ],  
    "hrefs": [
        {"href": "http://group1k.test.hdfgroup.org/groups", "rel": "self"}, 
        {"href": "http://group1k.test.hdfgroup.org/groups/cb9ebf11-9dbd-11e4-9e83-3c15c2da029e", "rel": "root"}, 
        {"href": "http://group1k.test.hdfgroup.org/", "rel": "home"}
        ]
    } 
        
Related Resources
=================

* :doc:`DELETE_Group`
* :doc:`GET_Links`
* :doc:`GET_Group`
* :doc:`POST_Group`
 

 