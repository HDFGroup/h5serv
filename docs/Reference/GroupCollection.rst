:tocdepth: 3

**********************************************
Groups
**********************************************

This resource represents the collection of all Groups within a domain.

*Supported Operations:*  GET, POST


GET /groups 
------------

Returns data about the Group collection.

*Note:* since an arbritrary number of groups may exist within the domain,
use the Marker and Limit parameters to iterate though large collections.  

Request
~~~~~~~

*Parameters:*

 - *Marker* [OPTIONAL]: Iteration marker.  See iteration 
 
 - *Limit*  [OPTIONAL]: Maximum number of uuids to return.  See iteration 

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
    "groups": ["<id1>", "<id2>", "<id3>", "<idN>"],

    "hrefs": [
        { "rel": "root",         "href": "http://<domain>/groups/<rootID>" },
        { "rel": "home",         "href": "http://<domain>/" },
        { "rel": "self",         "href": "http://<domain>/groups" }
    ]
   }

POST /groups 
-------------

Creates a new group. 

*Note:*   If link options are not passed in the body of the request, the new group will
initially be *anonymous*, i.e. it will not be linked
to by any other group within the domain.  However it can be accessed via: GET /groups/<id>.

If a "link" key is  passed in the body of the request the new group will be link to the 
given parent group with the given link name.  


Request
~~~~~~~

*Parameters:*




.. code-block:: http

    POST /groups HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    Content-Type: application/json
    
.. code-block:: json

    {
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
    "linkCount": "<non_negative_integer>",

    "refs": [
       { "rel": "attributes",   "href": "http://<domain>/groups/<id>/attributes" },
        { "rel": "links",        "href": "http://<domain>/groups/<id>/links" },
        { "rel": "root",         "href": "http://<domain>/groups/<rootID>" },
        { "rel": "home",         "href": "http://<domain>/" },
        { "rel": "self",         "href": "http://<domain>/groups/<id>" }
    ]
  


Errors
------

In addition to the general errors, requests to the groups resource may
return the following errors:

-  ``400 Bad Request``

   -  The request is not well formed. E.g. POST supplies a link key without an id or name.
   
-  ``403 Forbidden``

   - The requestor does not have sufficient privileges for this action.
   
-  ``404 Not Found``

   - The parent group does not exist. (For POST with a provided parent_group)
   
 
