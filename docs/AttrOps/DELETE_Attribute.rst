**********************************************
DELETE Attribute
**********************************************

Description
===========
The implementation of the DELETE operation deletes the attribute named in the URI.  All 
attributes and links of the dataset will also be deleted.

Requests
========

Syntax
------
.. code-block:: http

    DELETE /groups/<id>/<name> HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
* *<id>* is the UUID of the dataset/group/committed datatype
* *<name>* is the url-encoded name of the requested attribute
    
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

    DELETE /groups/36ae688a-ac0e-11e4-a44b-3c15c2da029e/attributes/attr1 HTTP/1.1
    Content-Length: 0
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: tall_updated.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Wed, 04 Feb 2015 01:36:17 GMT
    Content-Length: 420
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
  
    {
    "hrefs": [
        {"href": "http://tall_updated.test.hdfgroup.org/groups/36ae688a-ac0e-11e4-a44b-3c15c2da029e/attributes", "rel": "self"}, 
        {"href": "http://tall_updated.test.hdfgroup.org/groups/36ae688a-ac0e-11e4-a44b-3c15c2da029e", "rel": "owner"}, 
        {"href": "http://tall_updated.test.hdfgroup.org/groups/36ae688a-ac0e-11e4-a44b-3c15c2da029e", "rel": "root"}, 
        {"href": "http://tall_updated.test.hdfgroup.org/", "rel": "home"}
      ]
    }
    
Related Resources
=================

* :doc:`GET_Attributes`
* :doc:`GET_Attribute`
* :doc:`../DatasetOps/GET_Dataset`
* :doc:`../DatatypeOps/GET_Datatype`
* :doc:`../GroupOps/GET_Group`
* :doc:`PUT_Attribute`
 

 