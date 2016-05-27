#######################
Domains
#######################

In h5serv, domains are containers for related collection of resources, similar to a
file in the traditional HDF5 library.  In the h5serv implementation of the HDF5 REST API,
domains *are* files, but in general the HDF REST API supports alternative implementations 
(e.g. data that is stored in a database).
Most operations of the service act on a domain resource that is provided in 
the *Host* http header or (alternatively) the Host query parameter.

Mapping of file paths to domain names
-------------------------------------

To convert a file path to a domain name:

#. Remove the extension
#. Determine the path relative to the data directory
#. Replace '/' with '.'
#. Reverse the path
#. Add the domain suffix (using the domain config value)

As an example consider a server installation where that data directory is '/data'
and an HDF5 is located at ``/data/myfolder/an_hdf_file.h5`` and ``hdfgroup.org``
is the base domain.  The above sequence of steps would look like the following:

#. /data/myfolder/an_hdf_file
#. myfolder/an_hdf_file
#. myfolder.an_hdf_file
#. an_hdf_file.myfolder
#. an_hdf_file.myfolder.hdfgroup.org

The final expression is what should be used in the Host field for any request that access
that file.  

For path names that include non-alphanumeric charters, replace any such characters with 
the string '%XX' where XX is the hexidecimal value of the character.  For example:

``this.file.has.dots.h5``

becomes:

``this%2Efile%2Ehase%2Edots``


Creating Domains
----------------
Use :doc:`PUT_Domain` to create a domain.  The domain name must follow DNS conventions
(e.g. two consecutive "dots" are not allowed).  After creation, the domain will contain
just one resource, the root group.  

Use :doc:`GET_Domain` to get information about a domain, including the UUID of the 
domain's root group.

Getting Information about Domains
---------------------------------

Use :doc:`GET_Domain` to retreive information about a specific domain (specified in the Host
header).  If the Host value is not supplied, the service returns information on the 
auto-generated Table of Contents (TOC) that provides information on domains that are available.

Deleting Domains
----------------
Use :doc:`DELETE_Domain` to delete a domain.  All resources within the domain will be
deleted!

The TOC domain cannot be deleted.

List of Operations
------------------

.. toctree::
   :maxdepth: 1

   DELETE_Domain
   GET_Domain
   PUT_Domain
    
    
