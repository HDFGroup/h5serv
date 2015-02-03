**********************************************
GET Value
**********************************************

Description
===========
Gets data values of a dataset.

Requests
========

Syntax
------
.. code-block:: http

    GET /datasets/<id>/value HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
*<id>* is the UUID of the requested dataset.
    
Request Parameters
------------------

select
^^^^^^
Optionally the request can provide a select value to indicate a hyperslab selection for
the values to be returned - i.e. a rectangular (in 1, 2, or more dimensions) region of 
the dataset.   Format is the following as a url-encoded value:

[dim1_start:dim1_end:dim1_step, dim2_start:dim2_end:dim2_step, ... , dimn_start:dimn_stop:dimn_step]

The number of tuples "start:stop:step" should equal the number of dimensions of the dataset. 

For each tuple:

* start must be greater than equal to zero and less than the dimension extent
* stop must be greater than or equal to start and less than the dimension extent
* step is optional and if provided must be greater than 0.  If not provided, the step value for that dimension is assumed to be 1.

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

value
^^^^^
A json array (or value for scalar datasets) giving the values of the requested 
dataset region.

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

    GET /datasets/548f2f21-a83c-11e4-8baf-3c15c2da029e/value HTTP/1.1
    host: tall.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Fri, 30 Jan 2015 04:56:20 GMT
    Content-Length: 776
    Etag: "788efb3caaba7fd2ae5d1edb40b474ba94c877a8"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
    
.. code-block:: json

    {
    "value": [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 
        [0, 2, 4, 6, 8, 10, 12, 14, 16, 18], 
        [0, 3, 6, 9, 12, 15, 18, 21, 24, 27], 
        [0, 4, 8, 12, 16, 20, 24, 28, 32, 36], 
        [0, 5, 10, 15, 20, 25, 30, 35, 40, 45], 
        [0, 6, 12, 18, 24, 30, 36, 42, 48, 54], 
        [0, 7, 14, 21, 28, 35, 42, 49, 56, 63], 
        [0, 8, 16, 24, 32, 40, 48, 56, 64, 72], 
        [0, 9, 18, 27, 36, 45, 54, 63, 72, 81]
      ],
    "hrefs": [
        {"href": "http://tall.test.hdfgroup.org/datasets/548f2f21-a83c-11e4-8baf-3c15c2da029e/value", "rel": "self"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/548ed535-a83c-11e4-b58b-3c15c2da029e", "rel": "root"}, 
        {"href": "http://tall.test.hdfgroup.org/datasets/548f2f21-a83c-11e4-8baf-3c15c2da029e", "rel": "owner"}, 
        {"href": "http://tall.test.hdfgroup.org/", "rel": "home"}
      ] 
    }
    
Sample Request - Selection
--------------------------

.. code-block:: http

    GET /datasets/a299db70-ab57-11e4-9c00-3c15c2da029e/value?select=[1:9,1:9:2] HTTP/1.1
    host: tall.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response - Selection
---------------------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Tue, 03 Feb 2015 04:01:41 GMT
    Content-Length: 529
    Etag: "b370a3d34bdd7ebf57a496bc7f0da7bc5a1aafb9"
    Content-Type: application/json
    Server: TornadoServer/3.2.2    
    
.. code-block:: json
   
    {
    "value": [
       [1, 3, 5, 7], 
       [2, 6, 10, 14], 
       [3, 9, 15, 21], 
       [4, 12, 20, 28], 
       [5, 15, 25, 35], 
       [6, 18, 30, 42], 
       [7, 21, 35, 49], 
       [8, 24, 40, 56]
    ],  
    "hrefs": [
        {"href": "http://tall.test.hdfgroup.org/datasets/a299db70-ab57-11e4-9c00-3c15c2da029e/value", "rel": "self"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/a29982cf-ab57-11e4-b976-3c15c2da029e", "rel": "root"}, 
        {"href": "http://tall.test.hdfgroup.org/datasets/a299db70-ab57-11e4-9c00-3c15c2da029e", "rel": "owner"}, 
        {"href": "http://tall.test.hdfgroup.org/", "rel": "home"}
      ]
    }
       
Related Resources
=================

* :doc:`GET_Dataset`
* :doc:`POST_Value`
* :doc:`PUT_Value`
 

 