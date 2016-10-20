import sys
import h5py
import logging
from h5json import Hdf5db


dbname = "__db__"
if len(sys.argv) < 2 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
    print("Usage: python rebuildIndex.py [filename]")
    print("Warning: this utility will delete any previous UUIDs!");
    sys.exit()

# setup logger
log = logging.getLogger("rebuildIndex")
log.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
# create formatter
formatter = logging.Formatter( "%(levelname)s:%(filename)s:%(lineno)d::%(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)
log.propagate = False 

filepath = sys.argv[1]
log.info("openining file: " + filepath)
# remove the old index
f = h5py.File(filepath, 'a')
if dbname in f:
    log.info("deleting old db group")
    del f[dbname]
f.close()

# now open with hdf5db
 
with Hdf5db(filepath, app_logger=log) as db:
    # the actual index rebuilding will happen in the init function
    root_uuid = db.getUUIDByPath('/')
    print("root_uuid:", root_uuid)

print("done!")

