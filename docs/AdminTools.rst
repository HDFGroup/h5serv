###################
Admin Tools
###################

The scripts described here are intended to be run on the server by "privileged" users.  These are all
located in the ``util\admin`` directory.

makepwd_file.py
---------------

This script creates an initial password file "passwd.h5".  The password file will be used to manage 
http basic authentication.  After creation, move the file into the location referenced by 
the 'password_file' configuration value.

Usage:

``python makepwd_file.py``

Use the update_pwd.py utility to create user accounts.

update_pwd.py
-------------

This script can be used to add users and passwords to the password file, list information about
one or more users, or to update a user's information (e.g. change the password).

Usage: 

``python update_pwd.py [-h] [-r] [-a] [-f FILE] [-u USER] [-p PASSWD]``
  
Options:
 * ``-h``: print usage information
 * ``-r``: update a user's entry
 * ``-a``: add a user (requires -u and -p options)
 * ``-f``: password file to be used
 * ``-u``: print/update information for specified user (otherwise show all users)
 * ``-p``: password to be set for the given users
 

  Example - list all users
       ``python update_pwd.py -f passwd.h5``
  Example - list user 'bob':
       ``python update_pwd.py -f passwd.h5 -u bob``
  Example - add a user 'ann':
       ``python update_pwd.py -f passwd.h5 -a -u ann -p mysecret``
  Example - changes password for user 'paul':
       ``python update_pwd.py -f passwd.h5 -r -u paul -p mysecret2``
       
 Note, there is no way to display the passwords for any user.  If a password is 
 lost, that users password must be reset.
  
        
getacl.py
-----------

This script displays ACL's of a given file or object within a file.

usage: ``python getacl.py [-h] [-file <file>]  [-path <h5path>] [userid_1, userid_2, ... userid_n]``

Options:
 * ``-h``: print usage information
 * ``-file``: (required) data file to be used 
 * ``-path``: h5path to object.  If not present, ACLs of the root group will be displayed
 * ``<userids>``: list of user ids to fetch ACLs for.  If not present, ACLs for all users will be printed

 
  Example - get all ACLs of tall.h5 root group
       ``python getacl.py -file ../../data/tall.h5``
  Example - get ACLs for userid 123 of root group in tall.h5
       ``python getacl.py -file ../../data/tall.h5 123``
  Example - get ACLs for userid 123 of the dataset identified by path '/g1/g1.1/dset1.1.1'
       ``python getacl.py -file ../../data/tall.h5 -path /g1/g1.1/dset1.1.1``
       
setacl.py
-----------

This script creates or modifies ACL's of a given file or object within a file.

usage: ``python setacl.py [-h] [-file <file>]  [-path <h5path>] [+-][crudep] [userid_1, userid_2, ... userid_n]``

Options:
 * ``-h``: print usage information
 * ``-file``: (required) data file to be used 
 * ``-path``: h5path to object.  If not present, ACLs of the root group will be modified
 * ``[+-][crudep]``: add (+) or remove (-) permisions for Create (c), Read (r), Update (u), Delete (d), rEadAcl (e), and Putacl (p)
 * ``<userids>``: list of user ids to sets ACLs for.  If not present, ACLs for the default user will be set.

 
  Example - set default permission of tall.h5 to read only
       ``python setacl.py -file ../../data/tall.h5 +r-cudep``
  Example - give userid 123 full control of tall.h5:
       ``python setacl.py -file ../../data/tall.h5 +crudep 123``
  Example - give userid read/update access to dataset at path '/g1/g1.1/dset1.1.1' 
       ``python setacl.py -file ../../data/tall.h5 -path /g1/g1.1/dset1.1.1 +ru-cdep 123``
         
 
 
 




    
