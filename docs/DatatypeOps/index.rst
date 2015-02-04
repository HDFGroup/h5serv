#######################
Committed Datatypes
#######################

Committed datatypes (also know as "named types"), are object that describe types.  These
types can be used in the creation of datasets and attributes.

Committed datatypes can be linked to from a Group and can contain attributes, just like
a dataset or group object.

Creating committed datatypes
----------------------------

Use :doc:`POST_Datatype` to create a new datatype.  A complete description of the 
type must be sent with the POST request.

Getting information about a committed datatype
-----------------------------------------------

Use the :doc:`GET_Datatype` operation to retrieve information about a committed datatype.
To list all the committed datatypes within a domain use 
:doc:`GET_Datatypes`.  To list the committed types linked to a particular group use 
:doc:`../GroupOps/GET_Links` and examine link object with a "collection" key of 
"datatypes".

Deleting committed datatypes
----------------------------

Use :doc:`DELETE_Datatype` to delete a datatype.  Links from any group to the datatype
will be deleted.  

List of Operations
------------------

.. toctree::
   :maxdepth: 1

   DELETE_Datatype
   GET_Datatype
   GET_Datatypes
   POST_Datatype
    
    
