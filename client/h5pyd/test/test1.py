import sys
sys.path.append('..')
import h5pyd

f = h5pyd.File("tall.test.hdfgroup.org", "r", endpoint="http://127.0.0.1:5000")

print "filename,", f.filename
print "name:", f.name
print "id:", f.id
