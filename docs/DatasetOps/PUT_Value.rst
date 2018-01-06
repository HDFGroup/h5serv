**********************************************
PUT Value
**********************************************

Description
===========
Update the values in a dataset.

Requests
========

Syntax
------
.. code-block:: http

    PUT /datasets/<id>/value HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
*<id>* is the UUID of the requested dataset.
    
Request Parameters
------------------
This implementation of the operation does not use request parameters.

Request Headers
---------------
This implementation of the operation uses only the request headers that are common
to most requests.  See :doc:`../CommonRequestHeaders`

Request Body
------------
The request body should be a JSON object with the following keys:

start:
^^^^^^
An optional key that gives the starting coordinate of the selection to be updated.  The
start value can either be an integer (for 1 dimensional arrays) or an array of integers
where the length of the array is equal to the number of dimensions of the dataset.  Each
value must be greater than equal to zero and less than the extent of the corresponding
dimension.

If start is not provided, the selection starts at 0 for each dimension.

stop:
^^^^^
An optional key that gives the ending coordinate of the selection to be updated.
The stop value can either be an integer (for 1 dimensional arrays) or an array of integers
where the length of the array is equal to the number of dimensions of the dataset.  Each
value must be greater than equal to start (or zero if start is not provided) and less than
the extent of the corresponding dimension.

step:
^^^^^
An optional key that gives the step value (i.e. the increment of the coordinate for
each supplied value). The step value can either be an integer (for 1 dimensional arrays) or
an array of integers where the length of the array is equal to the number of dimensions of
the dataset.  Each value must be greater than equal to start (or zero if start is not 
provided) and less than or equal to the extent of the corresponding dimension.

points:
^^^^^^^

An optional key that contains a list of array elements to be updated.  Each element of the list should be an 
an integer if the dataset is of rank 1 or an n-element list (which n is the dataset rank) is the dataset
rank is greater than 1.  If points is provided (indicating a point selection update), then start, stop, 
and step (used for hyperslab selection) should not be provied.

value:
^^^^^^
A JSON array containing the data values to be written.

value_base64:
^^^^^^^^^^^^^

Use this key instead of "value" to use base64-encoded binary data rather than JSON ascii.  This will be more
efficient for large data transfers than using a JSON array.

Note: "value_base64" is only supported for fixed length datatypes.


Responses
=========

Response Headers
----------------

This implementation of the operation uses only response headers that are common to 
most responses.  See :doc:`../CommonResponseHeaders`.

Response Elements
-----------------

No response elements are returned.

Special Errors
--------------

The implementation of the operation does not return special errors.  For general 
information on standard error codes, see :doc:`../CommonErrorResponses`.

Examples
========


Sample Request
--------------

This example writes a 10x10 integer datasets with the values 0-99 inclusive.

.. code-block:: http

    PUT /datasets/817e2280-ab5d-11e4-afe6-3c15c2da029e/value HTTP/1.1
    Content-Length: 465
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: valueput.datasettest.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
.. code-block:: json

    {
    "value": [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 
        [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], 
        [20, 21, 22, 23, 24, 25, 26, 27, 28, 29], 
        [30, 31, 32, 33, 34, 35, 36, 37, 38, 39], 
        [40, 41, 42, 43, 44, 45, 46, 47, 48, 49], 
        [50, 51, 52, 53, 54, 55, 56, 57, 58, 59], 
        [60, 61, 62, 63, 64, 65, 66, 67, 68, 69], 
        [70, 71, 72, 73, 74, 75, 76, 77, 78, 79], 
        [80, 81, 82, 83, 84, 85, 86, 87, 88, 89], 
        [90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
      ]
    }
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Tue, 03 Feb 2015 04:31:22 GMT
    Content-Length: 0
    Content-Type: text/html; charset=UTF-8
    Server: TornadoServer/3.2.2
    
    
Sample Request - Selection
--------------------------

This example writes a portion of the dataset by using the start and stop keys in the
request.

.. code-block:: http

    PUT /datasets/b2d0af00-ab65-11e4-a874-3c15c2da029e/value HTTP/1.1
    Content-Length: 92
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: valueputsel.datasettest.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
.. code-block:: json

    {     
    "start": 5, 
    "stop": 10,
    "value": [13, 17, 19, 23, 29]
    }
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Tue, 03 Feb 2015 05:30:01 GMT
    Content-Length: 0
    Content-Type: text/html; charset=UTF-8
    Server: TornadoServer/3.2.2
    
    
Related Resources
=================

* :doc:`GET_Dataset`
* :doc:`GET_Value`
* :doc:`POST_Value`
 

 