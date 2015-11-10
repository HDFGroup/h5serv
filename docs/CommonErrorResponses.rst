***************************
Common Error Responses
***************************

For each request, h5serv returns a standard HTTP status code as described below.
In general 2xx codes indicate success, 3xx codes some form of redirection, 4xx codes 
client error, and 5xx codes for server errors.  In addition to the numeric code, h5serv
will return an informational message as part of the response providing further 
information on the nature of the error.

 * ``200 OK`` - The request was completed successfully
 * ``201 Created`` - The request was fulfilled and a new resource (e.g. group, dataset, attribute was created) 
 * ``400 Bad Request`` - The request was not structured correctly (e.g. a required key was missing).
 * ``401 Unauthorization`` - Use authentitcation is required, supply an Authentication header with valid user and password
 * ``403 Forbidden`` - The requesting user does not have access to the requested resource
 * ``404 Not Found`` - The requested resource was not found (e.g. ``GET /groups/<id>`` where <id> was not a valid identifier for a group in the domain).
 * ``409 Conflict`` - This error is used with PUT requests where the resources cannot be created because there is an existing resource with the same name (e.g. PUT / where the requested domain is already present).
 * ``410 Gone`` - The resource requested has been recently deleted.
 * ``500 Internal Error`` - An unexpected error that indicates some problem occurred on the server.
 * ``501 Not Implemented`` - The request depends on a feature that is not yet implemented.
