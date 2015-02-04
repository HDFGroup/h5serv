**********************************************
GET Attributes
**********************************************

Description
===========
Gets all the attributes of a dataset, group, or committed datatype.
For each attribute the request returns the attributes name, type, and shape.  To get 
the attribute data use :doc:`GET_Attribute`.

Requests
========

Syntax
------

To get the attributes of a group:

.. code-block:: http

    GET /groups/<id>/attributes HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
To get the attributes of a dataset:

.. code-block:: http

    GET /datasets/<id>/attributes HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
To get the attributes of a datatype:

.. code-block:: http

    GET /datatypes/<id>/attributes HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
 
where:    
    
* *<id>* is the UUID of the dataset/group/committed datatype
    
Request Parameters
------------------
This implementation of the operation uses the following request parameters (both 
optional):

Limit
^^^^^
If provided, a positive integer value specifying the maximum number of attributes to return.

Marker
^^^^^^
If provided, a string value indicating that only attributes that occur after the
marker value will be returned.
*Note:* the marker expression should be url-encoded.

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


attributes
^^^^^^^^^^

An array of JSON objects with an element for each returned attribute.
Each element will have keys: name, type, shape, created, and lastModified.  See 
:doc:`GET_Attribute` for a description of these keys.

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

Get attributes of a group with UUID: "45a882e1-...".

.. code-block:: http

    GET /groups/1a956e54-abf6-11e4-b878-3c15c2da029e/attributes HTTP/1.1
    host: tall.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Wed, 04 Feb 2015 00:49:28 GMT
    Content-Length: 807
    Etag: "7cbeefcf8d9997a8865bdea3bf2d541a14e9bf71"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json

    {
    "attributes": [
        {
        "name": "attr1", 
        "type": {
            "base": "H5T_STD_I8LE", 
            "class": "H5T_INTEGER"
            },
        "shape": {
            "dims": [10], 
            "class": "H5S_SIMPLE"
            },
        "created": "2015-02-03T22:40:09Z",
        "lastModified": "2015-02-03T22:40:09Z", 
        },
        "name": "attr2", 
         "type": {
            "base": "H5T_STD_I32BE", 
            "class": "H5T_INTEGER"
            }, 
        "shape": {
            "dims": [2, 2], 
            "class": "H5S_SIMPLE"
            }, 
        "created": "2015-02-03T22:40:09Z",
        "lastModified": "2015-02-03T22:40:09Z",    
        }
      ], 
      "hrefs": [
        {"href": "http://tall.test.hdfgroup.org/groups/1a956e54-abf6-11e4-b878-3c15c2da029e/attributes", "rel": "self"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/1a956e54-abf6-11e4-b878-3c15c2da029e", "rel": "owner"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/1a956e54-abf6-11e4-b878-3c15c2da029e", "rel": "root"}, 
        {"href": "http://tall.test.hdfgroup.org/", "rel": "home"}
      ]
    }
    

Sample Request - get Batch
---------------------------

Get 5 the five attributes that occur after attribute "a0004" from a of a group with UUID: 
"45a882e1-...".

.. code-block:: http

    GET /groups/4cecd4dc-ac0a-11e4-af59-3c15c2da029e/attributes?Marker=a0004&Limit=5 HTTP/1.1
    host: attr1k.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response - get Batch
---------------------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Wed, 04 Feb 2015 01:08:16 GMT
    Content-Length: 1767
    Etag: "9483f4356e08d12b719aa64ece09e659b05adaf2"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
 
    {
    "attributes": [
        {
        "name": "a0005", 
        "type": {"cset": "H5T_CSET_ASCII", "order": "H5T_ORDER_NONE", "class": "H5T_STRING", "strpad": "H5T_STR_NULLTERM", "strsize": "H5T_VARIABLE"}, 
        "shape": {"class": "H5S_SCALAR"}, 
        "created": "2015-02-03T22:40:09Z",
        "lastModified": "2015-02-03T22:40:09Z"
        }, {
        "name": "a0006", 
        "type": {"cset": "H5T_CSET_ASCII", "order": "H5T_ORDER_NONE", "class": "H5T_STRING", "strpad": "H5T_STR_NULLTERM", "strsize": "H5T_VARIABLE"}, 
        "shape": {"class": "H5S_SCALAR"}, 
        "created": "2015-02-03T22:40:09Z",
        "lastModified": "2015-02-03T22:40:09Z"
        }, {
        "name": "a0007",
        "type": {"cset": "H5T_CSET_ASCII", "order": "H5T_ORDER_NONE", "class": "H5T_STRING", "strpad": "H5T_STR_NULLTERM", "strsize": "H5T_VARIABLE"}, 
        "shape": {"class": "H5S_SCALAR"}, 
        "created": "2015-02-03T22:40:09Z",
        "lastModified": "2015-02-03T22:40:09Z"
        }, {
        "name": "a0008", 
        "type": {"cset": "H5T_CSET_ASCII", "order": "H5T_ORDER_NONE", "class": "H5T_STRING", "strpad": "H5T_STR_NULLTERM", "strsize": "H5T_VARIABLE"}, 
        "shape": {"class": "H5S_SCALAR"}, 
        "created": "2015-02-03T22:40:09Z",
        "lastModified": "2015-02-03T22:40:09Z"
        }, {
        "name": "a0009", 
        "type": {"cset": "H5T_CSET_ASCII", "order": "H5T_ORDER_NONE", "class": "H5T_STRING", "strpad": "H5T_STR_NULLTERM", "strsize": "H5T_VARIABLE"}, 
        "shape": {"class": "H5S_SCALAR"}, 
        "created": "2015-02-03T22:40:09Z",
        "lastModified": "2015-02-03T22:40:09Z"
        }
      ], 
    "hrefs": [
        {"href": "http://attr1k.test.hdfgroup.org/groups/4cecd4dc-ac0a-11e4-af59-3c15c2da029e/attributes", "rel": "self"}, 
        {"href": "http://attr1k.test.hdfgroup.org/groups/4cecd4dc-ac0a-11e4-af59-3c15c2da029e", "rel": "owner"}, 
        {"href": "http://attr1k.test.hdfgroup.org/groups/4cecd4dc-ac0a-11e4-af59-3c15c2da029e", "rel": "root"}, 
        {"href": "http://attr1k.test.hdfgroup.org/", "rel": "home"}
      ]
    }
    
Related Resources
=================

* :doc:`DELETE_Attribute`
* :doc:`GET_Attributes`
* :doc:`../DatasetOps/GET_Dataset`
* :doc:`../DatatypeOps/GET_Datatype`
* :doc:`../GroupOps/GET_Group`
* :doc:`PUT_Attribute`
 

 