import socket
import select
from _thread import *
import sys


server = socket.socket()
# IP_address = input("Enter IP address: ")
Port = int(input("Enter port number: "))

uname_conn = {}
IP_address = "10.184.16.146"
server.bind((IP_address, Port)) 
server.listen(100)
print("Server is listening.......")

list_of_clients={}

def clientthread(conn, addr):
    conn.send("[Server] You are now connected.".encode())
    while True:     
            message = conn.recv(2048)    
            if message:
                print ("[" + list_of_clients[conn] + "] " + "Message received")
                broadcast(message,conn)
            else:
                continue

def broadcast(message,connection):
    message = message.decode()
    uname , message = message.split("][")
    uname = uname[1:].strip()
    message = message.replace("]","").strip()
    message = "["+ list_of_clients[connection] + "] " + message
    uname_up_flag = False
    uname_flag = True
    if uname in list(uname_conn.keys()):
        uname_flag = False    
        client = uname_conn[uname]
        try:
            client.send(message.encode())
        except:
            uname_up_flag = True
            client.close()
            remove(client)
    if uname_flag:
        connection.send("[Server] No such username exist!".encode())
    elif uname_up_flag:
        connection.send("[Server] User not online!".encode())

def remove(connection):
    if connection in list_of_clients:
        print(list_of_clients[connection]+ " left")
        uname_conn.pop(list_of_clients[connection])
        list_of_clients.pop(connection)

while True:
    conn, addr = server.accept()
    name = (conn.recv(2048)).decode().strip()
    if name in list(uname_conn.keys()):
        conn.send("[Server] Username already exists. Pickup another username and try again".encode())
        continue
    list_of_clients[conn] = name
    uname_conn[name] = conn
    start_new_thread(clientthread,(conn,addr))

conn.close()
server.close()