**********************************************
DELETE Link
**********************************************

Description
===========
The implementation of the DELETE operation deletes the link named in the URI.   

Groups, datatypes, and datasets that are referenced by the link will **not** be
deleted.   To delete groups, datatypes or datasets, use the appropriate DELETE operation
for those objects.

Requests
========

Syntax
------
.. code-block:: http

    DELETE /groups/<id>/links/<name> HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
* *<id>* is the UUID of the group the link is a member of.
* *<name>* is the URL-encoded name of the link.
    
    
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

An attempt to delete the root group will return 403 - Forbidden.  For general 
information on standard error codes, see :doc:`../CommonErrorResponses`.

Examples
========

Sample Request
--------------

.. code-block:: http

    DELETE /groups/25dd052b-a06d-11e4-a29e-3c15c2da029e/links/deleteme HTTP/1.1
    Content-Length: 0
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: tall_updated.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Tue, 20 Jan 2015 06:25:37 GMT
    Content-Length: 299
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
  
    {
    "hrefs": [
        {"href": "http://tall_updated.test.hdfgroup.org/groups/25dd052b-a06d-11e4-a29e-3c15c2da029e", "rel": "root"}, 
        {"href": "http://tall_updated.test.hdfgroup.org/", "rel": "home"}, 
        {"href": "http://tall_updated.test.hdfgroup.org/groups/25dd052b-a06d-11e4-a29e-3c15c2da029e", "rel": "owner"}
        ]
    }
    
Related Resources
=================

* :doc:`../DatasetOps/DELETE_Dataset`
* :doc:`../DatatypeOps/DELETE_Datatype`
* :doc:`DELETE_Group`
* :doc:`GET_Link`
* :doc:`GET_Groups`
* :doc:`POST_Group`
 

 