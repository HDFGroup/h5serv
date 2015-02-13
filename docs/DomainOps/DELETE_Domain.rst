**********************************************
DELETE Domain
**********************************************

Description
===========
The DELETE operation deletes the given domain and
all its resources (groups, datasets, attributes, etc.).

Requests
========

Syntax
------
.. code-block:: http

    DELETE /  HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
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

This implementation of the operation does not return any response elements.


Special Errors
--------------

The implementation of the operation does not return special errors.  For general 
information on standard error codes, see :doc:`../CommonErrorResponses`.

Examples
========

Sample Request
--------------

.. code-block:: http

   DELETE / HTTP/1.1
   Content-Length: 0
   User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
   host: deleteme.test.hdfgroup.org
   Accept: */*
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Fri, 16 Jan 2015 03:47:33 GMT
    Content-Length: 0
    Content-Type: text/html; charset=UTF-8
    Server: TornadoServer/3.2.2
    
 
    
Related Resources
=================

* :doc:`GET_Domain`
* :doc:`PUT_Domain`
 

 