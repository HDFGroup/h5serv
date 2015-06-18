**********************************************
GET Dataset
**********************************************

Description
===========
Returns information about the dataset with the UUID given in the URI.

Requests
========

Syntax
------
.. code-block:: http

    GET /datasets/<id> HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
**<id>** is the UUID of the requested dataset.
    
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

id
^^
The UUID of the dataset object.

type
^^^^
A JSON object representing the type of the dataset.  See :doc:`../Types/index` for 
details of the type representation.

shape
^^^^^
A JSON object representing the shape of the dataset.  See :doc:`GET_DatasetShape` for
details of the shape representation.

creationProperties
^^^^^^^^^^^^^^^^^^
A JSON object that describes chunk layout, filters, fill value, and other aspects of the dataset.
See: http://hdf5-json.readthedocs.org/en/latest/bnf/dataset.html#grammar-token-dcpl for a complete 
description of fields that can be used.

attributeCount
^^^^^^^^^^^^^^
The number of attributes belonging to the dataset.

created
^^^^^^^
A timestamp giving the time the dataset was created in UTC (ISO-8601 format).

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

.. code-block:: http

    GET /datasets/c8d83759-a2c6-11e4-8713-3c15c2da029e HTTP/1.1
    host: tall.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Fri, 23 Jan 2015 06:15:33 GMT
    Content-Length: 755
    Etag: "ecbd7e52654b0a8f4ccbebac06175ce5df5f8c79"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
       
    {
    "id": "c8d83759-a2c6-11e4-8713-3c15c2da029e",
    "shape": {
        "dims": [10], 
        "class": "H5S_SIMPLE"
    },
    "type": {
        "base": "H5T_IEEE_F32BE", 
        "class": "H5T_FLOAT"
    },
    "creationProperties": {
        "allocTime": "H5D_ALLOC_TIME_LATE",
        "fillTime": "H5D_FILL_TIME_IFSET",
        "layout": {
            "class": "H5D_CONTIGUOUS"
        }
    },
    "attributeCount": 0,  
    "created": "2015-01-23T06:12:18Z", 
    "lastModified": "2015-01-23T06:12:18Z",     
    "hrefs": [
        {"href": "http://tall.test.hdfgroup.org/datasets/c8d83759-a2c6-11e4-8713-3c15c2da029e", "rel": "self"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/c8d7842b-a2c6-11e4-b4f1-3c15c2da029e", "rel": "root"}, 
        {"href": "http://tall.test.hdfgroup.org/datasets/c8d83759-a2c6-11e4-8713-3c15c2da029e/attributes", "rel": "attributes"}, 
        {"href": "http://tall.test.hdfgroup.org/datasets/c8d83759-a2c6-11e4-8713-3c15c2da029e/value", "rel": "data"}, 
        {"href": "http://tall.test.hdfgroup.org/", "rel": "home"}
      ] 
    }
    
Related Resources
=================

* :doc:`DELETE_Dataset`
* :doc:`../AttrOps/GET_Attributes`
* :doc:`GET_DatasetShape`
* :doc:`GET_DatasetType`
* :doc:`GET_Datasets`
* :doc:`GET_Value`
* :doc:`POST_Value`
* :doc:`PUT_Value`
 

 