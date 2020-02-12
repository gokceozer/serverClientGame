#!/usr/bin/python3
import threading
import socket
import sys
import os

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serverName = "localhost"

serverPort = 12000

clientSocket.connect( (serverName, serverPort) )

# Get input for sending
username = input("Please input your user name:")

password = input("Please input your password:")

credentials ='/login ' + username + ' ' + password

clientSocket.send(credentials.encode())

server_message = clientSocket.recv(1024)

print(server_message.decode())


def send_data():
    #print("waiting for command:")
    client_message = input()
#    if client_message == "true" or client_message == "false":
#        clientSocket.send(("guess " + client_message).encode())
#    else:
    clientSocket.send(client_message.encode())



while(server_message.decode() != "4001 Bye bye"):

    x = threading.Thread(target=send_data)
    x.daemon = True
    x.start()

    server_message = clientSocket.recv(1024)
    print(server_message.decode())




    #try:
        #server_message = clientSocket.recv(1024)
        #print(server_message.decode())
    #except socket.timeout:
    #    print("Didn't receive data! [Timeout 2s]")

print("Client ends")
clientSocket.close()
