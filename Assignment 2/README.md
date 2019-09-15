# Chat_Bot
An end-to-end encrypted chat application

## Details
This is a course assignment for the graduate-level Computer Networks course taught by [**Prof. Aditeshwar Seth**]  
The assignment documentation can be found [here](https://d1b10bmlvqabco.cloudfront.net/attach/jydz42yrnzu2mc/ir1uq7pcpba2cm/jzm0prt5ymp9/2_chat_application.pdf)

## Main Files
+ `client.py` - This is an implementation of a client side application which sends the message to other client using their user name.
+ `chat_server.py` - This is an implementation of a server.

## Run Instructions
Here are the sample instructions used to connect and send messages between two clients connected to the server.
### Mode
 + 1: `unencrypted`
 + 2: `encrypted`
 + 3: `encrypted and signature`
### Setup Server
`python chat_server.py`
 + Enter Port Number: `8000`
 + Enter IP address: `0.0.0.0`
 + Enter mode: `mode`
### Setup Client 1
`python client.py`
 + Enter Port Number: `8000`
 + Enter IP address: `0.0.0.0`
 + Enter username: `medha`
 + Enter mode: `mode`
 
### Setup Client 2
`python client.py`
 + Enter Port Number: `8000`
 + Enter IP address: `0.0.0.0`
 + Enter username: `namrata`
 + Enter mode: `mode`

## Messages Format
+ `@[recipient_username][message]` : To send message to client
+ `#[username_sender] message` : when message is received
+ `UNREGISTER` : To unregister the client

