***************************
Common Response Headers
***************************

The following describes some of the common response lines returned by h5serv.

 * Status Line: the first line of the ressponse will always by: "``HTTP/1.1``" followed by 
    a status code (e.g. 200) followed by a reason message (e.g. "``OK``").  For errors, 
    an additional error message may be included on this line.
    
 * Content-Length: the response size in bytes.
 
 * Etag: a hash code that indicates the state of the requested resource.  If the client
    sees the same Etag value for the same request, it can assume the resource has not           
    changes since the last request.
    
 * Content-Type: the mime type of the response.  Currently always "``application/json``".
    
