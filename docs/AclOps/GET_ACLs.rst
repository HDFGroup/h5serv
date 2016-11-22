**********************************************
GET ACLs
**********************************************

Description
===========
Returns access information for all users defined in the ACL (Access Control List) 
for the object with the UUID provided in the URI.

Requests
========

Syntax
------

To get the ACL for a domain:

.. code-block:: http

    GET /acls HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>

To get the ACL for a group:

.. code-block:: http

    GET /groups/<id>/acls HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    

To get the ACL for a dataset:

.. code-block:: http

    GET /datasets/<id>/acls HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    

To get the ACL for a committed datatype:

.. code-block:: http

    GET /datatypes/<id>/acls HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>

where:
    
* <id> is the UUID of the requested dataset/group/committed datatype
    
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


acls
^^^^
A JSON list that contains one element for each user specified in the ACL.
The elements will be JSON object that describe the users acces permisions.  
Subkeys of the element are are:

userName: the userid of the user ('default' for the default access)

create: A boolean flag that indicated if the user is authorized to create new resources

delete: A boolean flag that indicated if the user is authorized to delete resources

read: A boolean flag that indicated if the user is authorized to read (GET) resources

update: A boolean flag that indicated if the user is authorized to update resources

readACL: A boolean flag that indicated if the user is authorized to read the object's ACL

updateACL: A boolean flag that indicated if the user is authorized to update the object's ACL

 
hrefs
^^^^^
An array of hypertext links to related resources.  See :doc:`../Hypermedia`.

Special Errors
--------------

The implementation of the operation does not return special errors.  For general 
information on standard error codes, see :doc:`../CommonErrorResponses`.

Examples
========

Sample Request
--------------

.. code-block:: http

    GET /groups/052dcbbd-9d33-11e4-86ce-3c15c2da029e/acls  HTTP/1.1
    host: tall.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Fri, 16 Jan 2015 20:06:08 GMT
    Content-Length: 660
    Etag: "2c410d1c469786f25ed0075571a8e7a3f313cec1"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json

    {
    "acls": [
        {
            "create": true,
            "delete": true,
            "read": true,
            "readACL": true,
            "update": true,
            "updateACL": true,
            "userName": "test_user2"
        },
        {
            "create": false,
            "delete": false,
            "read": true,
            "readACL": false,
            "update": false,
            "updateACL": false,
            "userName": "test_user1"
        },
        {
            "create": false,
            "delete": false,
            "read": false,
            "readACL": false,
            "update": false,
            "updateACL": false,
            "userName": "default"
        }
    ],
    "hrefs": [
        {
            "href": "http://tall_acl.test.hdfgroup.org/groups/eb8f6959-8775-11e5-96b6-3c15c2da029e/acls",
            "rel": "self"
        },
        {
            "href": "http://tall_acl.test.hdfgroup.org/groups/eb8f6959-8775-11e5-96b6-3c15c2da029e",
            "rel": "root"
        },
        {
            "href": "http://tall_acl.test.hdfgroup.org/",
            "rel": "home"
        },
        {
            "href": "http://tall_acl.test.hdfgroup.org/groups/eb8f6959-8775-11e5-96b6-3c15c2da029e",
            "rel": "owner"
        }
    ]
    
Related Resources
=================

* :doc:`PUT_ACL`
* :doc:`GET_ACL`

 

 