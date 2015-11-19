import errno


def errNoToHttpStatus(error_code):
    """Convert IOError error numbers to HTTP equivalent status codes."""
    httpStatus = 500
    if error_code == errno.EINVAL:  # formerly EBADMSG
        httpStatus = 400  # bad request
    elif error_code == errno.EACCES:
        httpStatus = 401   # unauthorized
    elif error_code == errno.EPERM:
        httpStatus = 403  # forbidden
    elif error_code == errno.ENXIO:
        httpStatus = 404  # Not Found
    elif error_code == errno.EEXIST:
        httpStatus = 409   # conflict
    elif error_code == errno.ENOENT:  # formerly EIDRM
        httpStatus = 410   # Gone
    elif error_code == errno.EIO:
        httpStatus = 500   # Internal Error
    elif error_code == errno.ENOSYS:
        httpStatus = 501   # Not implemented

    return httpStatus
