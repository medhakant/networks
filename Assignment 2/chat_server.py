import socket
import select
from _thread import *
import sys
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import ast
import re
import time


server = socket.socket()
# IP_address = input("Enter IP address: ")
Port = int(input("Enter port number: "))
Mode = int(input("Enter mode: "))
ack = {}
uname_conn = {}
list_of_clients = {}
pubkey = {}
IP_address = "127.0.0.1"
server.bind((IP_address, Port)) 
server.listen(100)
print("Server is listening.......")


def clientthread(conn, addr):
    publickey = pubkey[list_of_clients[conn]]
    message = "[CONNECTED]You are now connected.".encode()
    print(list_of_clients[conn].upper()+" has joined")
    conn.send(message)
    while True:     
            message = conn.recv(1024)    
            if message:
                message = message.decode()
                instruction = (re.search(r"\[[A-Z0-9]+\]",message)).group(0)
                print ("[" + list_of_clients[conn] + "] " + "Message received " + instruction)                
                if(instruction=="[SEND]"):
                    message = message[len(instruction):]
                    broadcast(message,conn)
                elif(instruction=="[GETKEY]"):
                    message = message[len(instruction):]
                    reciever = (re.search(r"\[[a-z0-9]+\]",message)).group(0)[1:-1]
                    if reciever in list(pubkey.keys()):
                        key = pubkey[reciever].exportKey(format='PEM', passphrase=None, pkcs=1)
                        conn.send(key)
                    else:
                        message_to_send = "[ERROR404][user not exist]"
                        conn.send(message_to_send.encode())
                elif(instruction=="[RECEIVED]"):
                    sender = message[len(instruction):]
                    ack[list_of_clients[conn]] = 0
            else:
                continue

def broadcast(message,conn):
    try:
        uname , message = message.split("][")
    except:
        message_to_send = "[ERROR103][header incomplete]".encode()
        conn.send(message_to_send)
        return
    uname = uname[1:].strip()
    message = message[:-1].strip()
    message = "[FORWARD]["+ list_of_clients[conn] + "]" + message
    if uname in list(uname_conn.keys()):   
        client = uname_conn[uname]
        client.send(message.encode())
        ack[uname] = -1
        time.sleep(1)
        if ack[uname] == -1:
            remove(client)
            message_to_send = "[ERROR102][unable to send]".encode()
            conn.send(message_to_send)
        else:
            message_to_send = ("[SENT]["+uname+"]").encode()
            conn.send(message_to_send)
            
    

def remove(connection):
    if connection in list_of_clients:
        print(list_of_clients[connection]+ " left")
        uname_conn.pop(list_of_clients[connection])
        pubkey.pop(list_of_clients[connection])
        list_of_clients.pop(connection)
        connection.close()


def register(conn,addr):
    registered = False
    username = ""
    while not registered:
        message = conn.recv(1024)    
        if message:
            message = message.decode()
            instruction = (re.search(r"\[[A-Z0-9]+\]",message)).group(0)               
            if(instruction=="[REGISTERTOSEND]"):
                message = message[len(instruction):]
                username = (re.search(r"\[.+\]",message)).group(0)[1:-1]
                valid = re.match(r"([a-z0-9]+)",username)
                if not valid:
                    message_to_send = "[ERROR100][malformed username]".encode()
                    conn.send(message_to_send)
                elif username in list(uname_conn.keys()):
                    message_to_send = "[ERROR100][username already exists]".encode()
                    conn.send(message_to_send)
                else:
                    message_to_send = ("[REGISTEREDTOSEND]["+username+"]").encode()
                    conn.send(message_to_send)
                    registered = True
                    continue
            else:
                message_to_send = "[ERROR101][no user registered]".encode()
                conn.send(message_to_send)                
                
    return username
        
while True:
    conn, addr = server.accept()
    publickey = RSA.importKey(conn.recv(1024))
    print("Request received")
    name = register(conn,addr)
    list_of_clients[conn] = name
    uname_conn[name] = conn
    pubkey[name] = publickey

    start_new_thread(clientthread,(conn,addr))

server.close()