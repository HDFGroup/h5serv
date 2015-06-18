**********************************************
POST Dataset
**********************************************

Description
===========
Creates a new Dataset.

Requests
========

Syntax
------
.. code-block:: http

    POST /datasets HTTP/1.1
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
The request body must include a JSON object with a "type" key.  Optionally "shape", 
"maxdims", and "link" keys can be provided.

type
^^^^
Either a string that is one of the predefined type values, a uuid of a committed type,
or a JSON object describing the type.  See :doc:`../Types/index` for details of the
type specification.

shape
^^^^^^
Either a string with the value ``H5S_NULL`` or an
integer array describing the initial dimensions of the dataset.  If shape is not
provided, a scalar dataset will be created.
If the shape value of ``H5S_NULL`` is specified a dataset with a null dataspace will be 
created.  A null
dataset has attributes and a type, but will not be able to store any values.

maxdims
^^^^^^^
An integer array describing the maximum extent of each dimension (or 0 for unlimited
dimensions).  If maxdims is not provided that resulting dataset will be non-extensible.
Not valid to include if ``H5S_NULL`` is specified for the shape.

creationProperties
^^^^^^^^^^^^^^^^^^
A JSON object that can specify chunk layout, filters, fill value, and other aspects of the dataset.
See: http://hdf5-json.readthedocs.org/en/latest/bnf/dataset.html#grammar-token-dcpl for a complete 
description of fields that can be used.

If creationProperties is not provided, default values will be used

link["id"]
^^^^^^^^^^
The UUID of the group the new group should be linked to.  If the UUID is not valid,
the request will fail and a new group will not be created.

link["name"]
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
The UUID of the newly created dataset.

attributeCount
^^^^^^^^^^^^^^
The number of attributes belonging to the dataset.

created
^^^^^^^
A timestamp giving the time the dataset was created in UTC (ISO-8601 format).

