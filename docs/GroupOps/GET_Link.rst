**********************************************
GET Link
**********************************************

Description
===========
Returns information about a Link.

Requests
========

Syntax
------
.. code-block:: http

    GET /groups/<id>/links/<name> HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
* *<id>* is the UUID of the group the link is a member of.
* *<name>* is the URL-encoded name of the link.
    
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

link["title"]
^^^^^^^^^^^^^
The name of the link.

link["collection"]
^^^^^^^^^^^^^^^^^^
For hard links, the domain collection for which the object the link points to is a 
member of.  The value will be one of: "groups", "datasets", "datatypes".
For symbol links, this element is not present.

link["class"]
^^^^^^^^^^^^^
Indicates the type of link.  One of the following values will be returned:

* H5L_TYPE_HARD: A direct link to a group, dataset, or committed datatype object in the domain
* H5L_TYPE_SOFT: A symbolic link that gives a path to an object within the domain (object may or may not be present).
* H5L_TYPE_EXTERNAL: A symbolic link to an object that is external to the domain
* H5L_TYPE_UDLINK: A user-defined link (this implementation only provides title and class for user-defined links)

link["h5path"]
^^^^^^^^^^^^^^
For symbolic links ("H5L_TYPE_SOFT" or "H5L_TYPE_EXTERNAL"), the path to the resource the
link references.  

link["h5domain"]
^^^^^^^^^^^^^^^^
For external links, the path of the external domain containing the object that is linked.
*Note:* The domain may or may not exist.  Use GET / with the domain to verify.

link["id"]
^^^^^^^^^^^^
For hard links, the uuid of the object the link points to.  For symbolic links this
element is not present

created
^^^^^^^
A timestamp giving the time the link was created in UTC (ISO-8601 format).

lastModified
^^^^^^^^^^^^
A timestamp giving the most recent time the group has been
modified in UTC (ISO-8601 format).

hrefs
^^^^^
An array of hypertext links to related resources.  See :doc:`../Hypermedia`.

Special Errors
--------------

The implementation of the operation does not return special errors.  For general 
information on standard error codes, see :doc:`../CommonErrorResponses`.

Examples
========

Sample Request - Hard Link
--------------------------

.. code-block:: http

    GET /groups/052dcbbd-9d33-11e4-86ce-3c15c2da029e/links/g1 HTTP/1.1
    host: tall.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response - Hard Link
