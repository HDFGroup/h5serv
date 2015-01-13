#####
Link 
#####

This resource represents a link (a member of the links collection) within a group. 
See *Links* for a information on how links work in h5serv. 

*Supported Operations:*  GET, PUT, DELETE


GET /groups/<id>/links/<name> HTTP/1.1
--------------------------------------

Returns information about the link named <name> contained in the group with the UUID of <id>.

*Note:* since an arbritrary large number of links may exist within the collection,
use the Marker and Limit parameters to iterate though large collections.  To get
the number of links, use:
*GET /groups/<id>* and inspect that linkCount value.

Request
~~~~~~~

.. code-block:: http

    GET /groups/<id>/links/<name> HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    Content-Type: application/json

Response
~~~~~~~~

The following json elements will be returned:
 
    - name: the name of the link
    - class: the class of the link.  One of "hard", "soft", "external", or "user"
    - target: the contents of the link
    - created: the time at which the link was created
    - lastModified: the time at which the link was modified
    
Format of the target depends on the class returned:

    - hard: returns a link to the object in the datasets, datatypes, or groups
        collection (depending on the type of target).
    - soft: a fragment identifier containing the path to the linked object
    - external: a href to the resource 
    - user: A User Defined link - these are generated via User Defined link
        extensions to the HDF5 library.  Creation of User Defined Links or 
        not supported by the REST api currently.
 
 Currently "user" links do not return a target.
    
The object identified by the UUID in a hard link is guaranteed to be present.
For other link types, the resource may or may not exist.


.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/json
    
The format of the json response depends on the link class.

For hard links the following is returned:
    
.. code-block:: json

   {
    "name": "<name>",
    "class": "hard",
    "target": "/(datasets|datatypes|groups)/<id>",
    "created": "<utctime>",
    "lastModified": "<utctime>",
    "hrefs": [
        { "rel": "owner",        "href": "http://<domain>/groups/<id>/links" },
        { "rel": "root",         "href": "http://<domain>/groups/<rootID>" },
        { "rel": "home",         "href": "http://<domain>/" },
        { "rel": "self",         "href": "http://<domain>/groups/<id>/links/<name>" }
    ]
    }
    
For soft links the json response will be:

.. code-block:: json

 {
    "name": "<name>",
    "class": "soft",
    "target": "/#h5path(<HDF5 path name>)",
    "created": "<utctime>",
    "lastModified": "<utctime>",
    "hrefs": [
        { "rel": "owner",        "href": "http://<domain>/groups/<id>/links" },
        { "rel": "root",         "href": "http://<domain>/groups/<rootID>" },
        { "rel": "home",         "href": "http://<domain>/" },
        { "rel": "self",         "href": "http://<domain>/groups/<id>/links/<name>" }
    ]
    }
    
*"<HDF5 path name>"* will be a slash separated series of link names.  
E.g. *"/g1/g1.1/dset1.1.1"*

For external links the json response will be:

.. code-block:: json

 {
    "name": "<name>",
    "class": "external",
    "target": "<href>",
    "created": "<utctime>",
    "lastModified": "<utctime>",
    "hrefs": [
        { "rel": "owner",        "href": "http://<domain>/groups/<id>/links" },
        { "rel": "root",         "href": "http://<domain>/groups/<rootID>" },
        { "rel": "home",         "href": "http://<domain>/" },
        { "rel": "self",         "href": "http://<domain>/groups/<id>/links/<name>" }
    ]
    }
    
In this response, "<href>" will be in the form:

*"http://<domain>/(datasets|datatypes|groups)/<id>"*

if the value of the link is a UUID.  Or:

*"http://<domain>/#h5path(<HDF5 path name>) "*

if the value of the link represents an HDF5 path.


PUT /groups/<id>/links/<name> HTTP/1.1
--------------------------------------

Creates a new Link with the given name.  Link type is determined by argument 
 ("idref", "h5path", or "href") supplied in the body of the request.

*Note:* <name> in the path can not contain '/' characters.  <name> should be url-encoded
if it contains characters not allowed in URL strings (e.g. space characters).

*Note:* Creation of user defined links is not supported currently.

Request
~~~~~~~

*Parameters:*

 - *idref:* Used to create hard links.  Request will fail (return 404) if <id> does not 
    refer to the UUID of an existing Group, Dataset, or Committed Datatype in the domain.
 
 - *h5path:*  Path to a resource in the domain.  Referenced resource may or may not
    exist.
 
 - *href:* An href to an external resource.
 

.. code-block:: http

    PUT /groups/<id>/links/<name> HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    Content-Type: application/json
    
.. code-block:: json

 {
   "idref": <id>
 }
 
 or
 
 .. code-block:: json

 {
   "h5path": <path>
 }
 
 or
 
 .. code-block:: json

 {
   "href": <href>
 }
 
 
 

Response
~~~~~~~~
.. code-block:: http

    HTTP/1.1 201 Created
    Content-Type: application/json
    
.. code-block:: json


   {
    "name": <name>,
    "class": "hard"|"soft"|"external"|"user",
    "created": <utctime>,
    "lastModified": <utctime>,
    "target": "/(datasets|datatypes|groups)/<id>" |
              "/#h5path(<HDF5 path name>)" |
              "http://<domain>/(datasets|datatypes|groups)/<id>" |
              "http://<domain>/#h5path(<HDF5 path name>) ",
    "hrefs": [
        { "rel": "owner",        "href": "http://<domain>/groups/<id>/links" },
        { "rel": "root",         "href": "http://<domain>/groups/<rootID>" },
        { "rel": "home",         "href": "http://<domain>/" },
        { "rel": "self",         "href": "http://<domain>/groups/<id>/links/<name>" }
    ]
    }
    
    
DELETE /groups/<id>/link/<name>
--------------------------------

Removes the link resource identified by <name> of Group with UUID of <id>.

*Note:* Unlike with the HDF5 library, removing the last hardlink to a resource does
not remove the resource itself.  Use *DELETE* on the "/groups", "/datasets", or 
"/datatypes" to remove the target object.

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
Returns a representation of the Links collection the link was a in.
.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

.. code-block:: json  
  
    "hrefs": [
        { "rel": "self",        "href": "http://<domain>/groups/<id>/links" },
        { "rel": "root",         "href": "http://<domain>/groups/<rootID>" },
        { "rel": "home",         "href": "http://<domain>/" }    ]
    }


Errors
------

In addition to the general errors, requests to the domain resource may
return the following errors:

-  ``400 Bad Request``

   -  The domain name is not well formed.
   

-  ``403 Forbidden``

   - The requestor does not have sufficient privileges for this action.
   
- ``404 Not Found``

   - The Domain, Group, or Link name could not be found
   
- ``409 Conflict``

   - A link with this name already exists
   
- ``410 Gone``

   - The link has been removed
