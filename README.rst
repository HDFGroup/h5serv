h5serv - REST-based service for HDF5 data
===========================================

.. image:: https://travis-ci.org/HDFGroup/h5serv.svg?branch=develop
    :target: https://travis-ci.org/HDFGroup/h5serv

Introduction
------------
h5serv is a web service that implements a REST-based web service for HDF5 data stores
as described in the paper: http://hdfgroup.org/pubs/papers/RESTful_HDF5.pdf. 

Websites
--------

* Main website: http://www.hdfgroup.org
* Source code: https://github.com/HDFGroup/h5serv
* Mailing list: hdf-forum@lists.hdfgroup.org <hdf-forum@lists.hdfgroup.org>
* Documentation: http://h5serv.readthedocs.org


Installation
-------------

Setting up the server should take just a few minutes.  See h5serv/docs/Installation.rst 
for step by step instructions.

Writing Client Applications
----------------------------
As a REST service, clients be developed using almost any programming language.  The 
test programs under: h5serv/test/integ illustrate some of the methods for peforming
different operations using Python. 

Uninstalling
------------

h5serv does not modify anything in the system outside the directory where it was 
installed, so just remove the install directory and all contents to uninstall.

    
Reporting bugs (and general feedback)
-------------------------------------

Create new issues at http://github.com/HDFGroup/h5serv/issues for any problems you find. 

For general questions/feedback, please use the list (hdf-forum@lists.hdfgroup.org).
