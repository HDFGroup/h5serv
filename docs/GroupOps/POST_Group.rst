**********************************************
POST Group
**********************************************

Description
===========
Creates a new Group.

*Note:* By default he new Group will not be linked from any other group in the domain.
A link element can be included in the request body to have an existing group link to 
the new group.
Alternatively, use the *PUT link* operation to link the new 
group.

Requests
========

Syntax
------
.. code-block:: http

    POST /groups HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
Request Parameters
------------------
This implementation of the operation does not use request parameters.

Request Headers
---------------
This implementation of the operation uses only the request headers that are common
to most requests.  See :doc:`../CommonRequestHeaders`

Request Elements
----------------
Optionally the request body can be a JSON object that has a link key with sub-keys:

id
^^
The UUID of the group the new group should be linked to.  If the UUID is not valid,
the request will fail and a new group will not be created.

name
^^^^
The name of the new link.


Responses
=========

Response Headers
----------------

This implementation of the operation uses only response headers that are common to 
most responses.  See :doc:`../CommonResponseHeaders`.

Response Elements
-----------------

On success, a JSON response will be returned with the following elements:

id
^^
The UUID of the newly created group

attributeCount
^^^^^^^^^^^^^^
The number of attributes belonging to the group.

linkCount
^^^^^^^^^
The number of links belonging to the group.

created
^^^^^^^
A timestamp giving the time the group was created in UTC (ISO-8601 format).

lastModified
^^^^^^^^^^^^
A timestamp giving the most recent time the group has been modified (i.e. attributes or 
links updated) in UTC (ISO-8601 format).

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

Create a new, un-linked Group.

.. code-block:: http

    POST /groups HTTP/1.1
    Content-Length: 0
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: testGroupPost.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 201 Created
    Content-Length: 705
    Content-Location: http://testGroupPost.test.hdfgroup.org/groups/777978c5-a078-11e4-8755-3c15c2da029e
    Server: TornadoServer/3.2.2
    Location: http://testGroupPost.test.hdfgroup.org/groups/777978c5-a078-11e4-8755-3c15c2da029e
    Date: Tue, 20 Jan 2015 07:46:38 GMT
    Content-Type: application/json
    
.. code-block:: json
  
    {
    "id": "777978c5-a078-11e4-8755-3c15c2da029e",
    "created": "2015-01-20T07:46:38Z", 
    "lastModified": "2015-01-20T07:46:38Z", 
    "attributeCount": 0, 
    "linkCount": 0,
    "hrefs": [
        {"href": "http://testGroupPost.test.hdfgroup.org/groups/777978c5-a078-11e4-8755-3c15c2da029e", "rel": "self"}, 
        {"href": "http://testGroupPost.test.hdfgroup.org/groups/777978c5-a078-11e4-8755-3c15c2da029e/links", "rel": "links"}, 
        {"href": "http://testGroupPost.test.hdfgroup.org/groups/777109b3-a078-11e4-8512-3c15c2da029e", "rel": "root"}, 
        {"href": "http://testGroupPost.test.hdfgroup.org/", "rel": "home"}, 
        {"href": "http://testGroupPost.test.hdfgroup.org/groups/777978c5-a078-11e4-8755-3c15c2da029e/attributes", "rel": "attributes"}
      ]
    }
    
Sample Request with Link
------------------------

Create a new Group, link to root (which has uuid of "36b921f3-...") as "linked_group".

.. code-block:: http

    POST /groups HTTP/1.1
    Content-Length: 79
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: testGroupPostWithLink.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
.. code-block:: json

    {
    "link": {
        "id": "36b921f3-a07a-11e4-88da-3c15c2da029e", 
        "name": "linked_group"
      }
    }
    
Sample Response with Link
-------------------------

.. code-block:: http

    HTTP/1.1 201 Created
    Content-Length: 745
    Content-Location: http://testGroupPostWithLink.test.hdfgroup.org/groups/36cbe08a-a07a-11e4-8301-3c15c2da029e
    Server: TornadoServer/3.2.2
    Location: http://testGroupPostWithLink.test.hdfgroup.org/groups/36cbe08a-a07a-11e4-8301-3c15c2da029e
    Date: Tue, 20 Jan 2015 07:59:09 GMT
    Content-Type: application/json
    
.. code-block:: json
     
    {
    "id": "36cbe08a-a07a-11e4-8301-3c15c2da029e",   
    "attributeCount": 0, 
    "linkCount": 0, 
    "created": "2015-01-20T07:59:09Z", 
    "lastModified": "2015-01-20T07:59:09Z", 
    "hrefs": [
        {"href": "http://testGroupPostWithLink.test.hdfgroup.org/groups/36cbe08a-a07a-11e4-8301-3c15c2da029e", "rel": "self"}, 
        {"href": "http://testGroupPostWithLink.test.hdfgroup.org/groups/36cbe08a-a07a-11e4-8301-3c15c2da029e/links", "rel": "links"}, 
        {"href": "http://testGroupPostWithLink.test.hdfgroup.org/groups/36b921f3-a07a-11e4-88da-3c15c2da029e", "rel": "root"}, 
        {"href": "http://testGroupPostWithLink.test.hdfgroup.org/", "rel": "home"}, 
        {"href": "http://testGroupPostWithLink.test.hdfgroup.org/groups/36cbe08a-a07a-11e4-8301-3c15c2da029e/attributes", "rel": "attributes"}
        ]
    }
    
Related Resources
=================

* :doc:`DELETE_Group`
* :doc:`GET_Links`
* :doc:`PUT_Link`
* :doc:`GET_Group`
* :doc:`GET_Groups`
 

 