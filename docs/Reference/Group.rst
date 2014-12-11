###########
Group
###########

This resource represents an HDF5 group - a group can contain any number of attributes 
(see attributes), as well as any number of links (see links).  

*Supported Operations:*  GET, DELETE

 

GET /groups/<id> 
-----------------

Returns information about the group with the specified uuid

Request
~~~~~~~

.. code-block:: http

    GET /groups/<id> HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>

Response
~~~~~~~~
.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/json
    
.. code-block:: json

   {
    "id": <id>,

    "created": <utctime>,
    "lastModified": <utctime>,

    "attributeCount": <non_negative_integer>,
    "linkCount": <non_negative_integer>,

    "hrefs": [
        { "rel": "attributes",   "href": "http://<domain>/groups/<id>/attributes" },
        { "rel": "links",        "href": "http://<domain>/groups/<id>/links" },
        { "rel": "root",         "href": "http://<domain>/groups/<rootID>" },
        { "rel": "home",         "href": "http://<domain>/" },
        { "rel": "self",         "href": "http://<domain>/groups/<id>" }
    ]
    }

POST /groups 
-------------

Creates a new group. 

*Note:*   The new group group will initially be *anonymous*, i.e. it will not be linked
to by any other group within the domain.  However it can be accessed via: GET /groups/<id>.


Request
~~~~~~~

.. code-block:: http

    POST /groups HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    Content-Type: application/json
 

Response
~~~~~~~~
.. code-block:: http

    HTTP/1.1 201 Created
    Content-Type: application/json
    
.. code-block:: json

    {
    "created": <utctime>,
    "lastModified": <utctime>,

    "groupCount": <non_negative_integer>,
    "datasetCount": <non_negative_integer>,
    "typeCount": <non_negative_integer>,
    "root": <root_uuid>,

    "refs": [
      { "rel": "self",      "href": "http://<domain>/" } ,
      { "rel": "database",  "href": "http://<domain>/datasets" } ,
      { "rel": "groupbase", "href": "http://<domain>/groups" } ,
      { "rel": "typebase",  "href": "http://<domain>/datatypes" } ,
      { "rel": "root",      "href": "http://<domain>/groups/{root_uuid}" }
    ]
    }
    
DELETE /groups/<id>
-------------------

Deletes the group with UUID of <id>.  All hardlinks that point to this this group will also
be removed.

*WARNING:* all attributes and links of the group will be removed.  Groups and Datasets
that are referenced by this group's links will not be removed however.

*NOTE:*  The Root Group can not be deleted (except by deleting the domain).  Attempting
to delete the Root Group will return a status of 403 - Forbidden. 

Request
~~~~~~~

.. code-block:: http

    DELETE /groups/<id> HTTP/1.1
    Content-Length: 0
    host: DOMAIN
    Authorization: <authorization_string>
    Content-Type: application/json  

Response
~~~~~~~~
.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/json
    
.. code-block:: json

    {
    "hrefs": [
        { "rel": "root", "href": "http://<domain>/groups/<root ID>" } ,
        { "rel": "self", "href": "http://<domain>/groups" },
        { "rel": "home", "href": "http://<domain>/" }      
        ]
    }


Errors
------

In addition to the general errors, requests to the domain resource may
return the following errors:

-  ``400 Bad Request``

   -  The request is badly formed.
   
-  ``403 Forbidden``

   - The requestor does not have sufficient privileges for this action.
   
- ``404 Not Found``

   - The domain or group id could not be found
   
   - The domain name already exists
   
- ``410 Gone``

   - The resource has been removed previously
