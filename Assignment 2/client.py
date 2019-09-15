import socket
import select
import sys
import re
import Crypto
import Crypto.Hash.MD5 as MD5
from Crypto.PublicKey import RSA
from Crypto import Random
import ast
import random
print("Starting Client.............")
print("Messages should be of the format \"@[username][message]\"")
print("To close the application type \"UNREGISTER\"")
#initiate a random number
random.seed(random.randint(1,100))
#initiate server socket
server = socket.socket()
#take input from user IP, Port, Mode
IP_address = input("Enter IP address: ")
Port = int(input("Enter port number: "))
Mode = int(input("Enter mode: "))
#connect to the server
server.connect((IP_address, Port))
#generate RSA key
key = RSA.generate(1024, e=random.randrange(3,999999,2))
publickey = key.publickey().exportKey(format='PEM', passphrase=None, pkcs=1)
#instantiate connection with server by sending the publickey
server.send(publickey)

#input username from the user
uname = input("Enter username: ")
#instantiate a dictionary to store all the public keys
pubkey = {}
pubkey[uname] = key.publickey()

#function registers the given uname as username on the server
def register(uname):
    #form the message to send to the server
    message_to_send = "[REGISTERTOSEND]["+uname+"]"
    server.send(message_to_send.encode())
    #listen for the response
    sockets_list = [sys.stdin, server]
    read_sockets,write_socket, error_socket = select.select(sockets_list, [], [])
    for socks in read_sockets:
        #if the message is incoming from the server
        if socks == server:
            #store the server response
            reply = socks.recv(1024)
            reply = reply.decode()
            #split the instruction part of the response
            instruction = (re.search(r"\[[A-Z0-9]+\]",reply)).group(0)
            #if instruction is REGISTEREDTOSEND, exit the function
            if instruction == "[REGISTEREDTOSEND]":
                return
            #else promt for a new username and recurse
            else:
                reply = reply[len(instruction)+1:-1]
                print(reply)
                uname = input("Enter username: ")
                register(uname)
                
#function to fetch the key of the specified user, returns boolean to the call
def fetchkey(receiver):
    sockets_list = [sys.stdin, server]
    read_sockets,write_socket, error_socket = select.select(sockets_list, [], [])
    for socks in read_sockets:
        if socks == server:
            reply = socks.recv(1024)
            #check if the reponse is an RSA key
            try:
                key = RSA.importKey(reply)
                pubkey[receiver] = key
                return True
            #if not, print the error message
            except:
                reply = reply.decode()
                instruction = (re.search(r"\[[A-Z0-9]+\]",reply)).group(0)
                reply = reply[len(instruction)+1:-1]
                print(instruction[1:-1]+" "+reply)
                return False                
                

