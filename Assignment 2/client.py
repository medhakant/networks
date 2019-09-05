import socket
import select
import sys
import re
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import ast

server = socket.socket()
# IP_address = input("Enter IP address: ")
Port = int(input("Enter port number: "))
IP_address = "10.184.16.146"
server.connect((IP_address, Port))
random_generator = Random.new().read
key = RSA.generate(1024, random_generator)
publickey = key.publickey().exportKey(format='DER', passphrase=None, pkcs=1)
server.send(publickey)
uname = input("Enter username: ")
pubkey = {}
pubkey[uname] = key.publickey()

def register(uname):
    message_to_send = "[REGISTERTOSEND]["+uname+"]"
    server.send(message_to_send.encode())
    sockets_list = [sys.stdin, server]
    read_sockets,write_socket, error_socket = select.select(sockets_list, [], [])
    for socks in read_sockets:
        if socks == server:
            reply = socks.recv(1024)
            reply = reply.decode()
            instruction = (re.search(r"\[[A-Z0-9]+\]",reply)).group(0)
            if instruction == "[REGISTEREDTOSEND]":
                return
            else:
                reply = reply[len(instruction)+1:-1]
                print(reply)
                uname = input("Enter username: ")
                register(uname)
                

def fetchkey(receiver):
    sockets_list = [sys.stdin, server]
    read_sockets,write_socket, error_socket = select.select(sockets_list, [], [])
    for socks in read_sockets:
        if socks == server:
            reply = socks.recv(1024)
            try:
                key = RSA.importKey(reply)
                pubkey[receiver] = key
                return True
            except:
                reply = reply.decode()
                instruction = (re.search(r"\[[A-Z0-9]+\]",reply)).group(0)
                reply = reply[len(instruction)+1:-1]
                print(instruction[1:-1]+" "+reply)
                return False                
                
                

register(uname)
while True:
    sockets_list = [sys.stdin, server]
    read_sockets,write_socket, error_socket = select.select(sockets_list, [], [])
    for socks in read_sockets:
        if socks == server:
            message = (socks.recv(1024)).decode()
            print ("#"+str(key.decrypt(ast.literal_eval(message)).decode()))
        else:
            message = sys.stdin.readline()
            valid = re.match(r"^@\[([a-z][a-z0-9]*)\]\[(.+)\]$",message)
            if valid:
                receiver, message = message[2:-1].split("][")
                message = message[:-1]
                if receiver in list(pubkey.keys()):
                    rkey = pubkey[receiver]
                    message_to_send = "[SEND]["+receiver+"]["+str(rkey.encrypt(message.encode(), 32))+"]"
                    server.send(message_to_send.encode())
                else:
                    message_to_send = "[GETKEY]["+receiver+"]"
                    server.send(message_to_send.encode())
                    if not fetchkey(receiver):
                        continue
                    rkey = pubkey[receiver]
                    message_to_send = "[SEND]["+receiver+"]["+str(rkey.encrypt(message.encode(), 32))+"]"
                    server.send(message_to_send.encode())
                sys.stdout.flush()
            else:
                print("Wrong input format")



server.close()