:tocdepth: 3

**********************************************
Datasets
**********************************************

This resource represents the collection of all Datasets within a domain.

*Supported Operations:*  GET, POST


GET /datasets 
-------------

Returns data about the Datasets collection.

*Note:* since an arbritrary number of datasets may exist within the domain,
use the Marker and Limit parameters to iterate though large collections.  

Request
~~~~~~~

*Parameters:*

 - *Marker* [OPTIONAL]: Iteration marker.  See iteration 
 
 - *Limit*  [OPTIONAL]: Maximum number of uuids to return.  See iteration 

.. code-block:: http

    GET /datasets HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>

Response
~~~~~~~~
.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/json
    
.. code-block:: json

   {
    "datasets": ["<id1>", "<id2>", "<id3>", "<idN>"],

    "hrefs": [
        { "rel": "root",         "href": "http://<domain>/groups/<rootID>" },
        { "rel": "home",         "href": "http://<domain>/" },
        { "rel": "self",         "href": "http://<domain>/datasets" }
    ]
   }

POST /datasets 
--------------

Creates a new dataset. 

The body of the request must include a "type" that specifies the desired 
type of the dataset to be created. 

The type specification can be one of: a predefined type, a reference to a type object,
or an explicitly defined type.  See Type_Specification for details of how types are 
declared.

An optional shape key can either be (if provided)
a non-negative integer (for a one-dimensional dataset),
or an array of non-negative integers (for a multi-dimensional dataset).  If any of
the dimensions are zero, no space will be allocated for the dataset and it must be 
re-shaped (using the PUT shape operation) before values can be read or written to it.

If a shape key is not present in the body of the request, the dataset will be created
as a *scalar* dataset - i.e. a zero-dimensional dataset that can store only one value.

Optionally a maxdims key can be provided to create an *extensible* dataset.  Maxdims may
either a non-negative-integer (if the dataset is one-dimensional), or an array of  
non-negative integers where the number of elements is equal to the number of dimensions of
the dataset.  For any positive value, the array may be later extended in that dimension 
up to the given value.  For zero values, the dimension may be extended to any value.
See PUT shape for information on re-sizing datasets.

Optionally, if a "link" key is present in the body, a link will be created from the 
given parent group with name given by link name.

*Note:*   If link options are not passed in the body of the request, the new dataset
will initially be *anonymous*, i.e. it will not be linked
to by any other group within the domain.  However it can be accessed via: GET /datasets/<id>.


Request
~~~~~~~

*Parameters:*

.. code-block:: http

    POST /datasets HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    Content-Type: application/json
    
.. code-block:: json

    {
    "type": "<type specification>",
    "shape": ["dim1", "dim2", "dimn"],
    "maxdims": ["dim1", "dim2", "dimn"],
    "link": {
       "id": "<parent_id>",
       "name": "<link_name>"
    }
 

Response
~~~~~~~~
.. code-block:: http

    HTTP/1.1 201 Created
    Content-Type: application/json
    
.. code-block:: json

    {
    "id": "<id>",
    "created": "<utctime>",
    "lastModified": "<utctime>",

    "attributeCount": "<non_negative_integer>",

    "refs": [
       { "rel": "attributes",  "href": "http://<domain>/datasets/<id>/attributes" },
       { "rel": "links",       "href": "http://<domain>/datasets/<id>/links" },
       { "rel": "root",        "href": "http://<domain>/datasets/<rootID>" },
       { "rel": "home",        "href": "http://<domain>/" },
       { "rel": "self",        "href": "http://<domain>/datasets/<id>" }
    ]
  


Errors
------

In addition to the general errors, requests to the datasets resource may
return the following errors:

-  ``400 Bad Request``

   -  The request is not well formed. E.g. POST is given a dims key with negative values.
   
-  ``403 Forbidden``

   - The requestor does not have sufficient privileges for this action.
   
-  ``404 Not Found``

   - The parent group does not exist. (For POST with a provided parent_group)
   
 
