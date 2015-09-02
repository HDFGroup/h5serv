import h5py
import numpy as np
import argparse
import os.path as op
import os
import time
import datetime
import hashlib
 
def encrypt_pwd(passwd):
    encrypted = hashlib.sha224(passwd).hexdigest()
    return encrypted
    
def print_time(timestamp):
    str_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return str_time
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', "--replace", help="update existing user/password", action="store_true")
    parser.add_argument('-a', "--add", help="add a new user/password", action="store_true")
    parser.add_argument('-f', "--filename", help='password file')
    parser.add_argument('-u', "--user", help='user id')
    parser.add_argument('-p', "--passwd", help='user password') 
      
    args = parser.parse_args()
       
    filename = None
    passwd = None
    username = None
    
    if args.filename:
        filename = args.filename
    else:
        filename = '../server/passwd.h5'
        
    if args.user:
        username = args.user
        if username.find(':') != -1:
            print "invalid username (':' is not allowed)"
            return -1
        if username.find('/') != -1:
            print "invalid username ('/' is not allowed)"
            return -1
        
    if args.passwd:
        passwd = args.passwd
        if passwd.find(':') != -1:
            print "invalid passwd (':' is not allowed)"
            return -1
            
    print ">filename:", filename
    print ">username:", username
    print ">password:", passwd
    
    
    if args.replace:
        print "replace is on"
        
        
    # verify file exists and is writable
    if not op.isfile(filename):
        print "password file:", filename, " does not exist"
        return -1
        
    if not h5py.is_hdf5(filename):
        print "invalid password file"
        return -1
        
    mode = 'r'
    if args.replace or args.add:
        mode = 'r+'
    
        if not os.access(filename, os.W_OK):
            print "password file is not writable"
            return -1
            
    print "mode:", mode
    
    f = h5py.File(filename, mode)
    if 'user_type' not in f:
        print "invalid password file"
        return -1
        
    user_type = f['user_type']
       
    
    now = int(time.time())
    
    if args.add:
        # add a new user
        if username in f.attrs:
            print "user already exists"
            return -1
        # create userid 1 greater than previous used
        userid = len(f.attrs) + 1
        data = np.empty((), dtype=user_type)
        data['pwd'] = encrypt_pwd(passwd)
        data['state'] = 'A'
        data['userid'] = userid
        data['ctime'] = now
        data['mtime'] = now
        f.attrs.create(username, data, dtype=user_type)   
    elif args.replace:
        if username not in f.attrs:
            print "user not found"
            return -1
        data = f.attrs[username]
        data['pwd'] = encrypt_pwd(passwd)
        data['mtime'] = now
        f.attrs.create(username, data, dtype=user_type)
    elif username and passwd:
        if username not in f.attrs:
            print "user not found"
            return -1
        data = f.attrs[username]
        if data['pwd'] == encrypt_pwd(passwd):
            print "password is valid"
            return 0
        else:
            print "password is not valid"
             
    elif username:
        if username not in f.attrs:
            print "user not found"
            return -1
        data = f.attrs[username]
        print "username:", username, "userid:", data['userid'], "state:", data['state'], "ctime:", print_time(data['ctime']), "mtime:", print_time(data['mtime'])
    else:
        # print all users
        print "username\tuserid\tstate\tctime           \tmtime"
        print "-" * 80
        for username in f.attrs.keys():
            data = f.attrs[username]
            print username + "\t\t" + str(data['userid']) + "\t" + data['state'] + "\t" + print_time(data['ctime']) + "\t" + print_time(data['mtime'])  
    
    f.close()
    
    return 0
     
    

main()