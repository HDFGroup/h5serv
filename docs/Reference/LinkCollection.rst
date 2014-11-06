################
Link Collection
################

This resource represents the collection of links within a group. See *Links* for a 
informatin on how links work. 

*Supported Operations:*  GET, PUT


GET /groups/<id>/links 
----------------------

Returns information about the links contained in the group with the UUID of <id>.  See
*Links* for more information about how links work with h5serv.

*Note:* since an arbritrary large number of links may exist within the collection,
use the Marker and Limit parameters to iterate though large collections.  To get
the number of links, use:
*GET /groups/<id>* and inspect that linkCount value.

Request
~~~~~~~

*Parameters:*

 - *Marker:* Iteration marker.  See *paginatin*
 
 - *Limit:* Maximum number of uuids to return.  See *pagination*


.. code-block:: http

    GET /groups/<id> HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>

Response
~~~~~~~~

"links" will be an array of json elements consisting of:
 
    - name: the name of the link
    - class: the class of the link.  One of "hard", "soft", "external", or "user"
    - target: the contents of the link
    
Format of the target depends on the class returned:

 - hard: returns a link to the object in the datasets, datatypes, or groups
   collection (depending on the type of target).
 - soft: a fragment identifier containing the path to the linked object
 - external: a href to the resource 
 
 Currently "user" links do not return a target.
    
The object identified by the UUID in a hard link is guaranteed to be present.
For other link types, the resource may or may not exist.

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/json
    
.. code-block:: json

   {
    "links": [ 
        { "name": <name>, 
          "class": "hard|soft|external|user",
          "target":  "/(datasets|datatypes|groups)/<id>" |
                  "/#h5(<HDF5 path name>)" |
                  "http://<domain>/(datasets|datatypes|groups)/<id>" |
                  "http://<domain>/#h5(<HDF5 path name>)" }, 
        ...
    
    ],
    "hrefs": [
        { "rel": "owner",        "href": "http://<domain>/groups/<id>" },
        { "rel": "root",         "href": "http://<domain>/groups/<rootID>" },
        { "rel": "home",         "href": "http://<domain>/" },
        { "rel": "self",         "href": "http://<domain>/groups/<id>/links" }
    }


    

