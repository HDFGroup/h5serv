**********************************************
POST Datatype
**********************************************

Description
===========
Creates a new committed datatype.

Requests
========

Syntax
------
.. code-block:: http

    POST /datatypes  HTTP/1.1
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
The request body must be a JSON object with a 'type' link key as described below.
Optionally, the request body can include a 'link' key that describes how the new
committed datatype will be linked.

type
^^^^
The value of the type key can either be one of the predefined type strings 
(see predefined types), or a JSON representation of a type. (see :doc:`../Types/index`).

link
^^^^
If present, the link value must include the following subkeys:

link['id']
^^^^^^^^^^
The UUID of the group the new datatype should be linked from.  If the UUID is not valid,
the request will fail and a new datatype will not be created.

link['name']
^^^^^^^^^^^^
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

The UUID of the newly created datatype object.

attributeCount
^^^^^^^^^^^^^^
The number of attributes belonging to the datatype.

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

Create a new committed datatype using the "H5T_IEEE_F32LE" (32-bit float) predefined type.

.. code-block:: http

    POST /datatypes HTTP/1.1
    Content-Length: 26
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: newdtype.datatypetest.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
.. code-block:: json

    {
    "type": "H5T_IEEE_F32LE"
    }
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 201 Created
    Date: Thu, 22 Jan 2015 19:06:17 GMT
    Content-Length: 533
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
  
    {
    "id": "be08d40c-a269-11e4-84db-3c15c2da029e", 
    "attributeCount": 0, 
    "created": "2015-01-22T19:06:17Z",
    "lastModified": "2015-01-22T19:06:17Z",
    "hrefs": [
        {"href": "http://newdtype.datatypetest.test.hdfgroup.org/datatypes/be08d40c-a269-11e4-84db-3c15c2da029e", "rel": "self"}, 
        {"href": "http://newdtype.datatypetest.test.hdfgroup.org/groups/be00807d-a269-11e4-8d9c-3c15c2da029e", "rel": "root"}, 
        {"href": "http://newdtype.datatypetest.test.hdfgroup.org/datatypes/be08d40c-a269-11e4-84db-3c15c2da029e/attributes", "rel": "attributes"}
        ]
    }
    
    
Sample Request with Link
------------------------

Create a new committed datatype and link to root as "linked_dtype".

.. code-block:: http

    POST /datatypes HTTP/1.1
    Content-Length: 106
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: newlinkedtype.datatypetest.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
.. code-block:: json

    {
    "type": "H5T_IEEE_F64LE",
    "link": {
        "id": "76b0bbf8-a26c-11e4-8d4c-3c15c2da029e", 
        "name": "linked_dtype"
      }
    }
    
Sample Response with Link
-------------------------

.. code-block:: http

    HTTP/1.1 201 Created
    Date: Thu, 22 Jan 2015 19:25:46 GMT
    Content-Length: 548
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json

    {
    "id": "76c3c33a-a26c-11e4-998c-3c15c2da029e", 
    "attributeCount": 0, 
    "created": "2015-01-22T19:25:46Z",
    "lastModified": "2015-01-22T19:25:46Z", 
    "hrefs": [
        {"href": "http://newlinkedtype.datatypetest.test.hdfgroup.org/datatypes/76c3c33a-a26c-11e4-998c-3c15c2da029e", "rel": "self"}, 
        {"href": "http://newlinkedtype.datatypetest.test.hdfgroup.org/groups/76b0bbf8-a26c-11e4-8d4c-3c15c2da029e", "rel": "root"}, 
        {"href": "http://newlinkedtype.datatypetest.test.hdfgroup.org/datatypes/76c3c33a-a26c-11e4-998c-3c15c2da029e/attributes", "rel": "attributes"}
      ]
    }
    
Related Resources
=================

* :doc:`DELETE_Datatype`
* :doc:`GET_Datatype`
* :doc:`GET_Datatypes`
* :doc:`../DatasetOps/POST_Dataset`
* :doc:`../AttrOps/PUT_Attribute`
 

 