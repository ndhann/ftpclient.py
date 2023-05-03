#!/usr/bin/env python3

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
    filepath = None
    localfile = None

    if len(sys.argv) == 5:
        # the extra argument is assumed to be the local file to upload
        localfile = sys.argv[4]
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
    filepath = sys.argv[3]
    #print(filepath)

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
        request = "LIST " + filepath + "\r\n"
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
        request = "RETR " + filepath + "\r\n"
        sock.sendall(request.encode())
        response = file.readline()
        print(response)
        #byteamt = response.split("(")[1].split(" bytes")[0]
        #print(byteamt)

        # get file from data connection
        datafile = datasock.makefile('rb')
        data = datafile.read()
        localname = filepath.split("/")[-1]
        with open(localname, 'wb') as file:
            file.write(data)
            print("success")
            exitconn(sock, datasock)
            return 0 # success!
    elif cmd == "put":
        # not sure if we need to add the filename to the path we want to upload the file to...
        request = "STOR " + filepath + "/" + localfile + "\r\n"
        sock.sendall(request.encode())
        response = file.readline()
        print(response)
        if "Permission denied" not in response:
            with open(localfile, 'rb') as file:
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
