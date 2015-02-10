**************
DNS Setup
**************

The dns directory contains a simple dynamic dns server server.  Setting it up takes some
additional work, but it will be useful if you would like to display data from h5serv using a web 
browser.  If you are only accessing h5serv programmatically, it is not needed.

Background
-----------

The HDF5 REST api exposes each HDF5 file as a domain object.  E.g.
If the file "hdf_data.h5" is in the data directory, and the 'domain' config in server.py
is set to "mydata.myorg.org", the file is mapped to the domain path: 
*hdf_data.mydata.myorg.org*.

When the HDF REST Service is accessed programmatically, the http request can be sent 
to the endpoint where h5serv is running and local_dns.py is not needed. In this case it is 
important that the request host header provide the domain path above.

Example:

.. code-block:: http

    GET / HTTP/1.1
    Host: hdf_data.myserv.myorg.org
    
The service will look at the Host header line to determine which HDF5 file the ``GET /`` 
request refers to and return the appropriate response. 

However, if you type ``http://hdf_data.mydata.myorg.org`` in your favorite web browser you
will most likely get a DNS lookup failure.  These is because the DNS server your browser
is talking to doesn't know how to resolve the domain name: ``hdf_data.mydata.myorg.org``.  
You can verify this by running: ``nslookup hdf_data.mydata.myorg.org``, you should see a response:
``** server can't find hdf_data.mydata.myorg.org``.

You can imagine getting around this by configuring special DNS lookup rules for each 
HDF5 file managed by h5serv, but this would require a config update every time a new 
file was created (say by a ``PUT /`` request).  

The DNS server included with this release, local_dns.py, gets around this by simply
responding to any DNS request with the configured base domain name to the IP address of h5serv.
Any request that doesn't map to the base domain name will be forwarded to a regular DNS
server.

So a request to resolve ``hdf_data.myserv.myorg.org`` would return the IP address of h5serv, 
while a request to resolve ``www.google.com`` would be forwarded to a standard DNS server.

Running local_dns
-----------------

Before starting the local_dns server, update the local_ip, and default_dns config values 
in config.py to what makes sense for your network.  Using the above example, domain would 
be myserv.myorg.org and local_ip can be left as just 127.0.0.1 if we are running h5serv and 
local_dns on the same host.

Next, start the local_dns server: ``sudo python local_dns.py``

*Note:* You will need to run as root since local_dns using port 53 (the standard DNS port).

Now when you run: ``nslookup hdf_data.mydata.myorg.org 127.0.0.1``, you should see a response:
``Non-authoritative answer:``
``Name: hdf_data.mydata.myorg.org``
``Address: 127.0.0.1``

local_dns has resolved the domain name hdf_data.mydata.myorg.org to the local ip address.

If at this point you modify your machine's dns configuration to use the IP address where
local_dns.py is running, you'll be able to use: hdf_data.mydata.myorg.org/ as a browser
url and see the JSON response.

Integrating with you organization's network
-------------------------------------------
If you would like *any* computer to recognize the domain name of hdf_data.myserv.myorg.org
you will need to have your system admin update your organization's master DNS server to 
configure "myserv" as a zone of "myorg".  In our example, this would have the effect
of any sub-domain of "myserv.myorg" managed by its own DNS server.  In our case, the DNS
server will be local_dns.py.  Details of how zone's are setup will vary based on 
what DNS server software your network is running.  Your sysadmin should be able to help.

 
An Example
----------
As an example of how this would work we can look at the h5serv instance setup by The HDF
Group.  Entering <http://tall.data.hdfgroup.org:7253/> in your browser will return the JSON
domain response for tall.h5.  

If we trace the chain of events in displaying this page it
would be something like this (the actual IP address may be different than what you see here):

 #. User enters ``http://tall.data.hdfgroup.org:7253`` in the browser
 #. The browser sends the domain "tall.data.hdfgroup.org" to its normal DNS server
 #. If the DNS server is not familiar with "hdfgroup.org" it forwards the request to the root domain server
 #. The root domain server resolves "hdfgroup.org" the IP address 50.28.50.143
 #. The HDFGroup DNS server at 50.28.50.143 gets the request to resolve "data.hdfgroup.org"
 #. The HDF Group DNS server sees that "data" maps to a zone managed by the DNS server (local_dns) at IP address 54.174.38.12
 #. Finally, the local_dns.py service gets the DNS request and resolves the name "tall.data.hdfgroup.org" and returns the IP address 54.174.38.12 and returns the requested IP to the browser
 #. With the dns name resolved, the browser sends the original http request to port 7253 on the machine with IP address 54.174.38.12.
 #. This request is processed by h5serv which returns a http status of 200 followed by the response body
 #. The browser renders the response:
 
 
.. code-block:: json

  {
  root: "345239f2-963f-11e4-b8cf-06fc179afd5e",
  created: "2015-01-07T07:31:33.294348Z",
  lastModified: "2015-01-07T07:31:33.294348Z",
  hrefs: [
    {href: "http://tall.data.hdfgroup.org:7253/", rel: "self"},
    {href: "http://tall.data.hdfgroup.org:7253/datasets", rel: "database"},
    {href: "http://tall.data.hdfgroup.org:7253/groups", rel: "groupbase"},
    {href: "http://tall.data.hdfgroup.org:7253/datatypes",rel: "typebase"},
    {href: "http://tall.data.hdfgroup.org:7253/groups/345239f2-963f-11e4-b8cf-06fc179afd5e",rel: "root"}
   ]
  }





