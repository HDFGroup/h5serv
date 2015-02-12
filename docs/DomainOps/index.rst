#######################
Domains
#######################

In h5serv, domains are containers for related collection of resources, similar to a
file in the traditional HDF5 library.
Other than :doc:`PUT_Domain`, every operation of the service explicitly
includes the domain resource in the *Host* line of the http request.

If the included DNS server is set up (see :doc:`../Installation/DNSSetup`), the domain
name can also be used as the endpoint of the request.

*Note:* Currently h5serv does not include any functions for listing or querying which
domains are available.

Creating Domains
----------------
Use :doc:`PUT_Domain` to create a domain.  The domain name must follow DNS conventions
(e.g. two consecutive "dots" are not allowed).  After creation, the domain will contain
just one resource, the root group.  

Use :doc:`GET_Domain` to get information about a domain, including the UUID of the 
domain's root group.

Deleting Domains
----------------
Use :doc:`DELETE_Domain` to delete a domain.  All resources within the domain will be
deleted!

List of Operations
------------------

.. toctree::
   :maxdepth: 1

   DELETE_Domain
   GET_Domain
   PUT_Domain
    
    
