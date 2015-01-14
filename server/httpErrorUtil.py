import errno
"""
    Convert IOError error numbers to HTTP equivalent status codes
"""    
def errNoToHttpStatus(error_code):
    httpStatus = 500
    if error_code == errno.EBADMSG:
        httpStatus = 400  # bad request
    elif error_code == errno.EACCES:
        httpStatus = 401   # unauthorized
    elif error_code == errno.EPERM:
        httpStatus = 403  # forbidden
    elif error_code == errno.ENXIO:
        httpStatus = 404  # Not Found
    elif error_code == errno.EEXIST:
        httpStatus = 409   # conflict
    elif error_code == errno.EIDRM:
        httpStatus = 410   # Gone
    elif error_code == errno.EIO:
        httpStatus = 500   # Internal Error
    elif error_code == errno.ENOSYS:
        htpStatus = 501   # Not implemented
        
    return httpStatus
        
    
