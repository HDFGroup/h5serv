***************
Using Iteration
***************

There are some operations that may return an arbitrary large list of results. For 
example: ``GET /groups/<id>/attributes`` returns all the attributes of the 
group object with the given id.  It's possible (if not common in practice) that the 
group may contain hundreds or more attributes.

If you desire to retrieve the list of attributes in batches (say you are developing a 
user interface that has a "get next page" style button), you can use iteration.

This is accomplished by adding query parameters to the request the limit the number of
items returned and a marker parameter that identifies where the iteration should start 
off.

Let's flush out our example by supposing the group with UUID <id> has 1000 attributes 
named "a0000", "a0001", and so on.

If we'd like to retrieve just the first 100 attributes, we can add a limit value to the 
request like so:

``GET /groups/<id>/attributes?Limit=100``

Now the response will return attributes "a0000", "a0001", through "a0099". 

To get the next hundred, use the URL-encoded name of the last attribute received as the 
marker value for the next request:

``GET /groups/<id>/attributes?Limit=100&Marker="a0099"``

This request will return attributes "a0100", "a0101", through "a0199".

Repeat this pattern until less the limit items are returned.  This indicates that you've
completed the iteration through all elements of the group.

Iteration is also supported for links in a group, and the groups, datasets, and datatypes
collections.

Related Resources
=================

* :doc:`AttrOps/GET_Attributes`
* :doc:`GroupOps/GET_Groups`
* :doc:`GroupOps/GET_Links`
* :doc:`DatasetOps/GET_Datasets`
* :doc:`DatatypeOps/GET_Datatypes`

