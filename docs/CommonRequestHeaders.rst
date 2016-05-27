***********************
Common Request Headers
***********************

The following describe common HTTP request headers as used in h5serv:

 * Request line: The first line of the request, the format is of the form HTTP verb (GET, PUT, DELETE, or POST) followed by the path to the resource (e.g. /group/<uuid>.  Some operations take one or more query parameters (see relevant documentation) 
 * Accept: Specified the media type that is acceptable for the response.  Valid values are "application/json", and "*/*.  In addiiton, GET Value (see :doc:`DatasetOps/GET_Value`) supports the value "application/octet-stream"
 * Authorization: A string that provides the requester's credentials for the request. See  :doc:`Authorization`
 * Host: the domain (i.e. related collection of groups, datasets, and attributes) that the request should apply to
 
 Note: the host header can also be provided as a query paramter.  Example: https://data.hdfgroup.org:7258/?host=tall.test.data.hdfgroup.org 
