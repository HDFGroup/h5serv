**********************************************
GET Domain
**********************************************

Description
===========
This operation retrieves information about the requested domain.

*Note:* If the HDF Dynamic DNS Server (see https://github.com/HDFGroup/dynamic-dns) is running, 
the operations can specify the domain as part of the URI.  Example:  
http://tall.data.hdfgroup.org:7253/ 
returns data about the domain "tall" hosted on data.hdfgroup.org.  
The DNS server will determine the proper IP that maps to this domain.

If the DNS Server is not setup, specify the desired domain in the Host line of the http
header.

Alternatively, the domain can be specified as a 'Host' query parameter.  Example:
http://127.0.0.1:7253?host=tall.data.hdfgroup.org.

If no Host value is supplied, the default Table of Contents (TOC) domain is returned.

Requests
========

Syntax
------
.. code-block:: http

    GET / HTTP/1.1
    Host: DOMAIN
    Authorization: <authorization_string>
    
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

root
^^^^
The UUID of the root group of this domain.

created
^^^^^^^
A timestamp giving the time the domain was created in UTC (ISO-8601 format).

lastModified
^^^^^^^^^^^^
A timestamp giving the most recent time that any content in the domain has been
modified in UTC (ISO-8601 format).

hrefs
^^^^^
An array of links to related resources.  See :doc:`../Hypermedia`.

Special Errors
--------------

The implementation of the operation does not return any special errors.  For general 
information on standard error codes, see :doc:`../CommonErrorResponses`.

Examples
========

Sample Request
--------------

.. code-block:: http

    GET / HTTP/1.1
    host: tall.test.hdfgroup.org
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.3.0 CPython/2.7.8 Darwin/14.0.0
    
Sample Response
---------------

.. code-block:: http

    HTTP/1.1 200 OK
    Date: Fri, 16 Jan 2015 03:51:58 GMT
    Content-Length: 508
    Etag: "e45bef255ffc0530c33857b88b15f551f371de38"
    Content-Type: application/json
    Server: TornadoServer/3.2.2
    
.. code-block:: json
    
    {
    "root": "052dcbbd-9d33-11e4-86ce-3c15c2da029e", 
    "created": "2015-01-16T03:51:58Z",
    "lastModified": "2015-01-16T03:51:58Z", 
    "hrefs": [
        {"href": "http://tall.test.hdfgroup.org/", "rel": "self"},
        {"href": "http://tall.test.hdfgroup.org/datasets", "rel": "database"}, 
        {"href": "http://tall.test.hdfgroup.org/groups", "rel": "groupbase"}, 
        {"href": "http://tall.test.hdfgroup.org/datatypes", "rel": "typebase"},
        {"href": "http://tall.test.hdfgroup.org/groups/052dcbbd-9d33-11e4-86ce-3c15c2da029e", "rel": "root"}
    ]      
    }
    
Related Resources
=================

* :doc:`DELETE_Domain`
* :doc:`../GroupOps/GET_Group`
* :doc:`PUT_Domain`
 

 