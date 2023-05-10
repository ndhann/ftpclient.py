#!/usr/bin/env python3

# ftpclient.py - Nathan Dhanasekaran
# command format:
# - get: 3 arguments, <user>:<password>@<server> get <remote_file>
#        this will output the file into the current directory with the same name as on the server
# - ls: 3 arguments, <user>:<password>@<server> ls <remote_dir>
#       directory listing of the remote server at <remote_dir>
# - put: 4 arguments, <user>:<password>@<server> <command> <local_source> <remote_destination>
#        uploads local_source to remote_destination. NOTE: remote_destination must include a filename; the local file's name is not automatically appended!

import socket
import sys

def exitconn(sock, datasock):
    request = "QUIT\r\n"
    sock.sendall(request.encode())
    sock.close()
    datasock.close()
    print("bye!")

def main():
    if len(sys.argv) < 4:
        print("Incorrect number of arguments (Expected 3 or more)")
        return -1

    auth = None
    user = None
    password = None
    server = None
    port = 21
    cmd = None
    source = None
    destination = None

    if len(sys.argv) == 5:
        # the extra argument is assumed to be the local file to upload
        destination = sys.argv[4]
    # extract arguments here
    auth = sys.argv[1]
    user = auth.split(':')[0]
    #print(user)
    password = auth.split(':')[1].split('@')[0]
    #print(password)
    server = auth.split('@')[1]
    #print(server)
    port = 21 # by default at least
    cmd = sys.argv[2]
    #print(cmd)
    source = sys.argv[3]
    #print(source)

    sock = socket.create_connection((server, port))
    file = sock.makefile('r')

    #sock.recv(1024, socket.MSG_WAITALL)
    line = file.readline(8192)
    print(line)

    request = "USER " + user + "\r\n"
    sock.sendall(request.encode())
    print(file.readline())

    request = "PASS " + password + "\r\n"
    sock.sendall(request.encode())
    response = file.readline()
    print(response)
    # wait until successful login
    while not "Login successful" in response:
        response = file.readline()
        print(response)

    print("sending pasv")
    request = "PASV\r\n"
    sock.sendall(request.encode())
    pasvinfo = file.readline().split('(')[1].split(')')[0].split(',')
    print(pasvinfo)

    datahost = pasvinfo[0] + "." + pasvinfo[1] + "." + pasvinfo[2] + "." + pasvinfo[3]
    if datahost == "0.0.0.0":
        # assuming a response of 0.0.0.0 means use the same ip
        datahost = server
    dataport = ((int(pasvinfo[4]) * 256) + int(pasvinfo[5]))

    print(datahost)
    print(dataport)
    datasock = socket.create_connection((datahost, dataport))

    if cmd == "ls":
        request = "LIST " + source + "\r\n"
        sock.sendall(request.encode())
        response = file.readline()
        print(response)
        while not "Directory send OK" in response:
            if "226" in response:
                exitconn(sock, datasock)
                return -1
            response = file.readline()
            print(response)

        # get directory listing from data connection now
        datafile = datasock.makefile('r')
        listing = datafile.readline()
        print(listing)
        while listing != "":
            listing = datafile.readline()
            print(listing)

        exitconn(sock, datasock)
        return 0 # success!
    elif cmd == "get":
        request = "RETR " + source + "\r\n"
        sock.sendall(request.encode())
        response = file.readline()
        print(response)
        #byteamt = response.split("(")[1].split(" bytes")[0]
        #print(byteamt)

        # get file from data connection
        datafile = datasock.makefile('rb')
        data = datafile.read()
        localname = source.split("/")[-1]
        with open(localname, 'wb') as file:
            file.write(data)
            print("success")
            exitconn(sock, datasock)
            return 0 # success!
    elif cmd == "put":
        # not sure if we need to add the filename to the path we want to upload the file to...
        request = "STOR " + destination + "\r\n"
        sock.sendall(request.encode())
        response = file.readline()
        print(response)
        if "Permission denied" not in response:
            with open(source, 'rb') as file:
                datafile = datasock.makefile('wb')
                data = file.read()
                datafile.write(data)
                print("success")
                exitconn(sock, datasock)
                return 0
        else:
            exitconn(sock, datasock)
            return -1


main()
