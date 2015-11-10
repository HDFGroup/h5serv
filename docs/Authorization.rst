*********************************
Authorization and Authentication
*********************************

Request Authentication
-----------------------
h5serv supports HTTP Basic authentication to authenticate users by comparing an encrypted 
username and password against a value stored within a password file.  
(See :doc:`AdminTools` to create a password file and add user accounts.) 

If neither the requested object (Group, Dataset, or Committed Datatype) nor the object's root group
has an Access Control List (ACL), authorization is not required and no authentication string
needs to be supplied. See :doc:`../AclOps`) for information on how to use ACL's.

If the requested object (or object's root group), does have an ACL, authorization may be required 
(if the object is not publically readable),
and if so the requestor will need to provide an Authorization header in the request.  If 
authoriazation is required, but not provided, the server will return an HTTP Status of 401 - 
Unauthorized.

If authorization is required (i.e. a 401 response is received), the client should provide an authorization header in the
http request which conveys the userid and password.

The authorization string is constructed as follows:

 1. Username and password are combined into a string "username:password". Note that username cannot contain the ":" character
 2. The resulting string is then encoded using the RFC2045-MIME variant of Base64, except not limited to 76 char/line
 3. The authorization method and a space i.e. "Basic " is then put before the encoded string

For example, if the user agent uses 'Aladdin' as the username and 'open sesame' as the password then the field is 
formed as follows:
``Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==``.  When passwords are being sent over an open
network, SSL connections should be used to avoid "man in the middle attacks".  The Base64 encoding is
easily reversible and if using plain http there is no assurance that the password will not be compromised.

If the authorization string is validated, the server will verify the request is authorized as
per the object's ACL list.  If not authorized a http status 403 - Forbidden will be returned.


User ids and passwords
----------------------

User ids and passwords are maintained in an HDF5 file referenced in the server config: 
'password_file'.  The admin tool (See :doc:`AdminTools`) script: update_pwd.py can be used 
to create new users and update passwords.


 
