#!/usr/bin/python3
import sys, os
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


lock = threading.Condition()
lock1 = threading.Condition()

a = 0
b = 2

mutexout = threading.Lock()


def barrier2():
	with lock1:
		global a
		a += 1
		if a == b:
			lock1.notifyAll()
			a = 0
		else:
			lock1.wait()

for i in range(10):
	d = {}
	dict_list.append(d)

class ServerThread(threading.Thread):
	def __init__(self, client):
		threading.Thread.__init__(self)
		self.client = client
		self.is_connected = True
		self.handled = False

	def true_or_false(self):
		# generate some integers
		arr = ['true', 'false']
		value = randint(0, 1)
		return arr[value]

	def run(self):
		#in_game = False
		connectionSocket, addr = self.client
		is_connected = self.is_connected

		mutex = threading.Lock()

		try:
			credentials = connectionSocket.recv(1024)
		except socket.error as err:
			print("Recv error: ", err)
			#self.stop()
		except BrokenPipeError as err:
			print("Recv error: ", err)
			#self.stop()


		state = "out_of_house"

		try:
			dummy, username, password = credentials.decode().split(' ')
		except ValueError as err:
			print("Recv error: ", err)
			is_connected == False
			print("Killing this thread as the client left")
			#self.stop()
		except socket.error as err:
			print("Recv error: ", err)
			is_connected == False
			#self.stop()
		except BrokenPipeError as err:
			print("Recv error: ", err)
			is_connected == False
			#self.stop()


		if username not in credentails_dict.keys() or credentails_dict[username] != password:

			while username not in credentails_dict.keys() or credentails_dict[username] != password:
				try:
					connectionSocket.send(b"1002 Authentication failed")
					credentials = connectionSocket.recv(1024)
					dummy, username, password = credentials.decode().split(' ')
					password = password.strip()
				except socket.error as err:
					print("Recv error: ", err)
					#self.stop()
					is_connected == False
				except BrokenPipeError as err:
					print("Recv error: ", err)
					#self.stop()
					is_connected == False



		connectionSocket.send(b"1001 Authentication successful")
				#print("1001 Authentication successful")
		state = "logged_in"



		while state != "exit" and is_connected == True:

				try:
					connectionSocket.settimeout(None)
					#print(username + " is going to send command")
					client_message = connectionSocket.recv(1024)
				except socket.timeout as err:
					pass
					#self.stop()
				except BrokenPipeError as err:
					print("Recv error: ", err)
					is_connected = False
					#self.stop()
				except ConnectionResetError as err:
					print("Recv error: ", err)
					is_connected = False

				client_message_decoded = client_message.decode()[1:]
				message_array_form = client_message.decode()
				#print("message is" + client_message_decoded)
				if client_message_decoded == "list":

					message_info = "3001 " + str(len(game_rooms)) + " " + " ".join(str(x) for x in game_rooms)
					connectionSocket.send(message_info.encode())

				elif client_message_decoded.split(" ")[0] == "enter" and int(client_message_decoded.split(" ")[1]) >= 0 and int(client_message_decoded.split(" ")[1])<=10:

					room_no = int(client_message_decoded.split(" ")[1])
					opponent_timed_out = False
					if game_rooms[room_no-1] == 2:
						connectionSocket.send(b"3013 The room is full")
					elif game_rooms[room_no-1] == 0:
						#print("Sending wait statement")
						connectionSocket.send(b"3011 Wait")
						mutex.acquire()
						game_rooms[room_no-1] += 1
						mutex.release()
						#print("Game room length is " + str(game_rooms[room_no-1]))
						#print(username + "WAITINGGG")
						while game_rooms[room_no-1] != 2 and is_connected == True:
							connectionSocket.settimeout(2)
							try:
								#print(game_rooms[room_no-1])
								mes = connectionSocket.recv(1024).decode()

								if mes == "exit":
									state = "exit"
									connectionSocket.send(b"4001 Bye bye")
								else:
									connectionSocket.send(b"4002 Unrecognized message")

							except socket.timeout:
								pass
							except ConnectionResetError as err:
								print(username + " ConnectionResetError")
								is_connected = False
								dict_list[room_no-1][username] = "discon"
								#self.stop()
							except BrokenPipeError as err:
								print("Recv error: ", err)
								dict_list[room_no-1][username] = "discon"
								is_connected = False
								#self.stop()
							except OSError as err:
								print(username + " 0S Error")
								is_connected = False
								dict_list[room_no-1][username] = "discon"

						connectionSocket.settimeout(None)
						state = "in_game"

					if (game_rooms[room_no-1] == 1 or state=="in_game") and is_connected == True:
						if state == "logged_in":
							mutex.acquire()
							game_rooms[room_no-1] += 1
							mutex.release()
							state = "in_game"

						connectionSocket.send(b"3012 Game started. Please guess true or false")


						received = False
						okay = False
						notified = False
						while( len(dict_list[room_no-1])<2):#okay == False and is_connected == True and notified == False):
							connectionSocket.settimeout(2)
							#print("Checking for disconneted " + username)
							try:
								if "discon" in dict_list[room_no-1].values():
									print("A player is disconneted")
									#print("MY OPPONENT IS GONE")
									notified = True
									opponent_timed_out = True
									print(dict_list[room_no-1])
									connectionSocket.send(b"3021 You are the winner")
									break
								else:
									pass
									#print("It is not in the list yet")

								if opponent_timed_out == False:
									#print("NO ONE Disconnected yet")
									#print("Waiting for message from " + username)

									client_message = connectionSocket.recv(1024)

										#print(username + " sent " + client_message.decode())
									client_guess = client_message.decode().split(" ")
									if len(client_guess) != 2 or client_guess[0] != '/guess' or client_guess[1] != 'true' and client_guess[1] != 'false':
										connectionSocket.send(b"4002 Unrecognized message")

									else:
											#print("Legal")
										received = True
										dict_list[room_no-1][username] = client_guess[1]



							except socket.timeout:
								pass

							except ConnectionResetError as err:
								print(username + " ConnectionResetError")
								#print("Recv error: ", err)
								dict_list[room_no-1][username] = "discon"
								is_connected = False
								break
								#self.stop()
							except BrokenPipeError as err:
								print(username + " BrokenPipeError")
								#print("Recv error: ", err)
								dict_list[room_no-1][username] = "discon"
								is_connected = False
								break
							except KeyboardInterrupt as err:
								print(username + " Keyboard Interrupt")
								#print("Recv error: ", err)
								dict_list[room_no-1][username] = "discon"
								is_connected = False
								break

								#self.stop()
						#print(username + " is here")
						#print(dict_list[room_no-1])
						if is_connected == True:
						#	dict_list[room_no-1][username] = client_guess[1]


							mutex.acquire()
							if ans_list[room_no-1] == "":
								ans_list[room_no-1] = self.true_or_false()
							mutex.release()

						#while len(dict_list[room_no-1])<2:
						#	pass

							#while(len(dict_list[room_no-1])<2):
								#NO EXCEPTIONS RAISED IF THE CLIENT RAISES A KEYBOARDINTERRUPT OR CUTS CONNECTTION
							#	if opponent_timed_out:
							#		break


							#print(username + " before break")
							#barrier(room_no)
							#print(username + " after break")

							#print(dict_list[room_no-1])

							if "discon" in dict_list[room_no-1].values() and is_connected==True and notified == False:
								connectionSocket.send(b"3021 You are the winner")

							#elif opponent_timed_out:
							#	connectionSocket.send(b"3021 You are the winner")

							elif "discon" not in dict_list[room_no-1].values() and len(dict_list[room_no-1].values()) != len(set(dict_list[room_no-1].values())):
								connectionSocket.send(b"3023 The result is a tie")


							elif "discon" not in dict_list[room_no-1].values() and dict_list[room_no-1][username] == ans_list[room_no-1]:
								connectionSocket.send(b"3021 You are the winner")


							elif "discon" not in dict_list[room_no-1].values():
								connectionSocket.send(b"3022 You lost this game")



						#print(username + " at barrier")
						barrier2()
						#print(username + " passed barrier")
						opponent_timed_out = False
						mutex.acquire()
						ans_list[room_no-1] = ""
						dict_list[room_no-1].clear()
						game_rooms[room_no-1] = 0
						mutex.release()
						#in_game = False
						state="logged_in"
						#print("End of the game")

					#Clean the room if thread is disconneted
					if is_connected == False and game_rooms[room_no-1] == 1:
						mutex.acquire()
						ans_list[room_no-1] = ""
						dict_list[room_no-1].clear()
						game_rooms[room_no-1] = 0
						opponent_timed_out = False
						mutex.release()




				elif client_message_decoded == "exit":
					state = "exit"
					connectionSocket.send(b"4001 Bye bye")

				else:
					try:
						connectionSocket.send(b"4002 Unrecognized message")
					except socket.error as err:
						print("Recv error: ", err)
						is_connected = False
					except BrokenPipeError as err:
						print("Recv error: ", err)
						is_connected = False
						#self.stop()



		#print("Imma out")
		connectionSocket.close()




