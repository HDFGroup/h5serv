**********************************************
GET Shape
**********************************************

Description
===========
Gets shape of a dataset.

Requests
========

Syntax
------
.. code-block:: http

    GET /datasets/<id>/shape HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
*<id>* is the UUID of the dataset that shape is requested for.
    
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

shape
^^^^^

A JSON object with the following keys:

class: A string with one of the following values:

 * H5S_NULL: A null dataspace, which has no elements
 * H5S_SCALAR: A dataspace with a single element (although possibly of a complext datatype)
 * H5S_SIMPLE: A dataspace that consists of a regular array of elements
 
dims: An integer array whose length is equal to the number of dimensions (rank) of the 
dataspace.  The value of each element gives the the current size of each dimension.  Dims
is not returned for H5S_NULL or H5S_SCALAR dataspaces.

maxdims: An integer array whose length is equal to the number of dimensions of the 
dataspace.  The value of each element gives the maximum size of each dimension. A value
of 0 indicates that the dimension has *unlimited* extent.  maxdims is not returned for
H5S_SIMPLE dataspaces which are not extensible or for H5S_NULL or H5S_SCALAR dataspaces.

fillvalue: A value of compatible with the dataset's type, which gives the *fill* value
for the dataset (the value for which elements will be initialized to when a dataspace
is extended).  fillvalue is only returned for extensible dataspaces.

created
^^^^^^^
A timestamp giving the time the datashape (same as the dataset) was created in 
UTC (ISO-8601 format).

lastModified
^^^^^^^^^^^^
A timestamp giving the most recent time the dataspace has been modified (i.e. a  
dimension has been extended) in UTC (ISO-8601 format).

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

    GET /datasets/3b57b6d4-a6a8-11e4-96b5-3c15c2da029e/shape HTTP/1.1
    host: tall.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Wed, 28 Jan 2015 04:43:41 GMT
    Content-Length: 445
    Etag: "76ed777f151c70d0560d1414bffe1515a3df86b0"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
    
   {    
   "shape": {
        "class": "H5S_SIMPLE"
        "dims": [10], 
    },
    "created": "2015-01-28T04:40:23Z",
    "lastModified": "2015-01-28T04:40:23Z", 
    "hrefs": [
        {"href": "http://tall.test.hdfgroup.org/datasets/3b57b6d4-a6a8-11e4-96b5-3c15c2da029e", "rel": "self"},
        {"href": "http://tall.test.hdfgroup.org/datasets/3b57b6d4-a6a8-11e4-96b5-3c15c2da029e", "rel": "owner"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/3b56ee54-a6a8-11e4-b2ae-3c15c2da029e", "rel": "root"}
      ], 
    }
    
Sample Request - Resizable
--------------------------

.. code-block:: http

    GET /datasets/a64010e8-a6aa-11e4-98c8-3c15c2da029e/shape HTTP/1.1
    host: resizable.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response - Resizable
----------------------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Wed, 28 Jan 2015 05:00:59 GMT
    Content-Length: 500
    Etag: "1082800980d6809a8008b22e225f1adde8afc73f"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
       
    {
    "shape": {
        "class": "H5S_SIMPLE",
        "dims": [10, 10], 
        "maxdims": [10, 0],
    }, 
    "created": "2015-01-28T04:40:23Z",
    "lastModified": "2015-01-28T04:40:23Z", 
    "hrefs": [
        {"href": "http://resizable.test.hdfgroup.org/datasets/a64010e8-a6aa-11e4-98c8-3c15c2da029e", "rel": "self"}, 
        {"href": "http://resizable.test.hdfgroup.org/datasets/a64010e8-a6aa-11e4-98c8-3c15c2da029e", "rel": "owner"}, 
        {"href": "http://resizable.test.hdfgroup.org/groups/a63f5dcf-a6aa-11e4-ab68-3c15c2da029e", "rel": "root"}
      ] 
    }
    
Related Resources
=================

* :doc:`GET_Dataset`
* :doc:`GET_DatasetType`
* :doc:`PUT_DatasetShape`
 

 
