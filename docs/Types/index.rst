####################
Types
####################

The h5serv REST API supports the rich type capabilities provided by HDF.  Types are 
are described in JSON and these JSON descriptions are used in operations involving 
datasets, attributes, and committed types.  

There is not a separate request for creating types, rather the description of the type in
included with the request to create the dataset, attribute, or committed type.   Once
a type is created it is immutable and will exist until the containing object is deleted.

Type information is returned as a JSON object in dataset, attribute, or committed type
GET requests (under the type key).  


Predefined Types
================

Predefined types are base integer and floating point types that are identified via
one of the following strings:

 * ``H5T_STD_U8{LE|BE}``: a one byte unsigned integer
 * ``H5T_STD_I8{LE|BE}``: a one byte signed integer
 * ``H5T_STD_U6{LE|BE}``: a two byte unsigned integer
 * ``H5T_STD_I16{LE|BE}``: a two byte signed integer
 * ``H5T_STD_U32{LE|BE}``: a four byte unsigned integer
 * ``H5T_STD_I32{LE|BE}``: a four byte signed integer
 * ``H5T_STD_U64{LE|BE}``: a eight byte unsigned integer
 * ``H5T_STD_I64{LE|BE}``: a eight byte signed integer
 * ``H5T_IEEE_F32{LE|BE}``: a four byte floating-point value
 * ``H5T_IEEE_F64{LE|BE}``: a eight byte floating-point integer
        
Predefined types ending in "LE" or little-endian formatted and types ending in "BE"
are big-endian.  E.g. ``H5T_STD_I64LE`` would be an eight byte, signed, little-endian
integer.    

*Note:* little vs. big endian are used to specify the byte ordering in the server storage
system and are not reflected in the JSON representation of the values.

Example 
-------

JSON Representation of an attribute with a ``H5T_STD_I8LE`` (signed, one byte) type:

.. code-block:: json

    {
    "name": "attr1", 
    "shape": {
        "class": "H5S_SIMPLE", 
        "dims": [27]
    }, 
    "type": {
        "class": "H5T_INTEGER",
        "base": "H5T_STD_I8LE"
        },
    "value": [49, 115, 116, 32, 97, 116, 116, 114, 105, 98, 117, 116, 101, 32, 
              111, 102, 32, 100, 115, 101, 116, 49, 46, 49, 46, 49, 0]
    }


String Types - Fixed Length
============================

                     
Fixed length strings have a specified length (supplied when the object is created) that 
is used for each data element.  Any values that are assigned that exceed that length 
will be truncated. 

To specify a fixed length string, create a JSON object with class, charSet, strPad,
and length keys (see definitions of these keys below).

*Note:* Current only the ASCII character set is supported.

*Note:* Fixed width unicode strings are not currently supported.

*Note:* String Padding other than "H5T_STR_NULLPAD" will get stored as "H5T_STR_NULLPAD"

Example 
-------

JSON representation of a dataset using a fixed width string of 40 characters:

.. code-block:: json

    {
    "id": "1e8a359c-ac46-11e4-9f3e-3c15c2da029e",
    "shape": {
        "class": "H5S_SCALAR", 
    }, 
    "type": {
        "class": "H5T_STRING", 
        "charSet": "H5T_CSET_ASCII", 
        "strPad": "H5T_STR_NULLPAD", 
        "length": 40
        },
    "value": "Hello, World!"
    }
    
String Types - Variable Length
==============================

Variable length strings allow each element of an array to only use as much storage
as needed.  This is convenient when the maximum string length is not know before hand,
or there is a great deal of variability in the lengths of strings.  

*Note:* Typically there is a slight performance penalty in accessing variable length
string elements of an array in the server.

To specify a variable length string, create a JSON object with class, charSet, strPad,
and length keys (see definitions of these keys below) where the value of "length" is:
``H5T_VARIABLE``.

*Note:* Current only the ASCII character set is supported.

*Note:* Variable width unicode strings are not currently supported.

*Note:* String Padding other than "H5T_STR_NULLTERM" will get stored as "H5T_STR_NULLTERM"

Example 
-------

JSON representation of a attribute using a variable length string:

