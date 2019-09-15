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

#intialise the server socket
server = socket.socket()

# Input IP address, port and Mode from the user
IP_address = input("Enter IP address: ")
Port = int(input("Enter port number: "))
Mode = int(input("Enter mode: "))

#dictionary to store ack messages if received from receiver
ack = {}
#dictionary to store username as keys and values as connection
uname_conn = {}
#dictionary to store username as values and keys as connection
list_of_clients = {}
#store the public key  as values with user as keys
pubkey = {}
#bind to the specified IP and port
server.bind((IP_address, Port)) 
server.listen(100)
#initialise server
print("Server is listening.......")

#client thread keeps listening to client requests and caters to them
def clientthread(conn, addr):
    #when the connection is established a connection message is sent to the client
    message = "[CONNECTED]You are now connected.".encode()
    #print a joining message on server
    print(list_of_clients[conn].upper()+" has joined")
    conn.send(message)
    #run a loop while connection exists
    while True:     
            message = conn.recv(1024)   
            #if a message exist, process it 
            if message:
                message = message.decode()
                #get the instruction part of the message and act accordingly
                instruction = (re.search(r"\[[A-Z0-9]+\]",message)).group(0)
                #print a instruction message on server
                print ("[" + list_of_clients[conn] + "] " + "Message received " + instruction)
                #if the instruction is SEND, call the broadcast function                
                if(instruction=="[SEND]"):
                    message = message[len(instruction):]
                    broadcast(message,conn)
                #if instruction is GETKEY, return a key if the user exist or send an error message
                elif(instruction=="[GETKEY]"):
                    message = message[len(instruction):]
                    reciever = (re.search(r"\[[a-z0-9]+\]",message)).group(0)[1:-1]
                    if reciever in list(pubkey.keys()):
                        key = pubkey[reciever].exportKey(format='PEM', passphrase=None, pkcs=1)
                        conn.send(key)
                        print ("[" + list_of_clients[conn] + "] " + "Message sent [KEY]") 
                    else:
                        message_to_send = "[ERROR404][user not exist]"
                        conn.send(message_to_send.encode())
                        print ("[" + list_of_clients[conn] + "] " + "Message sent [ERROR404]")
                #if an ack is received, change the value of ack dict
                elif(instruction=="[RECEIVED]"):
                    sender = message[len(instruction):]
                    ack[list_of_clients[conn]] = 1
                elif(instruction=="[ERROR103]"):
                    sender = message[len(instruction):]
                    ack[list_of_clients[conn]] = 0
            else:
                continue

#this function forwards the message to the required person
def broadcast(message,conn):
    #if Mode is 3, try split the message into 3 parts and remove brackets or throw exception
    if Mode == 3:
        try:
            uname , message , signature = message.split("][")
            uname = uname[1:].strip()
            message = message.strip()
            signature = signature[:-1].strip()
            #form the message to be sent to the receiver
            message = "[FORWARD]["+ list_of_clients[conn] + "][" + message + "][" + signature + "]"
        except:
            message_to_send = "[ERROR103][header incomplete]".encode()
            conn.send(message_to_send)
            print ("[" + list_of_clients[conn] + "] " + "Message sent [ERROR103]")
            return
    #if Mode is 2 or 1, try split the message into 2 parts and remove brackets or throw exception
    else:
        try:
            uname , message = message.split("][")
            uname = uname[1:].strip()
            message = message[:-1].strip()
            #form the message to be sent to the receiver
            message = "[FORWARD]["+ list_of_clients[conn] + "]" + message
        except:
            message_to_send = "[ERROR103][header incomplete]".encode()
            conn.send(message_to_send)
            print ("[" + list_of_clients[conn] + "] " + "Message sent [ERROR103]")
            return

    #if the receiver exist, send the message and wait for and acknowlegdement
    if uname in list(uname_conn.keys()):   
        client = uname_conn[uname]
        client.send(message.encode())
        ack[uname] = -1
        #wait for an ack for 1 second, and then declare timeout
        time.sleep(1)
        #if no ack is received, user is offline/has unregistered
        if ack[uname] == -1:
            remove(client)
            message_to_send = "[ERROR102][unable to send, user offline]".encode()
            conn.send(message_to_send)
            print ("[" + list_of_clients[conn] + "] " + "Message sent [ERROR102]")
        #if ack is received but error in received message
        elif ack[uname] == 0:
            message_to_send = "[ERROR102][unable to send]".encode()
            conn.send(message_to_send)
            print ("[" + list_of_clients[conn] + "] " + "Message sent [ERROR102]")
        #if ack is received and message received properly
        else:
            message_to_send = ("[SENT]["+uname+"]").encode()
            conn.send(message_to_send)
            print ("[" + list_of_clients[conn] + "] " + "Message sent [SENT]")
    else:
        #if no such user exist
        message_to_send = "[ERROR102][unable to send, user not exist]".encode()
        conn.send(message_to_send)
        print ("[" + list_of_clients[conn] + "] " + "Message sent [ERROR102]")
            
    
#function to unregister user
def remove(connection):
    if connection in list_of_clients:
        #remove the entries from dictionaries and print a message on server
        print(list_of_clients[connection]+ " unregistered")
        uname_conn.pop(list_of_clients[connection])
        pubkey.pop(list_of_clients[connection])
        list_of_clients.pop(connection)


#function to register a new user
def register(conn,addr):
    registered = False
    username = ""
    #while user is not registered, run the loop
    while not registered:
        message = conn.recv(1024)    
        if message:
            #decode the message and split the instruction
            message = message.decode()
            instruction = (re.search(r"\[[A-Z0-9]+\]",message)).group(0)  
            #if the instruction is REGISTERTOSEND              
            if(instruction=="[REGISTERTOSEND]"):
                message = message[len(instruction):]
                username = (re.search(r"\[.+\]",message)).group(0)[1:-1]
                valid = re.match(r"([a-z0-9]+)",username)
                #if username is not valid, return error
                if not valid:
                    message_to_send = "[ERROR100][malformed username]".encode()
                    conn.send(message_to_send)
                #if username already exists, return an error
                elif username in list(uname_conn.keys()):
                    message_to_send = "[ERROR100][username already exists]".encode()
                    conn.send(message_to_send)
                #if username is valid, register the user
                else:
                    message_to_send = ("[REGISTEREDTOSEND]["+username+"]").encode()
                    conn.send(message_to_send)
                    #turn up the flag
                    registered = True
                    continue
            #else promt an error
            else:
                message_to_send = "[ERROR101][no user registered]".encode()
                conn.send(message_to_send)                
                
    return username

#the entry point of the program, the clients iniatiates request by sending the publickey        
while True:
    conn, addr = server.accept()
    publickey = RSA.importKey(conn.recv(1024))
    print("Request received")
    #get the use name and make entries to the specific dictionaries
    name = register(conn,addr)
    list_of_clients[conn] = name
    uname_conn[name] = conn
    pubkey[name] = publickey
    #start a new thread for the new connection
    start_new_thread(clientthread,(conn,addr))

server.close()