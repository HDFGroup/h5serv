:tocdepth: 3

**********************************************
Datatypes
**********************************************

This resource represents the collection of all Committed (*named*) Datatypes within a domain.

*Supported Operations:*  GET, POST


GET /datatypes 
--------------

Returns data about the Datatypes collection.

*Note:* since an arbritrary number of datatypes may exist within the domain,
use the Marker and Limit parameters to iterate though large collections.  

Request
~~~~~~~

*Parameters:*

 - *Marker* [OPTIONAL]: Iteration marker.  See iteration 
 
 - *Limit*  [OPTIONAL]: Maximum number of uuids to return.  See iteration 

.. code-block:: http

    GET /datatypes HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>

Response
~~~~~~~~
.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/json
    
.. code-block:: json

   {
    "datatypes": ["<id1>", "<id2>", "<id3>", "<idN>"],

    "hrefs": [
        { "rel": "root",         "href": "http://<domain>/groups/<rootID>" },
        { "rel": "home",         "href": "http://<domain>/" },
        { "rel": "self",         "href": "http://<domain>/datatypes" }
    ]
   }

POST /datatypes 
---------------

Creates a new committed datatype. 

The body of the request must include a "type" that specifies the desired 
type of the dataset to be created. 

The type specification can be either a predefined type (e.g. "H5T_STD_I16LE"), 
or an explicitly defined type.  See Type_Specification for details of how types are 
declared.

Optionally, if a "link" key is present in the body, a link will be created from the 
given parent group with name given by link name.

*Note:*   If link options are not passed in the body of the request, the new datatype
will initially be *anonymous*, i.e. it will not be linked
to by any other group within the domain.  However it can be accessed via: GET /datatypes/<id>.


Request
~~~~~~~

*Parameters:*

.. code-block:: http

    POST /datatypes HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    Content-Type: application/json
    
.. code-block:: json

    {
    "type": "<type specification>",
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
    "type": "<type specification>",
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

   -  The request is not well formed. 
   
-  ``403 Forbidden``

   - The requestor does not have sufficient privileges for this action.
   
-  ``404 Not Found``

   - The parent group does not exist. (For POST with a provided parent_group)
   
 