#Entry point of the program
#run the client untill flag is true               
flag = True
#register the user
register(uname)
#start the connection
while flag:
    sockets_list = [sys.stdin, server]
    read_sockets,write_socket, error_socket = select.select(sockets_list, [], [])
    #listen for activity on socket
    for socks in read_sockets:
        #if socket is server
        if socks == server:
            #decode the message, and split the instruction part
            message = (socks.recv(1024)).decode()
            if (re.search(r"\[[A-Z0-9]+\]",message)):
                instruction = (re.search(r"\[[A-Z0-9]+\]",message)).group(0)
                #if instruction is FORWARD, split the message into sender and the message (and signature if in Mode 3)
                #and print on the terminal
                if instruction == "[FORWARD]":
                    #remove the instruction part from the message
                    message = message[len(instruction):]
                    try:
                        #find the sender of the message and the message
                        sender = (re.search(r"\[[a-z0-9]+\]",message)).group(0)
                        message = message[len(sender):]
                        #if the program is running in mode 1, directly print the sender and message
                        if Mode ==1:
                            print("#"+sender+message)
                        #elif the program is running in mode 2, decrypt the 
                        # message and  print the sender and message  
                        elif Mode ==2:
                            print("#"+sender+str(key.decrypt(ast.literal_eval(message)).decode()))
                        #elif the program is running in mode 3, decrypt the 
                        # message and verify the signature and then print the sender and message  
                        elif Mode ==3:
                            #remove the starting and end brackets and split the message
                            message = message[1:-1]
                            message,signature = message.split("][")
                            senderuname = sender[1:-1]
                            #find the hash of the encrypted message
                            hashmessage = MD5.new(message.encode()).digest()
                            #if we have the publickey of the sender
                            #verify the signature and if it's true, print the sender and message
                            if senderuname in list(pubkey.keys()):
                                rkey = pubkey[senderuname]
                                if rkey.verify(hashmessage,ast.literal_eval(signature)):
                                    print("#"+sender+str(key.decrypt(ast.literal_eval(message)).decode()))
                            # if we don't have the publickey of the sender, fetch from server 
                            #verify the signature and if it's true, print the sender and message
                            else:
                                message_to_send = "[GETKEY]["+senderuname+"]"
                                server.send(message_to_send.encode())
                                #call the fetchkey function
                                if not fetchkey(senderuname):
                                    continue
                                rkey = pubkey[senderuname]
                                if rkey.verify(hashmessage,ast.literal_eval(signature)):
                                    print("#"+sender+str(key.decrypt(ast.literal_eval(message)).decode()))
                        #send an ack back to the server that the message was received properly
                        message_to_send = "[RECEIVED]"+sender
                        server.send(message_to_send.encode())
                    except:
                        #send an ack back to the server that the message was improper
                        message_to_send = "[ERROR103][header incomplete]"
                        server.send(message_to_send.encode())
                #for all instruction other than FORWARD, print the message on the terminal
                else:
                    print(message)
        else:
            #if there is no message waiting for us, read for user input
            message = sys.stdin.readline()
            #if the user input is UNREGISTER, turn down the flag and kill the connection
            if(message.strip() == "UNREGISTER"):
                server.close()
                flag = False
            #else match the input with proper message format
            else:
                valid = re.match(r"^@\[([a-z][a-z0-9]*)\]\[(.+)\]$",message)
                #if the message is valid, proceed
                if valid:
                    #split the message into receiver and message
                    receiver, message = message[2:-1].split("][")
                    message = message[:-1]
                    #if mode is 1, simply form the message with instruction,receiver,message and send the message
                    if Mode == 1:
                        message_to_send = "[SEND]["+receiver+"]["+message+"]"
                        server.send(message_to_send.encode())
                    #if mode is 2, form the message with instruction,receiver,encrypted message and send the message
                    elif Mode == 2:
                        #if we already have the publickey of the receiver, encrypt and send
                        if receiver in list(pubkey.keys()):
                            rkey = pubkey[receiver]
                            message_to_send = "[SEND]["+receiver+"]["+str(rkey.encrypt(message.encode(), 32))+"]"
                            server.send(message_to_send.encode())
                        #else, first fetch the key from the server, then encrypt and send
                        else:
                            message_to_send = "[GETKEY]["+receiver+"]"
                            server.send(message_to_send.encode())
                            #if no key is received, continue
                            if not fetchkey(receiver):
                                continue
                            rkey = pubkey[receiver]
                            message_to_send = "[SEND]["+receiver+"]["+str(rkey.encrypt(message.encode(), 32))+"]"
                            server.send(message_to_send.encode())
                    #if mode is 2, form the message with instruction,receiver,encrypted message,signature and send the message
                    elif Mode == 3:
                        #if we already have the publickey of the receiver, encrypt and send
                        #also create a hash of the encrypted message, and then sign it using out private key 
                        if receiver in list(pubkey.keys()):
                            rkey = pubkey[receiver]
                            encrypted_text = str(rkey.encrypt(message.encode(), 32))
                            hash = MD5.new(encrypted_text.encode()).digest()
                            signature = key.sign(hash,'')
                            message_to_send = "[SEND]["+receiver+"]["+encrypted_text+"]["+str(signature)+"]"
                            server.send(message_to_send.encode())
                        else:
                        #else, first fetch the key from the server, then encrypt and send 
                        #also create a hash of the encrypted message, and then sign it using out private key    
                            message_to_send = "[GETKEY]["+receiver+"]"
                            server.send(message_to_send.encode())
                            #if no key is received, continue
                            if not fetchkey(receiver):
                                continue
                            rkey = pubkey[receiver]
                            encrypted_text = str(rkey.encrypt(message.encode(), 32))
                            hash = MD5.new(encrypted_text.encode()).digest()
                            signature = key.sign(hash,'')
                            message_to_send = "[SEND]["+receiver+"]["+encrypted_text+"]["+str(signature)+"]"
                            server.send(message_to_send.encode())
                    sys.stdout.flush()
                #if the message is of wrong input format
                else:
                    print("Wrong input format")


#close the connection
server.close()