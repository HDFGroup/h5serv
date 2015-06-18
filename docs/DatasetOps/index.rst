######################
Datasets
######################

Datasets are objects that a composed of a homogenous collection of data elements.   Each
dataset has a *type* that specifies the structure of the individual elements (float, string,
compound, etc.), and a *shape* that specifies the layout of the data elements (scalar, 
one-dimensional, multi-dimensional).  In addition meta-data can be attached to a dataset
in the form of attributes.  See: :doc:`../AttrOps/index`.

Creating Datasets
-----------------

Use the :doc:`POST_Dataset` operation to create new datasets.  As part of the POST
request, JSON descriptions for the type and shape of the dataset are included with the
request.  Optionally, creation properties can be used to specify the chunk layout (how
the data elements are stored in the server) and compression filter (e.g. GZIP, LZF, SZIP).

Getting information about a dataset
-----------------------------------
Use the :doc:`GET_Dataset` operation to retrieve information about a datasets type,
shape, creation properties, and number of attributes.  To list all the datasets within a domain use 
:doc:`GET_Datasets`.  To list the datasets linked to a particular group use 
:doc:`../GroupOps/GET_Links` and look at links with a "collection" key of "datsets".

Writing data to a dataset
-------------------------
To write data into the dataset, use the :doc:`PUT_Value` operation.  The request can
either provide values for the entire dataset, or values for a hyperslab (rectangular
sub-region) selection.  In addition, if it desired to update a specific list of 
data elements, a point selection (series of element coordinates) can be passed to the 
:doc:`PUT_Value` operation.
 
Reading data from a dataset
---------------------------
To read either the entire dataset, or a specified selection, use the :doc:`GET_Value`
operation.  Without any request parameters, the GET operation retuns all data values.  
To read a specific hyperslab, use the select parameter to start and end indexes of the hyperslab
(the selection can also include a step value to include a regular subset of the hyperslab).
Finally, for one-dimensional datasets with compound types, a *where* parameter can be used to 
select elements meeting a specified condition. 

To read a specific list of elements (by index values), use the :doc:`POST_Value` operation  (POST is 
used in this case rather than GET since the point selection values may be to 
large to include in the URI.) 

Resizable datasets
------------------
If one or more of the dimensions of a dataset may need to be extended after creation,
provide a *maxdims* key to the shape during creation (see :doc:`POST_dataset`).  If the value of the maxdims
dimension is 0, that dimension is *unlimited* and may be extended as much as desired.
If an upper limit is known, use that value in maxdims which will allow that dimension
to be extended up to the given value.
To resize the dataset, use :doc:`PUT_DataShape.rst` operation with the desired shape value(s) for
the new dimensions.

Note: dimensions can only be increased, not decreased.

Deleting datasets
-----------------
The :doc:`DELETE_Dataset` operation will remove the dataset, its attributes, and any
links to the object.

List of Operations
-------------------

.. toctree::
   :maxdepth: 1

   DELETE_Dataset
   GET_Dataset
   GET_Datasets
   GET_DatasetShape
   GET_DatasetType
   GET_Value
   POST_Dataset
   POST_Value
   PUT_DatasetShape
   PUT_Value
    
    
