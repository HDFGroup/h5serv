import h5py
import numpy as np
import sys
import argparse
import os.path as op
import os
import time
import datetime
import hashlib
import config
 
def encrypt_pwd(passwd):
    passwd = passwd.encode('utf-8')
    encrypted = hashlib.sha224(passwd).hexdigest()
    return encrypted
    
def print_time(timestamp):
    str_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return str_time
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', "--replace", help="update existing user/password", action="store_true")
    parser.add_argument('-a', "--add", help="add a new user/password", action="store_true")
    parser.add_argument('-f', "--file", help='password file')
    parser.add_argument('-u', "--user", help='user id')
    parser.add_argument('-e', "--email", help='user email')
    parser.add_argument('-p', "--passwd", help='user password') 
      
    args = parser.parse_args()
       
    filename = None
    passwd = None
    username = None
    email = None
    
    if args.file:
        filename = args.file
    else:
        filename = config.get("password_file")
        
    if args.user:
        username = args.user
        for ch in username:
            if ord(ch) >= ord('a') and ord(ch) <= ord('z'):
                continue # OK
            if ord(ch) >= ord('0') and ord(ch) <= ord('9'):
                continue # OK
            if ord(ch) == ord('_'):
                continue # OK
            print("invalid username ('", ch, "' is not allowed)")
            return -1
                
        
    if args.passwd:
        passwd = args.passwd
        if passwd.find(':') != -1:
            print("invalid passwd (':' is not allowed)")
            return -1
    if args.email:
        email = args.email
        if email.find('@') == -1:
            print("invalid email address ('@' not found)")
            return -1
            
    print(">filename:", filename)
    print(">username:", username)
    print(">password:", passwd)
    print(">email:", email)
    
    
    if args.replace:
        print("replace is on")
        
        
    # verify file exists and is writable
    if not op.isfile(filename):
        print("password file:", filename, " does not exist")
        return -1
        
    if not h5py.is_hdf5(filename):
        print("invalid password file")
        return -1
        
    mode = 'r'
    if args.replace or args.add:
        mode = 'r+'
    
        if not os.access(filename, os.W_OK):
            print("password file is not writable")
            return -1
    
    f = h5py.File(filename, mode)
    if 'user_type' not in f:
        print("invalid password file")
        return -1
        
    user_type = f['user_type']
       
    
    now = int(time.time())
    
    if args.add:
        # add a new user
        if username in f.attrs:
            print("user already exists")
            return -1
        # create userid 1 greater than previous used
        userid = len(f.attrs) + 1
        data = np.empty((), dtype=user_type)
        data['pwd'] = encrypt_pwd(passwd)
        data['state'] = 'A'
        data['userid'] = userid
        data['email'] = email
        data['ctime'] = now
        data['mtime'] = now
        f.attrs.create(username, data, dtype=user_type)   
    elif args.replace:
        if username not in f.attrs:
            print("user not found")
            return -1
        data = f.attrs[username]
        if passwd:
            data['pwd'] = encrypt_pwd(passwd)
        if email:
            data['email'] = email
        data['mtime'] = now
        f.attrs.create(username, data, dtype=user_type)
    elif username and passwd:
        if username not in f.attrs:
            print("user not found")
            return -1
        data = f.attrs[username]
        if data['pwd'] == encrypt_pwd(passwd):
            print("password is valid")
            return 0
        else:
            print("password is not valid")
             
    elif username:
        if username not in f.attrs:
            print("user not found")
            return -1
        data = f.attrs[username]
        print("username:", username, "userid:", data['userid'], "email:", data['email'], "state:", data['state'], "ctime:", print_time(data['ctime']), "mtime:", print_time(data['mtime']))
    else:
        # print all users
        sys.stdout.write("{:<25}{:<8}{:<8}{:<40}{:<20}{:<20}\n".format('username', 'userid', 'state', 'email', 'ctime', 'mtime'))
        sys.stdout.write(("-" * 120)+'\n')
        for username in f.attrs.keys():
            data = f.attrs[username]
            
            sys.stdout.write("{:<25}{:<8}{:<8}{:<40}{:<20}{:<20}\n".format(username,
                 str(data['userid']), data['state'], data['email'], print_time(data['ctime']), print_time(data['mtime']))) 
             
    f.close()
    
    return 0
     
    

main()