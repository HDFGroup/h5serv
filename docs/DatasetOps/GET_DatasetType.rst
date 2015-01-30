**********************************************
GET Type
**********************************************

Description
===========
Gets Type Information for a dataset.

Requests
========

Syntax
------
.. code-block:: http

    GET /datasets/<id>/type HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
*<id>* is the UUID of the dataset the type information is requested for.
    
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

type
^^^^
A JSON object representing the type definition for the dataset. See :doc:`../Types/index`
for information on how different types are represented.

hrefs
^^^^^
An array of links to related resources.  See :doc:`../Hypermedia`.

Special Errors
--------------

The implementation of the operation does not return special errors.  For general 
information on standard error codes, see :doc:`../CommonErrorResponses`.

Examples
========

Sample Request - Predefined Type
--------------------------------

.. code-block:: http

    GET /datasets/ba06ce68-a6b5-11e4-8ed3-3c15c2da029e/type HTTP/1.1
    host: scalar.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response - Predefined Type
---------------------------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Wed, 28 Jan 2015 06:20:16 GMT
    Content-Length: 519
    Etag: "802b160bf786596a9cb9f6d5cd6faa4fe1127e8c"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json

    {
    "type": {
        "class": "H5T_INTEGER", 
        "order": "H5T_ORDER_LE", 
        "base_size": 4, 
        "base": "H5T_STD_I32LE", 
        "size": 4
    }, 
    "hrefs": [
        {"href": "http://scalar.test.hdfgroup.org/datasets/ba06ce68-a6b5-11e4-8ed3-3c15c2da029e/type", "rel": "self"}, 
        {"href": "http://scalar.test.hdfgroup.org/datasets/ba06ce68-a6b5-11e4-8ed3-3c15c2da029e", "rel": "owner"}, 
        {"href": "http://scalar.test.hdfgroup.org/groups/ba06992e-a6b5-11e4-9ba5-3c15c2da029e", "rel": "root"}
      ] 
    }
    
Sample Request - Compound Type
--------------------------------

.. code-block:: http

    GET /datasets/b9edddd7-a6b5-11e4-9afd-3c15c2da029e/type HTTP/1.1
    host: compound.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response - Compound Type
--------------------------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Wed, 28 Jan 2015 06:20:16 GMT
    Content-Length: 1199
    Etag: "1f97eac24aa18d3c462a2f2797c4782a1f2a0aa2"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json

    {
    "type": {
        "class": "H5T_COMPOUND",
        "fields": [
            {
            "type": {
                "order": "H5T_ORDER_LE", 
                "base_size": 8, 
                "class": "H5T_INTEGER", 
                "base": "H5T_STD_I64LE", 
                "size": 8}, 
            "name": "date"
            }, {
            "type": {
                "strpad": "H5T_STR_NULLPAD", 
                "base_size": 6, "order": "H5T_ORDER_NONE", 
                "cset": "H5T_CSET_ASCII", 
                "strsize": 6, 
                "class": "H5T_STRING", 
                "size": 6}, 
            "name": "time"
            }, {
            "type": {
                "order": "H5T_ORDER_LE", 
                "base_size": 8, 
                "class": "H5T_INTEGER", 
                "base": "H5T_STD_I64LE", 
                "size": 8}, 
            "name": "temp"
            }, {
            "type": {
                "order": "H5T_ORDER_LE", 
                "base_size": 8, 
                "class": "H5T_FLOAT", 
                "base": "H5T_IEEE_F64LE", 
                "size": 8}, 
            "name": "pressure"
            }, {
                "type": {
                    "strpad": "H5T_STR_NULLPAD", 
                    "base_size": 6, 
                    "order": "H5T_ORDER_NONE", 
                    "cset": "H5T_CSET_ASCII", 
                    "strsize": 6, 
                    "class": "H5T_STRING", 
                    "size": 6}, 
                "name": "wind"}
            ] 
        }, 
        "hrefs": [
            {"href": "http://compound.test.hdfgroup.org/datasets/b9edddd7-a6b5-11e4-9afd-3c15c2da029e/type", "rel": "self"}, 
            {"href": "http://compound.test.hdfgroup.org/datasets/b9edddd7-a6b5-11e4-9afd-3c15c2da029e", "rel": "owner"}, 
            {"href": "http://compound.test.hdfgroup.org/groups/b9eda805-a6b5-11e4-aa52-3c15c2da029e", "rel": "root"}
          ] 
        }
    
Related Resources
=================

* :doc:`GET_Dataset`
* :doc:`GET_DatasetShape`
* :doc:`POST_Dataset`
 

 