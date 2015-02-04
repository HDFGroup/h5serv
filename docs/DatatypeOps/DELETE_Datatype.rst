**********************************************
DELETE Datatype
**********************************************

Description
===========
The implementation of the DELETE operation deletes the committed datatype
 named in the URI.  All attributes the datatype will also be deleted.

Requests
========

Syntax
------
.. code-block:: http

    DELETE /datatypes/<id> HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
*<id>* is the UUID of the datatype to be deleted.
    
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

    DELETE /datatypes/93b6a335-ac44-11e4-8d71-3c15c2da029e HTTP/1.1
    Content-Length: 0
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: namedtype_deleted.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Wed, 04 Feb 2015 08:05:26 GMT
    Content-Length: 363
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
  
    {
    "hrefs": [
        {"href": "http://namedtype_deleted.test.hdfgroup.org/datatypes", "rel": "self"}, 
        {"href": "http://namedtype_deleted.test.hdfgroup.org/", "rel": "home"}, 
        {"href": "http://namedtype_deleted.test.hdfgroup.org/groups/93b51245-ac44-11e4-8a21-3c15c2da029e", "rel": "root"}
      ]
    }
    
Related Resources
=================

* :doc:`../AttrOps/GET_Attributes`
* :doc:`GET_Datatype`
* :doc:`GET_Datatypes`
* :doc:`POST_Datatype`
* :doc:`../DatasetOps/POST_Dataset`
* :doc:`../AttrOps/PUT_Attribute`
 

 