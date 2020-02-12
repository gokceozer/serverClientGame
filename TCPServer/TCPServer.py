#!/usr/bin/python3

import socket
import threading
import sys, traceback

# generate random integer values
from random import randint
import time


credentails_dict = {}
game_rooms = [0] * 10
dict_list = []
ans_list = [""] * 10
my_l = []

lock = threading.Condition()
v = 0
n = 2
mutexout = threading.Lock()

def barrier():
	with lock:
		global v
		v =+ 1

		print("v is increased to " + str(v))
		if v == n:
			print("v is equal to n")
			lock.notifyAll()
			print("v equals n")
			v = 0
		else:
			lock.wait()

for i in range(10):
	d = {}
	dict_list.append(d)

class ServerThread(threading.Thread):
	def __init__(self, client):
		threading.Thread.__init__(self)
		self.client = client

	def true_or_false(self):
		# generate some integers
		arr = ['true', 'false']
		value = randint(0, 1)
		return arr[value]

	def run(self):
		#in_game = False
		connectionSocket, addr = self.client

		mutex = threading.Lock()

		try:
			credentials = connectionSocket.recv(1024)
		except socket.error as err:
			print("Recv error: ", err)

		state = "out_of_house"

		#dummy, username, password = credentials.decode().split(' ')

		#password = password.strip()

		while username not in credentails_dict.keys() or credentails_dict[username] != password:
			try:
				credentials = connectionSocket.recv(1024)
				dummy, username, password = credentials.decode().split(' ')
				password = password.strip()
				if username not in credentails_dict.keys() or credentails_dict[username] != password:
					connectionSocket.send(b"1002 Authentication failed")
			except socket.error as err:
				print("Recv error: ", err)



		#if username in credentails_dict.keys() and credentails_dict[username] == password:


		connectionSocket.send(b"1001 Authentication successful")
				#print("1001 Authentication successful")
		state = "logged_in"



		while state != "exit":

				try:
					client_message = connectionSocket.recv(1024)
				except socket.error as err:
					print("Recv error: ", err)

				client_message_decoded = client_message.decode()[1:]

				if client_message_decoded == "list":

					message_info = "3001 " + str(len(game_rooms)) + " " + " ".join(str(x) for x in game_rooms)
					connectionSocket.send(message_info.encode())

				elif client_message_decoded.split(" ")[0] == "enter":

					room_no = int(client_message_decoded.split(" ")[1])

					if game_rooms[room_no-1] == 2:
						connectionSocket.send(b"3013 The room is full")
					elif game_rooms[room_no-1] == 0:
						connectionSocket.send(b"3011 Wait")
						mutex.acquire()
						game_rooms[room_no-1] += 1
						mutex.release()
						while game_rooms[room_no-1] != 2:
							connectionSocket.settimeout(2)
							try:
								print(game_rooms[room_no-1])
								mes = connectionSocket.recv(1024).decode()

								if mes == "exit":
									state = "exit"
									connectionSocket.send(b"4001 Bye bye")
								else:
									connectionSocket.send(b"4002 Unrecognized message")

							except socket.timeout:
								print("Didn't receive data! [Timeout 2s]")

						connectionSocket.settimeout(None)
						#in_game = True
						state = "in_game"

					if game_rooms[room_no-1] == 1 or state=="in_game":
						#traceback.print_exc()
						if state == "logged_in":
							mutex.acquire()
							#print("Incresing room size")
							game_rooms[room_no-1] += 1
							mutex.release()
							state = "in_game"

						connectionSocket.send(b"3012 Game started. Please guess true or false")
						#state = str(room_no)

						guess_message = ""
						while guess_message != "/guess":

							try:
								client_message = connectionSocket.recv(1024)
								client_guess = client_message.decode().split(" ")
								guess_message = client_guess[0]
								if guess_message != "/guess":
									connectionSocket.send(b"4002 Unrecognized message")
							except socket.error as err:
								print("Recv error: ", err)

						#client_guess = client_message.decode().split(" ")
						#print(client_guess[0])
						#print(client_guess[1])
						dict_list[room_no-1][username] = client_guess[1]
						print(dict_list[room_no-1])

						mutex.acquire()
						if ans_list[room_no-1] == "":
							ans_list[room_no-1] = self.true_or_false()
							#print("The answer is: " + ans_list[room_no-1])
						mutex.release()

						while len(dict_list[room_no-1])<2:
							pass

						#print("Before Barrier")
						#barrier()

						print(len(dict_list[room_no-1].values()))
						print(len(set(dict_list[room_no-1].values())))

						if len(dict_list[room_no-1].values()) != len(set(dict_list[room_no-1].values())):
							connectionSocket.send(b"3023 The result is a tie")
							mutex.acquire()
							my_l.append("")
							mutex.release()

						elif dict_list[room_no-1][username] == ans_list[room_no-1]:
							connectionSocket.send(b"3021 You are the winner")
							mutex.acquire()
							my_l.append("")
							mutex.release()

						else:
							connectionSocket.send(b"3022 You lost this game")
							mutex.acquire()
							my_l.append("")
							mutex.release()


						mutex.acquire()
						print("Lenght is : "+str(len(my_l)))
						mutex.release()

						while len(my_l) != 2:
							pass
						#barrier()

						print("Lenght now is : "+str(len(my_l)))
						mutex.acquire()
						ans_list[room_no-1] = ""
						dict_list[room_no-1].clear()
						game_rooms[room_no-1] = 0
						my_l.clear()
						mutex.release()
						#in_game = False
						state="logged_in"
						print("End of the game")


				elif client_message_decoded == "exit":
					state = "exit"
					connectionSocket.send(b"4001 Bye bye")

				else:
					connectionSocket.send(b"4002 Unrecognized message")


		#else:

		#	connectionSocket.send(b"1002 Authentication failed")




		connectionSocket.close()

class ServerMain:
	def server_run(self):

		with open('authentication.txt') as fp:
			for line in fp:
				username, password = line.split(":")

				credentails_dict[username] = password.strip()



		serverPort = 12000
		serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serverSocket.bind( ("", serverPort) )
		serverSocket.listen(5)
		print("The server is ready to receive")
		while True:
			client = serverSocket.accept()
			t = ServerThread(client)
			t.start()

if __name__ == '__main__':
	server = ServerMain()
	server.server_run()
