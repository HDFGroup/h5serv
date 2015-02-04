########################
Attributes
########################

Like datasets (see :doc:`../DatasetOps/index`), attributes are objects that contain a 
homogeneous collection of elements
and have associatted type information.  Attributes are typically small metadata objects
that describe some aspect of the object (dataset, group, or committed datatype) that 
contains the attribute.

Creating Attributes
--------------------

Use :doc:`PUT_Attribute` to create an attribute.  If there is an existing attribute
with the same name, it will be overwritten by this request.  You can use
:doc:`GET_Attribute` to inquire if the attribute already exists or not.
When creating an attribute, the attribute name, type, and shape (for non-scalar
attributes) is included in the request.


Reading and Writing Data
-------------------------
Unlike datasets, attribute's data can not be
read or written partially.  Data can only be written as part of the PUT requests.  
Reading the data of an attribute is done by :doc:`GET_Attribute`.

Listing attributes
------------------
Use :doc:`GET_Attributes` to get information about all the attributes of a group, 
dataset, or committed datatype.

Deleting Attributes
-------------------

Use :doc:`DELETE_Attribute` to delete an attribute.

List of Operations
------------------

.. toctree::
   :maxdepth: 1

   DELETE_Attribute
   GET_Attribute
   GET_Attributes
   PUT_Attribute
 
    
    
