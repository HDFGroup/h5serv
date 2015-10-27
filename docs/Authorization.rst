*********************************
Authorization and Authentication
*********************************

h5serv supports HTTP Basic authentication to authenticate users be comparing an encrypted 
username and password against a value stored within a password file.  
(See :doc: `AdminTools` to create a password file and add user accounts.) 

If neither the requested object (Group, Dataset, or Committed Datatype) nor the object's root group
has an Access Control List (ACL), authorization is not required and no authentication string
needs to be suplied. 

If the requested object (or object's root group), does have an ACL, authorization may be required,
and the requestor may need to provide an Authorization header in the request.
 
