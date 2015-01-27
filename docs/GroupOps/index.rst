####################
Groups
####################

Groups are objects that can be used to organize objects within a domain.  Groups contain
*links* which can reference other objects and attributes, which can contain metadata 
associated with the group.


Creating Groups
---------------

Use the :doc:`POST_Group` to create new Groups.  Initially the new group will have no
links and no attributes.

Adding Links
------------

Use :doc:`PUT_Link` to create hard, soft, or external links in the group.

Deleting Groups
---------------
Use :doc:`DELETE_Group` to remove a group.  All attributes and links of the group
will be deleted.

Operations
----------

.. toctree::
   :maxdepth: 2

   DELETE_Group
   DELETE_Link
   GET_Group
   GET_Groups
   GET_Link
   GET_Links
   POST_Group
   PUT_Link
    
    
