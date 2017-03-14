**********************************************
GET Group
**********************************************

Description
===========
Returns information about the group with the UUID given in the URI.

Requests
========

Syntax
------
.. code-block:: http

    GET /groups/<id> HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
*<id>* is the UUID of the requested group.
    
Request Parameters
------------------

include_links
^^^^^^^^^^^^^

If this request parameter is provided, the links of the group are included in the response.

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

id
^^
The UUID of the requested group

attributeCount
^^^^^^^^^^^^^^
The number of attributes belonging to the group.

linkCount
^^^^^^^^^
The number of links belonging to the group.

created
^^^^^^^
A timestamp giving the time the group was created in UTC (ISO-8601 format).

lastModified
^^^^^^^^^^^^
A timestamp giving the most recent time the group has been modified (i.e. attributes or 
links updated) in UTC (ISO-8601 format).

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

    GET /groups/052dcbbd-9d33-11e4-86ce-3c15c2da029e HTTP/1.1
    host: tall.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Fri, 16 Jan 2015 20:06:08 GMT
    Content-Length: 660
    Etag: "2c410d1c469786f25ed0075571a8e7a3f313cec1"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json

    {
    "id": "052dcbbd-9d33-11e4-86ce-3c15c2da029e",
    "attributeCount": 2,
    "linkCount": 2,
    "created": "2015-01-16T03:47:22Z", 
    "lastModified": "2015-01-16T03:47:22Z",    
    "hrefs": [
        {"href": "http://tall.test.hdfgroup.org/groups/052dcbbd-9d33-11e4-86ce-3c15c2da029e", "rel": "self"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/052dcbbd-9d33-11e4-86ce-3c15c2da029e/links", "rel": "links"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/052dcbbd-9d33-11e4-86ce-3c15c2da029e", "rel": "root"}, 
        {"href": "http://tall.test.hdfgroup.org/", "rel": "home"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/052dcbbd-9d33-11e4-86ce-3c15c2da029e/attributes", "rel": "attributes"}
        ]
     }
    
Related Resources
=================

* :doc:`DELETE_Group`
* :doc:`GET_Links`
* :doc:`GET_Groups`
* :doc:`POST_Group`
* :doc:`../AttrOps/GET_Attribute`
 

 