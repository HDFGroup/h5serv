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
* watchdog 0.8.3 or later
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

Install the watchdog package (this is currently not available through Anaconda):
``pip install watchdog``

Download the hdf5-json project: ``git clone https://github.com/HDFGroup/hdf5-json.git`` .
Alternatively, in a browser go to: https://github.com/HDFGroup/hdf5-json and click the 
"Download ZIP" button (right side of page).   Download the zip file and extract to
the destination directory of your choice.  

Next, cd to the hdf5-json folder and run: ``python setup.py install``.

Download the h5serv project: ``git clone https://github.com/HDFGroup/h5serv.git`` .
Alternatively, download the source zip as described above. 

Next, in the command window, cd to the folder you extracted the source files to.

Run: ``python h5serv``
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

Install the watchdog package (this is currently not available through Anaconda):
``pip install watchdog``

In the same shell, run: ``source activate h5serv``

Download the hdf5-json project: ``git clone https://github.com/HDFGroup/hdf5-json.git`` .
Alternatively, in a browser go to: https://github.com/HDFGroup/hdf5-json and click the 
"Download ZIP" button (right side of page).   Download the zip file and extract to
the destination directory of your choice.  

Next, cd to the hdf5-json folder and run: ``python setup.py install``.

Download the h5serv project: ``git clone https://github.com/HDFGroup/h5serv.git`` .
Alternatively, download the source zip as described above. 

Next, in the command window, cd to the folder you extracted the source files to.

Run: ``python h5serv``
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

The file ``h5serv/server/config.py`` provides several configuration options that can be
used to customize h5serv.  Each of the options can be changed by:

 * Changing the value in the config.py file and re-starting the service.
 * Passing a command line option to ``h5serv`` on startup. E.g. ``python h5serv --port=7253``
 * Setting an environment variable with the option name in upper case.  E.g. ``export PORT=5000; python h5serv``

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
A path indicating the directory where HDF5 files will be be stored.

*Note*: Any HDF5 file content that you put in this directory will be exposed via the
server REST api (unless the domain's ACL is configured to prevent public access, see: 
:doc:`../AclOps`).

Default: ``../data/``

public_dir
^^^^^^^^^^
A list of directories under datapath which will be visible to any autenticated user's 
request.

Default: ``['public', 'test']``

domain
^^^^^^
The base DNS path for domain access  (see comment to hdf5_ext config option).

Default. ``hdfgroup.org``

hdf5_ext
^^^^^^^^

The extension to assume for HDF5 files.  The REST requests don't assume an extension, so
a request such as:

.. code-block:: http

  GET /
  HOST: tall.data.hdfgroup.org
  
Translates to: "Get the file tall.h5 in the directory given by datapath".

Default: ``.h5``
 
toc_name
^^^^^^^^

Name of the auto-generated HDF5 that provides a "Table Of Contents" list of all HDF5
files in the datapath directory and sub-directories.

Default: ``.toc.h5``

home_dir
^^^^^^^^

A directory under data_path that will be the parent directory of user home directores.
For example if ``datapath`` is ``../data``, ``home_dir`` is ``home``, the authenticated request
of ``GET /`` for userid ``knuth`` would return a list of files in the directory: 
``../data/home/knuth``.

Default: ``home``

ssl_port
^^^^^^^^

The SSL port the server will listen on for HTTPS requests.

Default: 6050

ssl_cert
^^^^^^^^

Location of the SSL cert.

default: 

ssl_key
^^^^^^^

The SSL key.

default:

ssl_cert_pwd
^^^^^^^^^^^^

The SSL cert password

default:

password_uri
^^^^^^^^^^^^

Resource path to be used for user authentication.
Currently two methods are supported:

HDF5 Password file: An HDF5 that contains userids and (encrypted) passwords.
See: :doc:`../AdminTools`.  In this case the password_uri config is a path
to the password file.

MongoDB: A MongoDB database that contains a "users" collection of userids and 
passwords.  In this case the password_uri would be of the form: 
``mongodb://<mongo_ip>:<port>`` where ``<mongo_ip>`` is the IP 
address of the host running the mongo database and ``<port>`` is the port of 
the mongo database (typically 27017).

default: ``../util/admin/passwd.h5``

mongo_dbname
^^^^^^^^^^^^

Mongo database named used for MongoDB-based authentication as described above.

default: ``hdfdevtest``

static_url
^^^^^^^^^^

URI path that will be used to map any static HTML content to be displayed by the server.

default: ``/views/(.*)``

static_path
^^^^^^^^^^^

File path for files (i.e. regular HTML files) to be hosted statically.

default: ``../static``

cors_domain
^^^^^^^^^^^

Domains to allow for CORS (cross-origin resource sharing).  Use ``*`` to allow
any domain, None to disallow.

default: ``*``

log_file
^^^^^^^^

File path for server log files.  Set to None to have logout go to standard out.

log_level
^^^^^^^^^

Verbosity level for logging.  One of: ``ERROR, WARNING, INFO, DEBUG, NOTSET``.

default: ``INFO``

background_timeout
^^^^^^^^^^^^^^^^^^

Time interval in milliseconds to check for updates in the datapath folder (e.g. a file
that is added through some external process).  Set to 0 to disable background processsing.

default: 1000


Data files
----------

Copy any HDF5 files you would like exposed by the service to the datapath directory
(h5serv/data).  If you do not wish to have the files updatable by the service make the 
files read-only.

On the first request to the service, a Table of Contents (TOC) file will be generated which
will contain links to all HDF5 files in the data folder (and sub-folders).

*Note:* Do not modify files once they have been placed in the datapath directory.  h5serv
inventories new files on first access, but won't see some changes (e.g. new group is created)
made to the file outside the REST api.

*Note: HDF5 that are newly created (copied into) the datapath directory will be "noticed"
by the service and added into the TOC.
