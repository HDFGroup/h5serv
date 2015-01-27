########################
Attributes
########################

Like datasets, attributes are objects that contain a homogeneous collection of elements
and have associatted type informations.  


Creating Attributes
--------------------

Use :doc:`PUT_Attribute` to create an attribute.  If there is an existing attribute
with the same name, it will be overwritten by this request.


Reading and Writing Data
-------------------------
Unlike datasets, attribute's data can not be
read or written partially.  Data can only be written as part of the PUT requests.  
Reading the data of an attribute is done by :doc:`GET_Attribute`.

Deleting Attributes
-------------------

Use :doc:`DELETE_Attribute` to delete an attribute.

Operations
----------

.. toctree::
   :maxdepth: 3

   DELETE_Attribute
   GET_Attribute
   GET_Attributes
   PUT_Attribute
    
    
