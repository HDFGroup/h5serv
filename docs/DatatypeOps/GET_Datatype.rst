**********************************************
GET Datatype
**********************************************

Description
===========
Returns information about the committed datatype with the UUID given in the URI.

Requests
========

Syntax
------
.. code-block:: http

    GET /datatypes/<id> HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
*<id>* is the UUID of the requested datatype.
    
Request Parameters
------------------
This implementation of the operation does not use request parameters.

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

The UUID of the datatype object.

type
^^^^
A JSON object representing the type of the datatype object.

attributeCount
^^^^^^^^^^^^^^
The number of attributes belonging to the datatype.

created
^^^^^^^
A timestamp giving the time the dataset was created in UTC (ISO-8601 format).

lastModified
^^^^^^^^^^^^
A timestamp giving the most recent time the dataset has been modified (i.e. attributes updated) in UTC (ISO-8601 format).

hrefs
^^^^^
An array of links to related resources.  See :doc:`../Hypermedia`.

Special Errors
--------------

The implementation of the operation does not return special errors.  For general 
information on standard error codes, see :doc:`../CommonErrorResponses`.

Examples
========

Get the committed datatype with UUID: "f545543d-...".

Sample Request
--------------

.. code-block:: http

    GET /datatypes/f545543d-a1b4-11e4-8fa4-3c15c2da029e HTTP/1.1
    host: namedtype.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Wed, 21 Jan 2015 21:36:49 GMT
    Content-Length: 619
    Etag: "c53bc5b2d3c3b5059b71ef92ca7d144a2df54456"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json

    {
    "id": "f545543d-a1b4-11e4-8fa4-3c15c2da029e",
    "type": {
        "base": "H5T_IEEE_F32LE", 
        "class": "H5T_FLOAT"
      }, 
    "created": "2015-01-21T21:32:01Z", 
    "lastModified": "2015-01-21T21:32:01Z", 
    "attributeCount": 1, 
    "hrefs": [
        {"href": "http://namedtype.test.hdfgroup.org/datatypes/f545543d-a1b4-11e4-8fa4-3c15c2da029e", "rel": "self"}, 
        {"href": "http://namedtype.test.hdfgroup.org/groups/f545103d-a1b4-11e4-b4a1-3c15c2da029e", "rel": "root"}, 
        {"href": "http://namedtype.test.hdfgroup.org/datatypes/f545543d-a1b4-11e4-8fa4-3c15c2da029e/attributes", "rel": "attributes"}, 
        {"href": "http://namedtype.test.hdfgroup.org/", "rel": "home"}
      ]     
    }
    
Related Resources
=================

* :doc:`DELETE_Datatype`
* :doc:`GET_Datatypes`
* :doc:`POST_Datatype`
* :doc:`../DatasetOps/POST_Dataset`
* :doc:`../AttrOps/PUT_Attribute`
 

 