---------------------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Fri, 16 Jan 2015 22:42:05 GMT
    Content-Length: 688
    Etag: "70c5c4f2f7cac9f7f155fe026f4c492f65e3fb8e"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
        
    {
    "link": {
        "title": "g1", 
        "collection": "groups", 
        "class": "H5L_TYPE_HARD", 
        "id": "052e001e-9d33-11e4-9a3d-3c15c2da029e"
    }, 
    "created": "2015-01-16T03:47:22Z",
    "lastModified": "2015-01-16T03:47:22Z", 
    "hrefs": [
        {"href": "http://tall.test.hdfgroup.org/groups/052dcbbd-9d33-11e4-86ce-3c15c2da029e/links/g1", "rel": "self"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/052dcbbd-9d33-11e4-86ce-3c15c2da029e", "rel": "root"}, 
        {"href": "http://tall.test.hdfgroup.org/", "rel": "home"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/052dcbbd-9d33-11e4-86ce-3c15c2da029e", "rel": "owner"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/052e001e-9d33-11e4-9a3d-3c15c2da029e", "rel": "target"}
     ]
    } 
       
Sample Request - Soft Link
--------------------------

.. code-block:: http

    GET /groups/052e700a-9d33-11e4-9fe4-3c15c2da029e/links/slink HTTP/1.1
    host: tall.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0    
    Related Resources
    
Sample Response - Soft Link
---------------------------

.. code-block:: http
    
    HTTP/1.1 200 OK
    Date: Fri, 16 Jan 2015 23:29:27 GMT
    Content-Length: 620
    Etag: "7bd777729ac5af261c85c7e3b87ef0045739bf77"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json

    {
    "link": {
            "title": "slink",
            "class": "H5L_TYPE_SOFT",
            "h5path": "somevalue"
             }, 
    "created": "2015-01-16T03:47:22Z",
    "lastModified": "2015-01-16T03:47:22Z", 
    "hrefs": [
        {"href": "http://tall.test.hdfgroup.org/groups/052e700a-9d33-11e4-9fe4-3c15c2da029e/links/slink", "rel": "self"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/052dcbbd-9d33-11e4-86ce-3c15c2da029e", "rel": "root"},
        {"href": "http://tall.test.hdfgroup.org/", "rel": "home"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/052e700a-9d33-11e4-9fe4-3c15c2da029e", "rel": "owner"}, 
        {"href": "http://tall.test.hdfgroup.org/#h5path(somevalue)", "rel": "target"}
      ] 
    }
         
        
Sample Request - External Link
------------------------------

.. code-block:: http

    GET /groups/052e5ae8-9d33-11e4-888d-3c15c2da029e/links/extlink HTTP/1.1
    host: tall.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response - External Link
-------------------------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Tue, 20 Jan 2015 05:47:55 GMT
    Content-Length: 644
    Etag: "1b7a228acdb19f7259ed8a1b3ba4bc442b405ef9"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json

    {
    "link": {
        "title": "extlink", 
        "class": "H5L_TYPE_EXTERNAL",
        "h5path": "somepath",
        "h5domain": "somefile"
    }, 
    "created": "2015-01-16T03:47:22Z",
    "lastModified": "2015-01-16T03:47:22Z", 
    "hrefs": [
        {"href": "http://tall.test.hdfgroup.org/groups/052e5ae8-9d33-11e4-888d-3c15c2da029e/links/extlink", "rel": "self"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/052dcbbd-9d33-11e4-86ce-3c15c2da029e", "rel": "root"},
        {"href": "http://tall.test.hdfgroup.org/", "rel": "home"}, 
        {"href": "http://tall.test.hdfgroup.org/groups/052e5ae8-9d33-11e4-888d-3c15c2da029e", "rel": "owner"}, 
        {"href": "http://somefile.hdfgroup.org#h5path(somepath)", "rel": "target"}
      ] 
    }
    
    
        
Sample Request - User Defined Link
----------------------------------

.. code-block:: http

    GET /groups/0262c3a6-a069-11e4-8905-3c15c2da029e/links/udlink HTTP/1.1
    host: tall_with_udlink.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0


Sample Response - User Defined Link
-----------------------------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Tue, 20 Jan 2015 05:56:00 GMT
    Content-Length: 576
    Etag: "2ab310eba3bb4282f84d643fcc30e591da485576"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json

    {
    "link": {
        "class": "H5L_TYPE_USER_DEFINED", 
        "title": "udlink"
        }, 
    "created": "2015-01-16T03:47:22Z",
    "lastModified": "2015-01-16T03:47:22Z", 
    "hrefs": [
        {"href": "http://tall_with_udlink.test.hdfgroup.org/groups/0262c3a6-a069-11e4-8905-3c15c2da029e/links/udlink", "rel": "self"}, 
        {"href": "http://tall_with_udlink.test.hdfgroup.org/groups/0260b214-a069-11e4-a840-3c15c2da029e", "rel": "root"}, 
        {"href": "http://tall_with_udlink.test.hdfgroup.org/", "rel": "home"}, 
        {"href": "http://tall_with_udlink.test.hdfgroup.org/groups/0262c3a6-a069-11e4-8905-3c15c2da029e", "rel": "owner"}
    ]       
    }
    
=================

* :doc:`DELETE_Link`
* :doc:`GET_Links`
* :doc:`PUT_Link`
 

 