**********************************************
GET Links
**********************************************

Description
===========
Returns all the links for a given group.

Requests
========

Syntax
------
.. code-block:: http

    GET /groups/<id>/links HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
* *<id>* is the UUID of the group the links to be returned are a member of.
    
Request Parameters
------------------
This implementation of the operation uses the following request parameters (both 
optional):

Limit
^^^^^
If provided, a positive integer value specifying the maximum number of links to return.

Marker
^^^^^^
If provided, a string value indicating that only links that occur after the
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

links
^^^^^
An array of JSON objects giving information about each link returned.
See :doc:`GET_Link` for a description of the link response elements.

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

    GET /groups/0ad37be1-a06f-11e4-8651-3c15c2da029e/links HTTP/1.1
    host: tall.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0  
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Tue, 20 Jan 2015 06:55:19 GMT
    Content-Length: 607
    Etag: "49edcce6a8f724108d41d52c98002d6255286ff8"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
   
    {
    "links": [
        {
            "title": "g1.2.1",
            "class": "H5L_TYPE_HARD",
            "collection": "groups",
            "id": "0ad38d45-a06f-11e4-a909-3c15c2da029e"
        }, 
        {
            "title": "extlink",
            "class": "H5L_TYPE_EXTERNAL",
            "h5path": "somepath",
            "file": "somefile"  
        }
    ],
    "hrefs": [
        {"href": "http://tall.test.hdfgroup.org/groups/0ad37be1-a06f-11e4-8651-3c15c2da029e/links", "rel": "self"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/0ad2e151-a06f-11e4-bc68-3c15c2da029e", "rel": "root"}, 
        {"href": "http://tall.test.hdfgroup.org/", "rel": "home"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/0ad37be1-a06f-11e4-8651-3c15c2da029e", "rel": "owner"}
        ]
    } 
    
Sample Request Batch
--------------------

.. code-block:: http

    GET /groups/76bddb1e-a06e-11e4-86d6-3c15c2da029e/links?Marker=g0089&Limit=5 HTTP/1.1
    host: group1k.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0  
    
Sample Response Batch
---------------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Tue, 20 Jan 2015 07:30:03 GMT
    Content-Length: 996
    Etag: "221affdeae54076d3493ce8ce0ed80ddb89c6e27"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
   
     
    {
    "links": [
        {"title": "g0090", "id": "76c53485-a06e-11e4-96f3-3c15c2da029e", "class": "H5L_TYPE_HARD", "collection": "groups"}, 
        {"title": "g0091", "id": "76c54d40-a06e-11e4-a342-3c15c2da029e", "class": "H5L_TYPE_HARD", "collection": "groups"}, 
        {"title": "g0092", "id": "76c564f5-a06e-11e4-bccd-3c15c2da029e", "class": "H5L_TYPE_HARD", "collection": "groups"}, 
        {"title": "g0093", "id": "76c57d19-a06e-11e4-a9a8-3c15c2da029e", "class": "H5L_TYPE_HARD", "collection": "groups"}, 
        {"title": "g0094", "id": "76c5941c-a06e-11e4-b641-3c15c2da029e", "class": "H5L_TYPE_HARD", "collection": "groups"}
      ],
    "hrefs": [
        {"href": "http://group1k.test.hdfgroup.org/groups/76bddb1e-a06e-11e4-86d6-3c15c2da029e/links", "rel": "self"}, 
        {"href": "http://group1k.test.hdfgroup.org/groups/76bddb1e-a06e-11e4-86d6-3c15c2da029e", "rel": "root"}, 
        {"href": "http://group1k.test.hdfgroup.org/", "rel": "home"}, 
        {"href": "http://group1k.test.hdfgroup.org/groups/76bddb1e-a06e-11e4-86d6-3c15c2da029e", "rel": "owner"}
      ]
    } 
       
Related Resources
=================

* :doc:`DELETE_Link`
* :doc:`GET_Link`
* :doc:`GET_Group`
* :doc:`PUT_Link`
 

 