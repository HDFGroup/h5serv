import h5py
import sys
 
            
"""
main method
"""
def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Delete db from h5serv file.")
        print("Warning: all object uuids and any user ACLs will be lost")
        print("Usage: python remove_db.py <filename>")
        sys.exit(1)
    filename = sys.argv[1]
    f = h5py.File(filename, 'a')
    if "__db__" not in f:
        print("No db group found")
    else:
        del f["__db__"]
        print("db group removed")
    f.close()

        

main()