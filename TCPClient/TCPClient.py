#!/usr/bin/python3
import threading
import socket
import sys
import os

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serverName = sys.argv[1]

serverPort = sys.argv[2]

clientSocket.connect( (serverName, int(serverPort)) )

okay=True

# Get input for sending
username = input("Please input your user name:")

password = input("Please input your password:")

credentials ='/login ' + username + ' ' + password

clientSocket.send(credentials.encode())

server_message = clientSocket.recv(1024)

#print(server_message.decode())

while(server_message.decode() != "1001 Authentication successful"):

    print("1002 Authentication failed")

    username = input("Please input your user name:")

    password = input("Please input your password:")

    credentials ='/login ' + username + ' ' + password

    try:
        clientSocket.send(credentials.encode())

        server_message = clientSocket.recv(1024)

    except BrokenPipeError as err:
        print("Broken Pipe Error. Please restart server")
        okay = False
        break
    except ConnectionResetError as err:
        print("Server connection error. Please restart server")
        okay = False
        break
    except KeyboardInterrupt as err:
        print("Server has been interrupted via keyboard. Please restart server")
        okay = False
        break

print(server_message.decode())

def send_data():
    while(True):
    #    print("waiting for command:")

    #    if client_message == "true" or client_message == "false":
    #        clientSocket.send(("guess " + client_message).encode())
    #    else:

        client_message = input()
        clientSocket.send(client_message.encode())


x = threading.Thread(target=send_data)
x.daemon = True
x.start()

while(server_message.decode() != "4001 Bye bye" and okay == True):

    #client_message = input()
    #clientSocket.send(client_message.encode())

    server_message = clientSocket.recv(1024)
    print(server_message.decode())

    try:
        if server_message.decode().split()[0] == "Server":
            break
    except IndexError as err:
        print("Server has been shut down.")
        break
    except BrokenPipeError as err:
        print("Broken Pipe Error. Please restart server")
        break
    #if server_message.decode() == "3011 Wait":
    #    server_message = clientSocket.recv(1024)
    #    print(server_message.decode())


print("Client ends")
clientSocket.close()
