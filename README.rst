h5serv - REST-based service for HDF5 data
===========================================

Introduction
------------
h5serv is a web service that implements a REST-based web service for HDF5 data stores
as described in the paper: http://hdfgroup.org/pubs/papers/RESTful_HDF5.pdf. 
It is meant as "reference implementation" of the HDF5 Rest API, and may not be suitable
for use in production systems.  For example, there is currently no support for 
authentication.  Also, performance has not been a focus of this release.

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
* requests 2.3 or later

If you are not familiar with installing Python packages, the easy route is to 
use a package manager such as Anaconda (as described below).

If you have a git client installed on your system, you can directly download the h5serv 
source from github.com: git clone https://github.com/HDFGroup/h5serv.git.  Otherwise,
you can download a zip file of the source from GitHub (as described below).


Installing on Windows
---------------------

Anaconda from Continuum Analytics can be used to easily manage the package dependencies 
needed for HDF Server.  

In a browser go to: https://store.continuum.io/downloads and click the "Windows 64-bit 
Python 2.7 Graphical Installer" button.

Install Anaconda using the default options.

Once Anaconda is installed select "Anaconda Command Prompt" from the start menu.

In the command window that appears, create a new anaconda environment using the following command:
conda create -n testconda python=2.7 h5py twisted tornado requests pytz

Answer 'y' to the prompt, and the packages will be fetched.

In the same command window, run: activate h5serv

In a browser go to: https://github.com/HDFGroup/h5serv and click the "Download ZIP"
button (right side of page).  Save the file as "h5serv.zip" to your Downloads directory.

In Windows Explorer, right-click on the zip file and select "Extract All...".  You can 
choose any folder as the destination.

In the Anaconda window, cd to the folder you extracted the source files to.

From here cd to "h5serv-master/server".

Run: python app.py
You should see the output: "Starting event loop on port: 5000".

You may then see a security alert: "Windows Firewall has blocked some features of this 
program".  Click "Allow access" with the default option (Private network access).

At this point the server is running, waiting on any requests being sent to port 5000.
Go to the "verification" section below to try out the service.

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


Verification
-------------

To verify that h5serv was installed correctly, you can run the test suite included
with the installation.  

Open a new shell (on Windows, run "Annaconda Command Prompt" from the start menu).

In this shell, run the following commands:

* Conda activate h5serv  (just: activate h5serv on Windows)
* cd <h5serv installation directory>
* cd test
* python testall.py

All tests should report OK.  

Importing Data Files
--------------------

Copy any HDF5 datafiles you wish to be exposed by the server to the h5serv/data directory. 
Change the permission on the file to read-only if you do not wish to allow the files to
be modified by server PUT/POST/DELETE requests.

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
