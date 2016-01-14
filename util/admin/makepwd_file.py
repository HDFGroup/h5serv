import h5py
import numpy as np

file_name = 'passwd.h5'
f = h5py.File(file_name, 'x')
fields = []
fields.append(('pwd', np.dtype('S56')))
fields.append(('state', np.dtype('S1')))
fields.append(('userid', np.int32))
fields.append(('email', np.dtype('S80')))
fields.append(('ctime', np.int32))
fields.append(('mtime', np.int32))
dt = np.dtype(fields)
f['user_type'] = dt

f.close()
print(file_name, "created")
