**********************************************
PUT Link
**********************************************

Description
===========
Creates a new link in a given group.

Either hard, soft, or external links can be created based on the request elements.
See examples below.

*Note:* any existing link with the same name will be replaced with the new link.


Requests
========

Syntax
------
.. code-block:: http

    PUT /groups/<id>/links/<name> HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
* *<id>* is the UUID of the group that the link will be created in.
* *<name>* is the URL-encoded name of the link.
    
Request Parameters
------------------
This implementation of the operation does not use request parameters.

Request Headers
---------------
This implementation of the operation uses only the request headers that are common
to most requests.  See :doc:`../CommonRequestHeaders`

Request Elements
----------------
The request body must include a JSON object that has the following key:

id
^^
The UUID of the group the new group should be linked to.  If the UUID is not valid,
the request will fail and a new group will not be created.
If this key is present, the h5path and h5domain keys will be ignored

h5path
^^^^^^
A string describing a path to an external resource.  If this key is present an
soft or external link will be created.

h5domain
^^^^^^^^
A string giving the external domain where the resource is present.
If this key is present, the h5path key must be provided as well.
 

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

Sample Request - Create Hard Link
---------------------------------

In group "e0309a0a-...", create a hard link named "g3" that points to the object 
with uuid "e032ad9c-...".

.. code-block:: http

    PUT /groups/e0309a0a-a198-11e4-b127-3c15c2da029e/links/g3 HTTP/1.1
    Content-Length: 46
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: tall_updated.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
.. code-block:: json

    {"id": "e032ad9c-a198-11e4-8d53-3c15c2da029e"}
    
Sample Response - Create Hard Link
----------------------------------

.. code-block:: http

    HTTP/1.1 201 Created
    Date: Wed, 21 Jan 2015 18:11:09 GMT
    Content-Length: 418
    Content-Type: application/json
    Server: TornadoServer/3.2.2

    
.. code-block:: json
  
    {
    "hrefs": [
        {"href": "http://tall_updated.test.hdfgroup.org/groups/e0309a0a-a198-11e4-b127-3c15c2da029e/links/g3", "rel": "self"}, 
        {"href": "http://tall_updated.test.hdfgroup.org/groups/e0309a0a-a198-11e4-b127-3c15c2da029e", "rel": "root"}, 
        {"href": "http://tall_updated.test.hdfgroup.org/", "rel": "home"}, 
        {"href": "http://tall_updated.test.hdfgroup.org/groups/e0309a0a-a198-11e4-b127-3c15c2da029e", "rel": "owner"}
      ]
    }
    
Sample Request - Create Soft Link
---------------------------------

In group "e0309a0a-...", create a soft link named "softlink" that contains the path 
"/somewhere".

.. code-block:: http

    PUT /groups/e0309a0a-a198-11e4-b127-3c15c2da029e/links/softlink HTTP/1.1
    Content-Length: 24
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: tall_updated.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
.. code-block:: json
   
    {"h5path": "/somewhere"}
    
Sample Response - Create Soft Link
----------------------------------

.. code-block:: http

    HTTP/1.1 201 Created
    Date: Wed, 21 Jan 2015 18:35:26 GMT
    Content-Length: 424
    Content-Type: application/json
    Server: TornadoServer/3.2.2
  
.. code-block:: json
      
    {
    "hrefs": [
        {"href": "http://tall_updated.test.hdfgroup.org/groups/e0309a0a-a198-11e4-b127-3c15c2da029e/links/softlink", "rel": "self"}, 
        {"href": "http://tall_updated.test.hdfgroup.org/groups/e0309a0a-a198-11e4-b127-3c15c2da029e", "rel": "root"}, 
        {"href": "http://tall_updated.test.hdfgroup.org/", "rel": "home"}, 
        {"href": "http://tall_updated.test.hdfgroup.org/groups/e0309a0a-a198-11e4-b127-3c15c2da029e", "rel": "owner"}
      ]
    }
    
Sample Request - Create External Link
-------------------------------------

In group "d2f8bd6b-...", create an external link named "extlink" that references the  
object at path: "/somewhere" in domain: "external_target.test.hdfgroup.org".

.. code-block:: http

    PUT /groups/d2f8bd6b-a1b1-11e4-ae1c-3c15c2da029e/links/extlink HTTP/1.1
    Content-Length: 69
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: tall_updated.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
.. code-block:: json
   
    {"h5domain": "external_target.test.hdfgroup.org", "h5path": "/dset1"}
    
Sample Response - Create External Link
--------------------------------------

.. code-block:: http

    HTTP/1.1 201 Created
    Date: Wed, 21 Jan 2015 21:09:45 GMT
    Content-Length: 423
    Content-Type: application/json
    Server: TornadoServer/3.2.2
  
.. code-block:: json
         
    {
    "hrefs": [
        {"href": "http://tall_updated.test.hdfgroup.org/groups/d2f8bd6b-a1b1-11e4-ae1c-3c15c2da029e/links/extlink", "rel": "self"}, 
        {"href": "http://tall_updated.test.hdfgroup.org/groups/d2f8bd6b-a1b1-11e4-ae1c-3c15c2da029e", "rel": "root"}, 
        {"href": "http://tall_updated.test.hdfgroup.org/", "rel": "home"}, 
        {"href": "http://tall_updated.test.hdfgroup.org/groups/d2f8bd6b-a1b1-11e4-ae1c-3c15c2da029e", "rel": "owner"}
        ]
    }
    
    
Related Resources
=================

* :doc:`DELETE_Link`
* :doc:`GET_Link`
* :doc:`GET_Links`
* :doc:`GET_Group`
 

 