**********************************************
GET Datasets
**********************************************

Description
===========
Returns UUIDs for all the datasets in a domain.

Requests
========

Syntax
------
.. code-block:: http

    GET /datasets HTTP/1.1
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

datasets
^^^^^^^^
An array of UUID's, one for each dataset in the domain.

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

    GET /datasets HTTP/1.1
    host: tall.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Fri, 23 Jan 2015 06:33:36 GMT
    Content-Length: 413
    Etag: "977e96c7bc63a6e05d10d56565df2ab8d30e404d"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
  
    
    {
    "datasets": [
        "c8d7dd14-a2c6-11e4-a68c-3c15c2da029e", 
        "c8d7f159-a2c6-11e4-99af-3c15c2da029e", 
        "c8d83759-a2c6-11e4-8713-3c15c2da029e", 
        "c8d84a8a-a2c6-11e4-b457-3c15c2da029e"
      ],
    "hrefs": [
        {"href": "http://tall.test.hdfgroup.org/datasets", "rel": "self"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/c8d7842b-a2c6-11e4-b4f1-3c15c2da029e", "rel": "root"}, 
        {"href": "http://tall.test.hdfgroup.org/", "rel": "home"}
      ]
    }
    
Sample Request with Marker and Limit
------------------------------------

This example uses the "Marker" request parameter to return only UUIDs after the given
Marker value.
The "Limit" request parameter is used to limit the number of UUIDs in the response to 5.

.. code-block:: http

    GET /datasets?Marker=817db263-a2cc-11e4-87f2-3c15c2da029e&Limit=5 HTTP/1.1
    host: dset1k.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
 
Sample Response with Marker and Limit
-------------------------------------

.. code-block:: http
 
    HTTP/1.1 200 OK
    Date: Fri, 23 Jan 2015 06:53:52 GMT
    Content-Length: 459
    Etag: "cb708d4839cc1e165fe6bb30718e49589ef140f4"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
   
.. code-block:: json
     
    {
    "datasets": [
        "817dcfb8-a2cc-11e4-9197-3c15c2da029e", 
        "817de9ee-a2cc-11e4-8378-3c15c2da029e", 
        "817e028a-a2cc-11e4-8ce3-3c15c2da029e", 
        "817e1b61-a2cc-11e4-ba39-3c15c2da029e", 
        "817e341c-a2cc-11e4-a16f-3c15c2da029e"
      ],
    "hrefs": [
        {"href": "http://dset1k.test.hdfgroup.org/datasets", "rel": "self"}, 
        {"href": "http://dset1k.test.hdfgroup.org/groups/81760a80-a2cc-11e4-bb55-3c15c2da029e", "rel": "root"}, 
        {"href": "http://dset1k.test.hdfgroup.org/", "rel": "home"}
      ]
    } 
    
Related Resources
=================

* :doc:`DELETE_Dataset`
* :doc:`GET_Dataset`
* :doc:`POST_Dataset`
 

 