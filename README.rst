h5serv - REST-based service for HDF5 data
===========================================

Websites
--------

* Main website: http://www.hdfgroup.org
* Source code: https://github.com/HDFGroup/h5serv
* Mailing list: hdf-forum@lists.hdfgroup.org <hdf-forum@lists.hdfgroup.org>
* Documentation: tbd


Prerequisites
-------------

You need, at a minimum the following Python packages:

* Python 2.7
* NumPy 1.6.1 or later
* h5py 2.3.1 or later
* twisted 14.0 or later
* tornado 4.0.2 or later

You will also need a git client to download the source code.


Installing on Windows
---------------------

tbd

Installing on Linux/Mac OS X
-----------------------------

To install the server run the following from the command line::

    # get source code
    git clone https://github.com/HDFGroup/h5serv.git 
    # go to the server directory 
    cd h5serv/server
    # run the server
    python app.py
    # server is now running on port 5000

    # verify the installation (in a new window)
    cd h5serv/test
    ./testall.sh

    
Reporting bugs
--------------

Open a bug at http://github.com/HDFGroup/h5serv/issues.  For general questions, ask
on the list (hdf-forum@lists.hdfgroup.org).
