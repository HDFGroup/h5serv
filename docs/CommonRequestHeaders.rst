***********************
Common Request Headers
***********************

The following describe common HTTP request headers as used in h5serv:

 * Request line: The first line of the request, the format is of the form HTTP verb (GET,
    PUT, DELETE, or POST) followed by the path to the resource (e.g. /group/<uuid>.  Some
    operations take one or more query parameters (see relevant documentation).
    
 * Authorization: A string that provides the requester's credentials for the request. *Note:*
    currently authorization is not implemented and presence or absence of the line will have
    no effect.
    
 * Host: the domain (i.e. related collection of groups, datasets, and attributes) that 
    the request should apply to.  