###########
Domain
###########

This resource represents an HDF5 domain - a collection of related resources (Groups, Datasets,
Attributes, etc.) that is the equivalent
of an HDF5 file in traditional HDF5 applications.

*Supported Operations:*  GET, PUT, DELETE

*Note:* If the HDF DNS Server (see DNS) is not configured,
domains can be addressed using the host http header (see example below).  Use the 
server endpoint as target address in this case.
If the HDF DNS Server has  has been configured, you can use the domain name  
address.  The DNS server will determine the proper IP that maps to this domain.
 

GET /
-----------

Returns information about the specified domain.

Request
~~~~~~~

.. code-block:: http

    GET / HTTP/1.1
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

PUT /
-----------

Creates a new HDF5 domain. 

*Note:* The domain name must follow standard Domain naming specifications (see: xxx)

*Note:* The domain will initially contain one object, the root group, whose UUID is 
returned by this call.


Request
~~~~~~~

.. code-block:: http

    PUT / HTTP/1.1
    Content-Length: 0
    host: DOMAIN
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
    
DELETE /
-----------

Deletes a HDF5 domain.

*WARNING:* all resources within the domain will be removed!

Request
~~~~~~~

.. code-block:: http

    DELETE / HTTP/1.1
    Content-Length: 0
    host: DOMAIN
    Authorization: <authorization_string>
    Content-Type: application/json  

Response
~~~~~~~~
.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/json


Errors
------

In addition to the general errors, requests to the domain resource may
return the following errors:

-  ``400 Bad Request``

   -  The domain name is not well formed.
   

-  ``403 Forbidden``

   - The requestor does not have sufficient privileges for this action.
   
- ``404 Not Found``

   - The domain could not be found
   
- ``409 Conflict``

   - The domain name already exists
   
- ``410 Gone``

   - The domain has been removed
