####################
Types
####################

h5serv supports the rich type capabilities provided by HDF.  Types are used in datasets,
attributes, and committed types.  

There is not a separate request for creating types, rather the description of the type in
included with the request to create the dataset, attribute, or committed type.   Once
a type is created it is immutable and will exist until the containing object is deleted.

Type information is returned as a JSON object in dataset, attribute, or committed type
GET requests (under the type key).  


Predefined Types
----------------

tbd

Compound Types
---------------

tbd

Reference Types
---------------
tbd

Related Resources
=================

* :doc:`../DatasetOps/GET_Dataset`
* :doc:`../DatasetOps/GET_DatasetType`
* :doc:`../DatasetOps/POST_Dataset`
* :doc:`../AttrOps/GET_Attribute`
* :doc:`../AttrOps/PUT_Attribute`
* :doc:`../DatatypeOps/GET_Datatype`
* :doc:`../DatatypeOps/POST_Datatype`

 
    