lastModified
^^^^^^^^^^^^
A timestamp giving the most recent time the dataset has been modified (i.e. attributes or 
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

Create a one-dimensional dataset with 10 floating point elements.

.. code-block:: http

    POST /datasets HTTP/1.1
    Content-Length: 39
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: newdset.datasettest.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
.. code-block:: json

    {
    "shape": 10, 
    "type": "H5T_IEEE_F32LE"
    }
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 201 Created
    Date: Thu, 29 Jan 2015 06:14:02 GMT
    Content-Length: 651
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
   
    {
    "id": "0568d8c5-a77e-11e4-9f7a-3c15c2da029e", 
    "attributeCount": 0, 
    "created": "2015-01-29T06:14:02Z",
    "lastModified": "2015-01-29T06:14:02Z",
    "hrefs": [
        {"href": "http://newdset.datasettest.test.hdfgroup.org/datasets/0568d8c5-a77e-11e4-9f7a-3c15c2da029e", "rel": "self"}, 
        {"href": "http://newdset.datasettest.test.hdfgroup.org/groups/055fe7de-a77e-11e4-bbe9-3c15c2da029e", "rel": "root"}, 
        {"href": "http://newdset.datasettest.test.hdfgroup.org/datasets/0568d8c5-a77e-11e4-9f7a-3c15c2da029e/attributes", "rel": "attributes"}, 
        {"href": "http://newdset.datasettest.test.hdfgroup.org/datasets/0568d8c5-a77e-11e4-9f7a-3c15c2da029e/value", "rel": "value"}
      ]
    }
    
Sample Request with Link
------------------------

Create a dataset with 10 variable length string elements.  Create link in group: 
"5e441dcf-..." with name: "linked_dset".

.. code-block:: http

    POST /datasets HTTP/1.1
    Content-Length: 235
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: newdsetwithlink.datasettest.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
.. code-block:: json

    {
    "type": {
        "class": "H5T_STRING",
        "strsize": "H5T_VARIABLE", 
        "cset": "H5T_CSET_ASCII", 
        "order": "H5T_ORDER_NONE", 
        "strpad": "H5T_STR_NULLTERM"
    },
    "shape": 10, 
    "link": {
        "id": "5e441dcf-a782-11e4-bd6b-3c15c2da029e", 
        "name": "linked_dset"
      }
    
    }
    
Sample Response with Link
-------------------------

.. code-block:: http

    HTTP/1.1 201 Created
    Date: Thu, 29 Jan 2015 06:45:09 GMT
    Content-Length: 683
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
   
    
    {
    "id": "5e579297-a782-11e4-93f9-3c15c2da029e",
    "attributeCount": 0,
    "created": "2015-01-29T06:45:09Z",
    "lastModified": "2015-01-29T06:45:09Z",
    "hrefs": [
        {"href": "http://newdsetwithlink.datasettest.test.hdfgroup.org/datasets/5e579297-a782-11e4-93f9-3c15c2da029e", "rel": "self"}, 
        {"href": "http://newdsetwithlink.datasettest.test.hdfgroup.org/groups/5e441dcf-a782-11e4-bd6b-3c15c2da029e", "rel": "root"}, 
        {"href": "http://newdsetwithlink.datasettest.test.hdfgroup.org/datasets/5e579297-a782-11e4-93f9-3c15c2da029e/attributes", "rel": "attributes"}, 
        {"href": "http://newdsetwithlink.datasettest.test.hdfgroup.org/datasets/5e579297-a782-11e4-93f9-3c15c2da029e/value", "rel": "value"}
      ]
    }
    
Sample Request - Resizable Dataset
----------------------------------

  Create a one-dimensional dataset with 10 elements, but extendable to an unlimited
  dimension.
  
.. code-block:: http

    POST /datasets HTTP/1.1
    Content-Length: 54
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: resizabledset.datasettest.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
.. code-block:: json

    {
    "type": "H5T_IEEE_F32LE",
    "shape": 10,
    "maxdims": 0
    }
    
Sample Response - Resizable Dataset
-----------------------------------

.. code-block:: http

    HTTP/1.1 201 Created
    Date: Thu, 29 Jan 2015 08:28:19 GMT
    Content-Length: 675
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
     
   {
   "id": "c79933ab-a790-11e4-b36d-3c15c2da029e", 
   "attributeCount": 0, 
   "created": "2015-01-29T08:28:19Z",
   "lastModified": "2015-01-29T08:28:19Z", 
   "hrefs": [
        {"href": "http://resizabledset.datasettest.test.hdfgroup.org/datasets/c79933ab-a790-11e4-b36d-3c15c2da029e", "rel": "self"}, 
        {"href": "http://resizabledset.datasettest.test.hdfgroup.org/groups/c7759c11-a790-11e4-ae03-3c15c2da029e", "rel": "root"}, 
        {"href": "http://resizabledset.datasettest.test.hdfgroup.org/datasets/c79933ab-a790-11e4-b36d-3c15c2da029e/attributes", "rel": "attributes"}, 
        {"href": "http://resizabledset.datasettest.test.hdfgroup.org/datasets/c79933ab-a790-11e4-b36d-3c15c2da029e/value", "rel": "value"}
      ]
    }
    
Sample Request - Committed Type
----------------------------------

  Create a two-dimensional dataset which uses a committed type with uuid: 
  
.. code-block:: http

    POST /datasets HTTP/1.1
    Content-Length: 67
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: committedtype.datasettest.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
.. code-block:: json

    {
    "type": "accd0b1e-a792-11e4-bada-3c15c2da029e",
    "shape": [10, 10]
    }
    
Sample Response - Committed Type
-----------------------------------

.. code-block:: http

    HTTP/1.1 201 Created
    Date: Thu, 29 Jan 2015 08:41:53 GMT
    Content-Length: 675
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
     
    {
    "id": "ace8cdca-a792-11e4-ad88-3c15c2da029e", 
    "attributeCount": 0, 
    "created": "2015-01-29T08:41:53Z",
    "lastModified": "2015-01-29T08:41:53Z",
    "hrefs": [
        {"href": "http://committedtype.datasettest.test.hdfgroup.org/datasets/ace8cdca-a792-11e4-ad88-3c15c2da029e", "rel": "self"}, 
        {"href": "http://committedtype.datasettest.test.hdfgroup.org/groups/acc4d37d-a792-11e4-b326-3c15c2da029e", "rel": "root"}, 
        {"href": "http://committedtype.datasettest.test.hdfgroup.org/datasets/ace8cdca-a792-11e4-ad88-3c15c2da029e/attributes", "rel": "attributes"}, 
        {"href": "http://committedtype.datasettest.test.hdfgroup.org/datasets/ace8cdca-a792-11e4-ad88-3c15c2da029e/value", "rel": "value"}
      ]
    }
    
Sample Request - SZIP Compression with chunking
-----------------------------------------------

.. code-block:: http

    POST /datasets HTTP/1.1
    Content-Length: 67
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    host: szip.datasettest.test.hdfgroup.org
    Accept: */*
    Accept-Encoding: gzip, deflate
    
.. code-block:: json

    {
    "creationProperties": {
        "filters": [
            {
                "bitsPerPixel": 8,
                "coding": "H5_SZIP_EC_OPTION_MASK",
                "id": 4,
                "pixelsPerBlock": 32,
                "pixelsPerScanline": 100
            }
        ],
        "layout": {
            "class": "H5D_CHUNKED",
            "dims": [
                100,
                100
            ]
        }
    },
    "shape": [
        1000,
        1000
    ],
    "type": "H5T_IEEE_F32LE"
   }
   
Sample Response - SZIP Compression with chunking
------------------------------------------------

.. code-block:: http

    HTTP/1.1 201 Created
    Date: Thu, 18 Jun 2015 08:41:53 GMT
    Content-Length: 975
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json

    {
    "id": "ad283c05-158c-11e5-bd67-3c15c2da029e",
    "attributeCount": 0,
    "created": "2015-06-18T07:36:04Z",
    "lastModified": "2015-06-18T07:36:04Z",
    "hrefs": [
        {
            "href": "http://newdset_szip.datasettest.test.hdfgroup.org/datasets/ad283c05-158c-11e5-bd67-3c15c2da029e",
            "rel": "self"
        },
        {
            "href": "http://newdset_szip.datasettest.test.hdfgroup.org/groups/ad2746d4-158c-11e5-a083-3c15c2da029e",
            "rel": "root"
        },
        {
            "href": "http://newdset_szip.datasettest.test.hdfgroup.org/datasets/ad283c05-158c-11e5-bd67-3c15c2da029e/attributes",
            "rel": "attributes"
        },
        {
            "href": "http://newdset_szip.datasettest.test.hdfgroup.org/datasets/ad283c05-158c-11e5-bd67-3c15c2da029e/value",
            "rel": "value"
        }
    ]
    }


    
Related Resources
=================

* :doc:`GET_Dataset`
* :doc:`GET_Datasets`
* :doc:`GET_Value`
* :doc:`POST_Value`
* :doc:`PUT_Value`
 

 