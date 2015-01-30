**********************************************
PUT Shape
**********************************************

Description
===========
Modifies the dimensions of a dataset.  Dimensions can only be changed if the dataset
was initially created with that dimension as *extensible* - i.e. the maxdims value
for that dimension is larger than the initial dimension size (or maxdims set to 0).

*Note:* Dimensions can only be made larger, they can not be reduced.

Requests
========

Syntax
------
.. code-block:: http

    PUT /datasets/<id>/shape HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
*<id>* is the UUID of the dataset whose shape will be modified.
    
Request Parameters
------------------
This implementation of the operation does not use request parameters.

Request Headers
---------------
This implementation of the operation uses only the request headers that are common
to most requests.  See :doc:`../CommonRequestHeaders`

Request Elements
----------------
The request body must include a JSON object with a "shape" key as described below:

shape
^^^^^
An integer array giving the new dimensions of the dataset.

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

    PUT /datasets/b9b6acc0-a839-11e4-aa86-3c15c2da029e/shape HTTP/1.1
    Content-Length: 19
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: resized.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
.. code-block:: json

    {
    "shape": [10, 25]
    }
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 201 Created
    Date: Fri, 30 Jan 2015 04:47:47 GMT
    Content-Length: 331
    Content-Type: application/json
    Server: TornadoServer/3.2.2   
    
.. code-block:: json

    {
    "hrefs": [
        {"href": "http://resized.test.hdfgroup.org/datasets/22e1b235-a83b-11e4-97f4-3c15c2da029e", "rel": "self"}, 
        {"href": "http://resized.test.hdfgroup.org/datasets/22e1b235-a83b-11e4-97f4-3c15c2da029e", "rel": "owner"}, 
        {"href": "http://resized.test.hdfgroup.org/groups/22dfff8f-a83b-11e4-883d-3c15c2da029e", "rel": "root"}
      ]
    }
    
Related Resources
=================

* :doc:`GET_Dataset`
* :doc:`GET_DatasetShape`
* :doc:`GET_Value`
* :doc:`POST_Value`
* :doc:`PUT_Value`
 

 