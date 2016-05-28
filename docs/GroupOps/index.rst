####################
Groups
####################

Groups are objects that can be used to organize objects within a domain.  Groups contain
*links* which can reference other objects (datasets, groups or committed datatypes).
There are four different types of links that can be used:

* hard: A direct link to a group, dataset, or committed datatype object in the domain.
* soft: A symbolic link that gives a path to an object within the domain (object may or may not be present).
* external: A symbolic link to an object that is external to the domain.
* user-defined: A user-defined link (this implementation only provides title and class for user-defined links).

Groups all have attributes which can be used to store meta-data about the group.

Creating Groups
---------------

Use the :doc:`POST_Group` to create new Groups.  Initially the new group will have no
links and no attributes.


Getting information about Groups
--------------------------------

Use :doc:`GET_Group` to get information about a group: attribute count, link count,
creation and modification times.

To retrieve the UUIDs of all the groups in a domain, use :doc:`GET_Groups`.

To retrieve the links of a group use :doc:`GET_Links`. Use :doc:`GET_Link` to get
information about a specific link.

To get a group's attributes, use :doc:`../AttrOps/GET_Attributes`. 

Updating Links
---------------

To create a hard, soft, or external link, use :doc:`PUT_Link`.   

To delete a link use :doc:`DELETE_Link`.

*Note*: deleting a link doesn't delete the object that it refers to.


Deleting Groups
---------------
Use :doc:`DELETE_Group` to remove a group.  All attributes and links of the group
will be deleted.

*Note:* deleting a group will not delete any objects (datasets or other groups) that the
the group's links points to.  These objects may become *anonymous*, i.e. they are not
referenced by any link, but can still be accessed via ``GET`` request with the object
uuid.

List of Operations
------------------

.. toctree::
   :maxdepth: 1

   DELETE_Group
   DELETE_Link
   GET_Group
   GET_Groups
   GET_Link
   GET_Links
   POST_Group
   PUT_Link
    
    
