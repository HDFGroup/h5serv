#######################
Committed Datatypes
#######################

Committed datatypes (also know as "named types"), are object that describe types.  These
types can be used in the creation of datasets and attributes.

Committed datatypes can also contain attributes, to store metadata about the type.

Creating committed datatypes
----------------------------

Use :doc:`POST_Datatype` to create a new datatype.  A complete description of the 
type must be sent with the POST request.

Deleting committed datatypes
----------------------------

Use :doc:`DELETE_Datatype` to delete a datatype.  Links from any group to the datatype
will be deleted.  

Operations
----------

.. toctree::
   :maxdepth: 3

   DELETE_Datatype
   GET_Datatype
   GET_Datatypes
   POST_Datatype
    
    
