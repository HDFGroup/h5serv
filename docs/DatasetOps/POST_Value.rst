**********************************************
POST Value
**********************************************

Description
===========
Gets values of a data for a given point selection (provided in the body of the 
request).

Requests
========

Syntax
------
.. code-block:: http

    POST /datasets/<id>/value HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
*<id>* is the UUID of the requested dataset t
    
Request Parameters
------------------
This implementation of the operation does not use request parameters.

Request Headers
---------------
This implementation of the operation uses only the request headers that are common
to most requests.  See :doc:`../CommonRequestHeaders`

Request Body
------------

The request body should be a JSON object with the following key:

points
^^^^^^

An array of points defining the selection.  Each point can either be an integer
(if the dataset has just one dimension), or an array where the length of the 
array is equal to the number of dimensions of the dataset.

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
An array of values where the length of the array is equal to the number of points 
in the request.  Each value will be a string, integer, or JSON object consist
with the dataset type (e.g. an compound type).

Special Errors
--------------

The implementation of the operation does not return special errors.  For general 
information on standard error codes, see :doc:`../CommonErrorResponses`.

Examples
========

Sample Request
--------------

.. code-block:: http

    POST /datasets/4e83ad1c-ab6e-11e4-babb-3c15c2da029e/value HTTP/1.1
    Content-Length: 92
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: tall.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
.. code-block:: json

    {
    "points": [19, 17, 13, 11, 7, 5, 3, 2]
    }
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Tue, 03 Feb 2015 06:31:38 GMT
    Content-Length: 47
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
 
    {
    "value": [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    }
    
Related Resources
=================

* :doc:`GET_Dataset`
* :doc:`GET_Value`
* :doc:`PUT_Value`
 

 