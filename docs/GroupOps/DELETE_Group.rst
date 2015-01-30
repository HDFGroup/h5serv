**********************************************
DELETE Group
**********************************************

Description
===========
The implementation of the DELETE operation deletes the group with the UUID given in the
URI.  All attributes and links of the group will also be deleted.  In addition any 
links from other groups **TO** the deleted group will be removed.

*Note:* Groups, datatypes, and datasets that are referenced by the group's links will 
**not** be deleted.  Use the DELETE operation for those objects to remove.

Requests
========

Syntax
------
.. code-block:: http

    DELETE /groups/<id> HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
 
*<id>* is the UUID of the group to be deleted.
    
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

    DELETE /groups/45a882e1-9d01-11e4-8acf-3c15c2da029e HTTP/1.1
    Host: testGroupDelete.test.hdfgroup.org
    Authorization: authorization_string
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Thu, 15 Jan 2015 21:55:51 GMT
    Content-Length: 270
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json

    
    {
    "hrefs": [
        {"href": "http://testGroupDelete.test.hdfgroup.org/groups", "rel": "self"}, 
        {"href": "http://testGroupDelete.test.hdfgroup.org/groups/45a06719-9d01-11e4-9b1c-3c15c2da029e", "rel": "root"}, 
        {"href": "http://testGroupDelete.test.hdfgroup.org/", "rel": "home"}
    ]
    }
    
Related Resources
=================

* :doc:`POST_Group`
* :doc:`GET_Group`
 

 