.. code-block:: json

    {
    "name": "A1", 
    "shape": {
        "class": "H5S_SIMPLE", 
        "dims": [4]
    }, 
    "type": {
        "class": "H5T_STRING", 
        "charSet": "H5T_CSET_ASCII", 
        "strPad": "H5T_STR_NULLTERM", 
        "length": "H5T_VARIABLE"
    }, 
    "value": [
        "Hypermedia", 
        "as the", 
        "engine", 
        "of state."
      ]
    }

    

Compound Types
==============

For some types of data it makes sense to store sets of related items together rather
than in separate datasets or attributes.  For these use cases a compound datatype
can be defined.  A compound datatype has class: ``H5T_COMPOUND`` and a field key which
contains an array of sub-types.  
Each of these sub-types can be a primitive type, a string, or another 
compound type.  Each sub-type has a name that can be used to refer to the element.

*Note:* The field names are not shown in the representation of an dataset or attribute's
values.

Example 
-------

JSON representation of a scalar attribute with a compound type that consists of two 
floating point elements:

.. code-block:: json

    {
    "name": "mycomplex", 
    "shape": {
        "class": "H5S_SCALAR" 
    }, 
    "type": {
        "class": "H5T_COMPOUND", 
        "fields": [
                {
                "name": "real_part", 
                "type": {
                        "base": "H5T_IEEE_F64LE", 
                        "class": "H5T_FLOAT"
                    }
                }, 
                {
                "name": "imaginary_part", 
                "type": {
                        "base": "H5T_IEEE_F64LE", 
                        "class": "H5T_FLOAT"
                    }
                }
            ]
    }, 
    "value": [ 1.2345, -2.468 ]
    }
    
Enumerated Types
=================

Enumerated types enable the integer values of a dataset or attribute to be mapped to
a set of strings.  This allows the semantic meaning of a given set of values to be
described along with the data.

To specify an enumerated type, use the class ``H5T_ENUM``, provide a base type (must be
some form of integer), and a "mapping" key that list strings with their associated 
numeric values.


Example 
-------

.. code-block:: json
    
    {
    "id": "1e8a359c-ac46-11e4-9f3e-3c15c2da029e",
    "shape": {
        "class": "H5S_SIMPLE", 
        "dims": [ 7 ]
    }, 
    "type": {
        "class": "H5T_ENUM",
        "base": {
            "class": "H5T_INTEGER",
            "base": "H5T_STD_I16BE" 
        },  
        "mapping": {
            "GAS": 2, 
            "LIQUID": 1, 
            "PLASMA": 3, 
            "SOLID": 0
        }
    }, 
    "value": [ 0, 2, 3, 2, 0, 1, 1 ]
    }
                
Array Types
===========

Array types are used when it is desired for each element of a attribute or dataset
to itself be a (typically small) array.

To specify an array type, use the class ``H5T_ARRAY`` and provide the dimensions 
of the array with the type.  Use the "base" key to specify the type of the elements
of the array type.

Example 
-------

A dataset with 3 elements, each of which is a 2x2 array of integers.

.. code-block:: json

    {
    "id": "9348ad51-7bf7-11e4-a66f-3c15c2da029e",
    "shape": {
        "class": "H5S_SIMPLE", 
        "dims": [ 3 ]
    }, 
    "type": {
        "class": "H5T_ARRAY", 
        "base": {
            "class": "H5T_INTEGER",
            "base": "H5T_STD_I16BE"
        }, 
        "dims": [ 2, 2 ]
    }, 
    "value": [
        [ [1, 2], [3, 4] ],
        [ [2, 1], [4, 3] ],
        [ [1, 1], [4, 4] ]
      ]
    }
    
Opaque Types
=============

TBD

Example
-------
TBD

Object Reference Types
======================

An object reference type enables you to define an array where each element of the
array is a reference to another dataset, group or committed datatype.

To specify a object reference type, use ``H5T_REFERENCE`` as the type class, and
``H5T_STD_REF_OBJ`` as the base type.

The elements of the array consist of strings that have the prefix: "groups/", 
"datasets/", or "datatypes/" followed by the UUID of the referenced object.


Example 
-------

A JSON representation of an attribute that consist of a 3 element array of object 
references.  The first element points to a group, the second element is null, and the 
third element points to a group.

