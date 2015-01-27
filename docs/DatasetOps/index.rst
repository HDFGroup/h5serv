######################
Datasets
######################

Datasets are objects that a composed of a homogenous collection of data elements.   Each
dataset has a *type* that specifies the structure of the individual elements: float, string,
compound, etc.), and a *shape* that specifies that layout of the data elements (scalar, 
one-dimensional, multi-dimensional).  In addition meta-data can be attached to a dataset
in the form of attributes.  See: :doc:`../AttrOps/index`.

Creating Datasets
-----------------

Use the :doc:`POST_Dataset` operation to create new datasets.  As part of the POST
request, JSON descriptions for the type and shape of the dataset are included with the
request.  

Writing data to a dataset
-------------------------
To write data into the dataset, use the :doc:`PUT_Value` operation.  The request can
either provide values for the entire dataset, or values for a hyperslab (rectangular
sub-region) selection.  In addition, if it desired to update a specific list of 
data elements, a point selection (series of element coordinates) can be passed to the 
PUT operation.
 
Reading data from a dataset
---------------------------
To read either the entire dataset or a hyperslab selection, use the :doc:`GET_Value`
operation.  To read a point selection, use the :doc:`POST_Value` operation  (POST is 
used in this case rather than GET since the point selection values may be to 
large to include in the URI.) 

Resizable datasets
------------------
If one or more of the dimensions of a dataset may need to be extended after creation,
provide a *maxdims* key to the shape during creation.  If the value of the maxdims
dimension is 0, that dimension is *unlimited* and may be extended as much as desired.
If an upper limit is known, use that value in maxdims which will allow that dimension
to be extended up to the given value.

Deleting datasets
-----------------
The :doc:`DELETE_Dataset` operation will remove the dataset, its attributes, and any
links to the object.

Operations
----------

.. toctree::
   :maxdepth: 2

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
    
    
