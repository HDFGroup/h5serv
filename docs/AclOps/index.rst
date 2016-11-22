####################
Access Control List
####################

Access Control List (ACL) are key-value stores that can be used to manage what operations can 
be performed by which user on group, dataset, or committed type objects.  Operations on other 
objects (e.g. links, dataspace, or attributes) use the ACL of the object they belong to.

Each ACL consists of 1 or more items in the form:

(username, read, create, update, delete, readACL, updateACL)

where username is a string, and read, create, update, delete, readACL, updateACL are booleans.
There flags have the following semantics when the given username is provided in the http
Authorization header:

* read: The given user is authorized for read access to the resource (generally all GET requests)
* create: The given user is authorized to create new resources (generally POST or PUT requests)
* update: The given user is authorized to modified a resource (e.g. :doc:`../DatasetOps\PUT_Value`)
* delete: The given user is authorized to delete a resource (e.g. Delete a Group)
* readACL: The given user is authorized to read the ACLs of a resource
* updateACL: The given user is authorized to modify the ACLs of a resource

A special username 'default' is used to denote the access permission for all other users who
or not list in the ACL (including un-authenticated requests that don't provide a username).

Example
-------

Suppose a given dataset has the following ACL:

========   ====  ======   ======  ======  =======  ========
username   read  create   update  delete  readACL  writeACL
========   ====  ======   ======  ======  =======  ========
default    true  false    false   false   false    false
joe        true  false    true    false   false    false
ann        true  true     true    true    true     true
========   ====  ======   ======  ======  =======  ========

This ACL would enable anyone to read (perform GET requests).  User 'joe' would be able 
to read and update (modify values in the dataset).  While user 'ann' would have full 
control to do any operation on the dataset (including modifying permissions for herself or
other users).

The following unauthenticated (no HTTP Authorization header) 
requests on the dataset would be granted or denied as follows:

* GET /datasets/<id> - granted (returns HTTP Status 200 - OK)
* POST /datasets/<id>/value - granted (returns HTTP Status 200 - OK)
* PUT /datasets/<id>/shape) - denied (returns HTTP Status 401 - Unauthorized)
* PUT /datasets/<id>/attributes/<name> - denied (returns HTTP Status 401 - Unauthorized)
* DELETE /datasets/<id>  - denied (returns HTTP Status 401 - Unauthorized)

Next the same set of requests are sent with 'joe' as the user in the HTTP Authorization header:

* GET /datasets/<id> - granted (returns HTTP Status 200 - OK)
* POST /datasets/<id>/value - granted (returns HTTP Status 200 - OK)
* PUT /datasets/<id>/shape) - grant (returns HTTP Status 200 - OK)
* PUT /datasets/<id>/attributes/<name> - denied (returns HTTP Status 403 - Forbidden)
* DELETE /datasets/<id>  - denied (returns HTTP Status 403 - Forbidden)

Finally the same set of requests are sent with 'ann' as the user:

* GET /datasets/<id> - granted (returns HTTP Status 200 - OK)
* POST /datasets/<id>/value - granted (returns HTTP Status 200 - OK)
* PUT /datasets/<id>/shape) - grant (returns HTTP Status 200 - OK)
* PUT /datasets/<id>/attributes/<name> - denied (returns HTTP Status 201 - Created)
* DELETE /datasets/<id>  - denied (returns HTTP Status 200 - OK)
 
Note: HTTP Status 401 basically says: "you can't have access until you tell me who your are", 
while HTTP Status 403 says: "I know who you are, but you don't have permissions to access this
resource."

Root ACL Inheritance
--------------------

In many cases it will be desired to have a default ACL that applies to each resource in the domain.
This can be accomplished by defining an ACL for the root group.  This will control the access 
rights for any resource unless of ACL is present in that resource for the requesting user.

The default ACL can be read or updated by forming a request with a uri that includes the root group id, 
i.e.: "/groups/<root_id>/acls", or by using the uri path for the domain, i.e. "/acls".


For a given user then, the permissions for a resource are found in the following way:

#. If the user is present in the resources ACL, those permissions are used
#. If no user is present in the resources ACL, but is present in the root group, those permissions are used
#. Otherwise, if a 'default' user is present in the resource ACL, those permissions are used
#. If a 'default' user is not present in the resource ACL, but is present in the root ACL, those permissions are used
#. If no 'default' user is present in the root ACL, the permissions defined in the 'default_acl' config is used
  
List of Operations
------------------

.. toctree::
   :maxdepth: 1

   GET_ACL
   GET_ACLs
   PUT_ACL
    
    
