h5serv - REST-based service for HDF5 data
===========================================

.. image:: https://travis-ci.org/HDFGroup/h5serv.svg?branch=develop
    :target: https://travis-ci.org/HDFGroup/h5serv

Introduction
------------
h5serv is a web service that implements a REST-based web service for HDF5 data stores
as described in the paper: http://hdfgroup.org/pubs/papers/RESTful_HDF5.pdf. 

Notice
------
h5serv has been deprecated.  Users looking for a RESTful way of accessing HDF data should 
use HSDS (https://github.com/HDFGroup/hsds) instead.

Websites
--------

* Main website: http://www.hdfgroup.org
* Source code: https://github.com/HDFGroup/h5serv
* Mailing list: hdf-forum@lists.hdfgroup.org <hdf-forum@lists.hdfgroup.org>
* Documentation: http://h5serv.readthedocs.org


Quick Install
-------------

Install Python (2.7 or later) and the following packages:

* NumPy 1.10.4 or later
* h5py 2.5 or later
* tornado 4.0.2 or later
* watchdog 0.8.3 or later
* requests 2.3 or later (for client tests)

Clone the hdf5-json project: ``git clone https://github.com/HDFGroup/hdf5-json.git`` .
Next, cd to the hdf5-json folder and run: ``python setup.py install``.

Clone this project: ``git clone https://github.com/HDFGroup/h5serv.git``.

Running the Server
------------------

Start the server:  ``cd h5serv; python h5serv``.

By default the server will listen on port 5000.  The port and and several other defaults can be modified
with command line options.  For example to use port 8888 run:  ``python h5serv --port=8888``.

See test cases for examples of interacting with the server.  Run: ``python testall.py`` from the test directory 
to run through the entire test suite.

Also, the interface (at least as far as read requests) can be explored in a browser. Go to: http://127.0.0.1:5000/.  
A JSON browser plugin will be helpful for formatting responses from the server to be more human readable.

See h5serv/docs/Installation.rst for step by step install instructions.

Running with Docker
-------------------

To run h5serv as a docker container you just need to install Docker (no Python, h5py, etc. needed).

* Install docker: https://docs.docker.com/installation/#installation.
* Run the h5serv image: ``docker run -p 5000:5000 -d -v <mydata>:/data hdfgroup/h5serv`` where <mydata> is the folder path that contains any HDF5 files you want to made available through the h5serv REST API.  Since requests to the server can modify (or delete!) content, you probably want to create a new folder and copy files to it.
* Go to http://192.168.99.100:5000/ in your browser to verify the server is up and running (replace 192.168.99.100 with the IP address of the system or VM that is running the container).

Writing Client Applications
----------------------------
As a REST service, clients be developed using almost any programming language.  The 
test programs under: h5serv/test/integ illustrate some of the methods for peforming
different operations using Python. 

The related project: https://github.com/HDFGroup/h5pyd provides a (mostly) h5py-compatible 
interface to the server for Python clients.


Uninstalling
------------

h5serv does not modify anything in the system outside the directory where it was 
installed, so just remove the install directory and all contents to uninstall.

    
Reporting bugs (and general feedback)
-------------------------------------

Create new issues at http://github.com/HDFGroup/h5serv/issues for any problems you find. 

For general questions/feedback, please use the list (hdf-forum@lists.hdfgroup.org).
