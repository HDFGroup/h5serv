**********************************************
PUT Domain
**********************************************

Description
===========
This operation creates a new domain.

*Note*: Initially the only object contained in the domain is the root group.  Use other
PUT and POST operations to create new objects in the domain.

*Note*: The operation will fail if the domain already exists (a 409 code will be returned).

Requests
========

Syntax
------
.. code-block:: http

    PUT / HTTP/1.1
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

On success, a JSON response will be returned with the following elements:

root
^^^^
The UUID of the root group of this domain.

created
^^^^^^^
A timestamp giving the time the domain was created in UTC (ISO-8601 format).

lastModified
^^^^^^^^^^^^
A timestamp giving the most recent time that any content in the domain has been
modified in UTC (ISO-8601 format).

hrefs
^^^^^
An array of links to related resources.  See :doc:`../Hypermedia`.

Special Errors
--------------

The implementation of the operation does not return any special errors.  For general 
information on standard error codes, see :doc:`../CommonErrorResponses`.

An http status code of 409 (Conflict) will be returned if the domain already exists.

Examples
========

Sample Request
--------------

.. code-block:: http

    PUT / HTTP/1.1
    Content-Length: 0
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: newfile.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 201 Created
    Date: Fri, 16 Jan 2015 04:11:52 GMT
    Content-Length: 523
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json

    
  {
    "root": "cd31cfdc-9d35-11e4-aa58-3c15c2da029e",
    "created": "2015-01-16T04:11:52Z",
    "lastModified": "2015-01-16T04:11:52Z", 
    "hrefs": [
       {"href": "http://newfile.test.hdfgroup.org/", "rel": "self"}, 
       {"href": "http://newfile.test.hdfgroup.org/datasets", "rel": "database"}, 
       {"href": "http://newfile.test.hdfgroup.org/groups", "rel": "groupbase"}, 
       {"href": "http://newfile.test.hdfgroup.org/datatypes", "rel": "typebase"}, 
       {"href": "http://newfile.test.hdfgroup.org/groups/cd31cfdc-9d35-11e4-aa58-3c15c2da029e", "rel": "root"}
       ]    
  }
    
Related Resources
=================

* :doc:`DELETE_Domain`
* :doc:`../GroupOps/GET_Group`
* :doc:`GET_Domain`
 

 