class ServerMain:
	def server_run(self):
		threads = []
		directory = os.path.join(sys.argv[2], 'UserInfo.txt')


		with open(directory) as fp:
			for line in fp:
				username, password = line.split(":")
				credentails_dict[username] = password.strip()



		serverPort = sys.argv[1]
		serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serverSocket.bind( ("", int(serverPort)) )
		serverSocket.listen(5)
		print("The server is ready to receive")
		while True:
			for t in threads:
				if not t.isAlive():
					t.handled = True
					#print("A thread died", flush=True)
			threads = [t for t in threads if not t.handled]
			#print("This many threads: ", str(len(threads)), flush=True)
			try:
				client = serverSocket.accept()
			except KeyboardInterrupt as err:
				print("Server has been interrupted via keyboard. Please restart server")
				connectionSocket, addr = client
				connectionSocket.send(b"Server has been interrupted via keyboard. Please restart server.")
				time.sleep(0.5)
				os._exit(0)
			except ConnectionResetError as err:
				print("Server connection error. Please restart server")
				connectionSocket, addr = client
				connectionSocket.send(b"Server connection error. Please restart server.")
				time.sleep(0.5)
				os._exit(0)

			t = ServerThread(client)
			threads.append(t)
			t.start()
		serverSocket.close()



if __name__ == '__main__':
	server = ServerMain()
	server.server_run()
