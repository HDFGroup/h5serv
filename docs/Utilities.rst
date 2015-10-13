###################
Utilities
###################

The h5serv distribution includes the following utility scripts.  These are all
located in the ``util`` directory.

dumpobjdb.py
------------

This script prints all the UUID's in an h5serv data file.

Usage:

``python dumpobjdb.py <hdf5_file>``

hdf5_file is a file from the h5serv data directory.  Output is a list of All UUID's and
a path to the associated object.

exportjson.py
-------------

This script makes a series of rest requests to the desired h5serv endpoint and
constructs a JSON file representing the domain's contents.

Usage: 

``python exportjson.py [-v] [-D|d] [-endpoint=<server_ip>]  [-port=<port] <domain>``
  
Options:
 * ``-v``: verbose, print request and response codes from server
 * ``-D``: suppress all data output
 * ``-d``: suppress data output for datasets (but not attributes)
 * ``-endpoint``: specify IP endpoint of server
 * ``-port``: port address of server [default 7253]

  Example - get 'tall' collection from HDF Group server:
       ``python exportjson.py tall.data.hdfgroup.org``
  Example - get 'tall' collection from a local server instance 
        (assuming the server is using port 5000):
        ``python exportjson.py -endpoint=127.0.0.1 -port=5000 tall.test.hdfgroup.org``
        
exporth5.py
-----------

This script makes a series of rest requests to the desired h5serv endpoint and
constructs a HDF5 file representing the domain's contents.

usage: ``python exporth5.py [-v] [-endpoint=<server_ip>]  [-port=<port] <domain> <filename>``

Options:
 * ``-v``: verbose, print request and response codes from server
 * ``-endpoint``: specify IP endpoint of server
 * ``-port``: port address of server [default 7253]
 
  Example - get 'tall' collection from HDF Group server, save to tall.h5:
       ``python exporth5.py tall.data.hdfgroup.org tall.h5``
  Example - get 'tall' collection from a local server instance 
        (assuming the server is using port 5000):
        ``python exporth5.py -endpoint=127.0.0.1 -port=5000 tall.test.hdfgroup.org tall.h5``

The following two utilities are located in hdf5-json submodule: hdf5-json/util.

jsontoh5.py
-----------

Converts a JSON representation of an HDF5 file to an HDF5 file.

Usage:

``jsontoh5.py [-h] <json_file> <h5_file>``

<json_file> is the input .json file.
<h5_file> is the output file (will be created by the script)

Options:
 * ``-h``: prints help message
 
h5tojson.py
-----------

This script converts the given HDF5 file to a JSON representation of the file.

Usage:

``python h5tojson.py [-h] -[D|-d] <hdf5_file>``

Output is a file the hdf5 file base name and the extension ``.json``.

Options:
 * ``-h``: prints help message
 * ``-D``: suppress all data output
 * ``-d``: suppress data output for datasets (but not attributes)
 
 
 




    
