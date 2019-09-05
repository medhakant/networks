import socket
import select
import sys
import re

server = socket.socket()
# IP_address = input("Enter IP address: ")
Port = int(input("Enter port number: "))
IP_address = "10.184.16.146"
server.connect((IP_address, Port))
uname = input("Enter username: ")
server.send(uname.encode())
while True:
    sockets_list = [sys.stdin, server]
    read_sockets,write_socket, error_socket = select.select(sockets_list, [], [])
    for socks in read_sockets:
        if socks == server:
            message = socks.recv(1024)
            print ("#"+message.decode())
        else:
            message = sys.stdin.readline()
            valid = re.match(r"@\[([a-z][a-z0-9]+)\]\[.+\]",message)
            if valid:
                server.send(message[1:].encode())
                sys.stdout.flush()
            else:
                print("Wrong input format")
server.close()