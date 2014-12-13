#################
Groups Collection
#################

This resource is a collection of all Groups within a domain.

*Supported Operations:*  GET, POST


GET /groups 
------------

Returns data about the Group collection.

*Note:* since an arbritrary number of groups may exist within the domain,
use the Marker and Limit parameters to iterate though large collections.  To get
the number of groups in the domain, use:
*GET /* and inspect that groupCount value.

Request
~~~~~~~

*Parameters:*

 - *Marker:* Iteration marker.  See iteration
 
 - *Limit:* Maximum number of uuids to return.  See iteration

.. code-block:: http

    GET /groups HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>

Response
~~~~~~~~
.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/json
    
.. code-block:: json

   {
    "groups": [<id1>, <id2>, <id3>, ..., <idN>],

    "hrefs": [
        { "rel": "root",         "href": "http://<domain>/groups/<rootID>" },
        { "rel": "home",         "href": "http://<domain>/" },
        { "rel": "self",         "href": "http://<domain>/groups" }
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
  


Errors
------

In addition to the general errors, requests to the domain resource may
return the following errors:

-  ``400 Bad Request``

   -  The request is not well formed.
   
-  ``403 Forbidden``

   - The requestor does not have sufficient privileges for this action.
   
-  ``404 Not Found``

   - The Domain does not exist.
   
 
