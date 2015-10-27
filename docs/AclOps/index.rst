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

Suppose a given dataset had the following ACL:

========   ====  ======   ======  ======  =======  ========
username   read  create   update  delete  readACL  writeACL
========   ====  ======   ======  ======  =======  ========
default    true  false    false   false   false    false
joe        true  false    true    false   false    false
ann        true  true     true    true    true     true
========   ====  ======   ======  ======  =======  ========

In this case unauthenticated (requests has no HTTP Authorization header) 
on the dataset would be handled as follows:

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
 
    
