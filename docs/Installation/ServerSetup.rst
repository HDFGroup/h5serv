###################
Installing h5serv
###################

You should find h5serv quite easy to setup.  The server (based on Python Tornado) is 
self-contained, so you will not need to setup Apache or other web server software to utilize
h5serv.


Prerequisites
-------------

A computer running a 64-bit version of Windows, Mac OS X, or Linux.

You will also need the following Python packages:

* Python 2.7 or later
* NumPy 1.10.4 or later
* h5py 2.5 or later
* tornado 4.0.2 or later
* requests 2.3 or later (for client tests)

If you are not familiar with installing Python packages, the easiest route is to 
use a package manager such as Anaconda (as described below).

If you have a git client installed on your system, you can directly download the h5serv 
source from GitHub: ``git clone --recursive https://github.com/HDFGroup/h5serv.git``.  
Otherwise, you can download a zip file of the source from GitHub (as described below).


Installing on Windows
---------------------

Anaconda from Continuum Analytics can be used to easily manage the package dependencies 
needed for HDF Server.  

In a browser go to: http://continuum.io/downloads and click the "Windows 64-bit 
Python 2.7 Graphical Installer" button.

Install Anaconda using the default options.

Once Anaconda is installed select "Anaconda Command Prompt" from the start menu.

In the command window that appears, create a new anaconda environment using the following command:
``conda create -n h5serv python=2.7 h5py tornado requests pytz``

Answer 'y' to the prompt, and the packages will be fetched.

In the same command window, run: ``activate h5serv``

Download the hdf5-json project: ``git clone https://github.com/HDFGroup/hdf5-json.git`` .
Alternatively, in a browser go to: https://github.com/HDFGroup/hdf5-json and click the 
"Download ZIP" button (right side of page).   Download the zip file and extract to
the destination directory of your choice.  

Next, cd to the hdf5-json folder and run: ``python setup.py install``.

Download the h5serv project: ``git clone https://github.com/HDFGroup/h5serv.git`` .
Alternatively, download the source zip as described above. 

Next, in the command window, cd to the folder you extracted the source files to.

From here cd to "h5serv-master/server" (or just server if you used git).

Run: python app.py
You should see the output: "Starting event loop on port: 5000".

You may then see a security alert: "Windows Firewall has blocked some features of this 
program".  Click "Allow access" with the default option (Private network access).

At this point the server is running, waiting on any requests being sent to port 5000.
Go to the "verification" section below to try out the service.

Installing on Linux/Mac OS X
-----------------------------

Anaconda from Continuum Analytics can be used to easily manage the package dependencies 
needed for HDF Server.  

In a browser go to: http://continuum.io/downloads and click the "Mac OS X 64-bit 
Python 2.7 Graphical Installer" button for Mac OS X or: "Linux 64-bit Python 2.7".

Install Anaconda using the default options.

Once Anaconda is installed, open a new shell and run the following on the command line:

``conda create -n h5serv python=2.7 h5py tornado requests pytz``

Answer 'y' to the prompt, and the packages will be fetched.

In the same shell, run: ``source activate h5serv``

Download the hdf5-json project: ``git clone https://github.com/HDFGroup/hdf5-json.git`` .
Alternatively, in a browser go to: https://github.com/HDFGroup/hdf5-json and click the 
"Download ZIP" button (right side of page).   Download the zip file and extract to
the destination directory of your choice.  

Next, cd to the hdf5-json folder and run: ``python setup.py install``.

Download the h5serv project: ``git clone https://github.com/HDFGroup/h5serv.git`` .
Alternatively, download the source zip as described above. 

Next, cd to the h5serv folder.

From here cd to "server" (or "h5serv-master/server" if you extracted from ZIP file).

Run: ``python app.py``
You should see the output: "Starting event loop on port: 5000".

At this point the server is running, waiting on any requests being sent to port 5000.
Go to the "verification" section below to try out the service.


Verification
-------------

To verify that h5serv was installed correctly, you can run the test suite included
with the installation.  

Open a new shell (on Windows, run "Annaconda Command Prompt" from the start menu).

In this shell, run the following commands:

* source activate h5serv  (just: activate h5serv on Windows)
* cd <h5serv installation directory>
* cd test
* python testall.py

All tests should report OK. 

Server Configuration
--------------------

The file h5serv/server/config.py provides several configuration options that can be
used to customize h5serv.  Each of the options can be changed by:

 * Changing the value in the config.py file and re-starting the service.
 * Passing a command line option to app.py on startup. E.g. ``python app.py --port=7253``
 * Setting an environment variable with the option name in upper case.  E.g. ``export PORT=5000; python app.py``

The config options are:

port 
^^^^
The port that h5serv will listen on.  Change this if 5000 conflicts with another service.

Default: 5000
 
debug 
^^^^^
If ``True`` the server will report debug info (e.g. a stack trace) to the requester on 
error.  If  ``False``, just the status code and message will be reported. 

Default: ``True``

datapath
^^^^^^^^
A path indicating the directory where HDF5 will be be stored.

*Note*: Any HDF5 file content that you put in this directory will be exposed via the
server REST api.

Default: ``../data/``

hdf5_ext
^^^^^^^^

The extension to assume for HDF5 files.  The rest requests don't assume an extension, so
a request such as:

.. code-block:: http

  GET /
  HOST: tall.data.hdfgroup.org
  
Translates to: "Get the file tall.h5 in the directory given by datapath".

Default: ``.h5``
 

Data files
----------

Copy any HDF5 files you would like exposed by the service to the datapath directory
(h5serv/data).  If you do not wich to have the files updatable by the service make the 
files read-only.

*Note:* Do not modify files once they have been placed in the datapath directory.  h5serv
inventories new files on first access, but won't see some changes (e.g. new group is created)
made to the file outside the REST api.
     