.. code-block:: json

    {
    "name": "objref_attr", 
    "shape": {
        "class": "H5S_SIMPLE", 
        "dims": [ 3 ]
    }, 
    "type": {
        "class": "H5T_REFERENCE",
        "base": "H5T_STD_REF_OBJ"
    }, 
    "value": [
        "groups/a09a9b99-7bf7-11e4-aa4b-3c15c2da029e", 
        "",
        "datasets/a09a8efa-7bf7-11e4-9fb6-3c15c2da029e"
      ]
    }
    
Region Reference Types
======================

A region reference types allows the creation of attributes or datasets where each array
element references a section (point selection or hyperslab) of another dataset.

To specify a region reference type, use ``H5T_REFERENCE`` as the type class, and
``H5T_STD_REF_DSETREG`` as the base type.

*Note:* When writing values to the dataset, each element of the dataset must be 
a JSON object with keys: "id", "select_type", and "selection" (as in the example below).

Example 
-------

A JSON representation of a region reference dataset with two elements.

The first element is a point selection element that references 4 elements
in the dataset with UUID of "68ee967a-...".

The second element is a hyperslab selection that references 4 hyper-slabs in 
the same dataset as the first element.  Each element is a pair of points that
gives the boundary of the selection.

.. code-block:: json

    {
    "id": "68ee8647-7bed-11e4-9397-3c15c2da029e",
    "shape": {
        "class": "H5S_SIMPLE", 
        "dims": [2]
    }, 
    "type": {
        "class": "H5T_REFERENCE",
        "base": "H5T_STD_REF_DSETREG"
    }, 
    "value": [
        {
        "id": "68ee967a-7bed-11e4-819c-3c15c2da029e", 
        "select_type": "H5S_SEL_POINTS", 
        "selection": [ 
            [0, 1], [2, 11], [1, 0], [2, 4]
          ]
        }, 
        {
          "id": "68ee967a-7bed-11e4-819c-3c15c2da029e", 
          "select_type": "H5S_SEL_HYPERSLABS", 
          "selection": [
            [ [0, 0],  [0, 2] ], 
            [ [0, 11],  [0, 13] ], 
            [ [2, 0],  [2, 2] ], 
            [ [2, 11],  [2, 13] ]
          ]
        }
      ]
    }  
    
Type Keys
=========

Information on the JSON keys used in type specifications.

class
-----
The type class.  One of:

* ``H5T_INTEGER``: an integer type
* ``H5T_FLOAT``: a floating point type
* ``H5T_STRING``: a string type
* ``H5T_OPAQUE``: an opaque type
* ``H5T_COMPOUND``: a compound type
* ``H5T_ARRAY``: an array type
* ``H5T_ENUM``: an enum type
* ``H5T_REFERENCE``: a reference type

base
----

A string that gives the base predefined type used (or reference type for the 
reference class).

order
-----

The byte ordering.  One of:

* ``H5T_NONE``: Ordering is not relevant (e.g. for string types)
* ``H5T_ORDER_LE``: Little endian ordering (e.g. native ordering for x86 computers)
* ``H5T_ORDER_BE``: Big endian ordering

charSet
-------

Character set for strings.  Currently only ``H5T_CSET_ASCII`` is supported.

strPad
-------

Defines how fixed length strings are padded.  One of:

* ``H5T_STR_NULLPAD``: String is padded with nulls
* ``H5T_STR_NULLTERM``: String is null terminated
* ``H5T_STR_SPACEPAD``: String is padded with spaces

length
--------

Defines the string length.  Either a positive integer or the string: ``H5T_VARIABLE``.

name
----

The field name for compound types.

mapping
-------

The enum name for enum types.

select_type
-----------

The selection type for reference types.  One of:

* ``H5S_SEL_POINTS``: selection is a series of points
* ``H5S_SEL_HYPERSLABS``: selection is a series of hyper-slabs.

Related Resources
=================

* :doc:`../DatasetOps/GET_Dataset`
* :doc:`../DatasetOps/GET_DatasetType`
* :doc:`../DatasetOps/POST_Dataset`
* :doc:`../AttrOps/GET_Attribute`
* :doc:`../AttrOps/PUT_Attribute`
* :doc:`../DatatypeOps/GET_Datatype`


* :doc:`../DatatypeOps/POST_Datatype`

 
    
