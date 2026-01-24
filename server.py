import socket
import select
print("Server start up...")

'''
"127.0.0.1" or ::1 = localhost = loopback interface = data never leaves/never exposed to external network , all happens inside the host machine
So here it's just 2 process talking on the same HOST
Good for security because => other hosts on the network (outside) can't connect to it

2 types of interface : 
- loopback interface = socket connexion stays withing host
- ethernet interface = socket connexion to an external network (access to other hosts oustide of your localhost)

So depending on the IP adress you set, you will be bounded to either loopback/ethernet interface

.accept() is blocking
.recv() is blocking

.send() returns bytes sent, could have not send all bytes => our responsibility to call it again
.recv(buffsize) = will only read up to buffsize => our responsibility to call it again for bytes still in the pipe i guess 

- A big issue is that when server does socket.recv(), this is blocking until there is data send by this client. 
- Big issue because then server cannot accept new clients, read from existing clients => basically it's blocked until this client send something
- the OS knows which sockets have data, are blocked or are dead => this is why select() uses. 

readable, writable, exceptional = select.select(read_list, write_list, exception_list, timeout)
- read_list/write_list = list of sockets you want to read/write from/to
- exception_list = list of sockets to watch for errors 

- from all these lists, it gives you socket that are ready for you to read/write/handle execption
- it's like a trafic light for sockets connecting to server

.select() is blocking 

'''

HOST = "127.0.0.1"
PORT = 5789

watch_list = []


def handleClientConnexion(server_socket) :
  connexion_socket , client_adress = server_socket.accept()
  print(f"Server : connexion etablished with client {client_adress}")

  return connexion_socket

def handleClientMessage(client_socket) : 
  client_msg = client_socket.recv(1024)

  if not client_msg : 
    client_socket.close()
    print("Server : Client closed connexion")
    return False

  print("Echo :", client_msg.decode("utf-8"))
  client_socket.sendall("F".encode("utf-8"))

  return True

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket_type = SOCK_STREAM = TCP , socket_family = AF_INET => but still no name/address (bind)

server_socket.bind((HOST, PORT)) #address = IP+PORT , port < 1024 = priviliege access needed

server_socket.listen() #listening for active client connexion

watch_list.append(server_socket) #will be told when new client connexion

try :
  while True : 
    readable, _, _ = select.select(watch_list, [], []) #blocking until there is ready sockets

    for sock in readable : 
      if sock is server_socket : 
        newClientSocket = handleClientConnexion(sock)
        watch_list.append(newClientSocket)

      else : 
        state = handleClientMessage(sock)
        if not state : 
          watch_list.remove(sock)

except KeyboardInterrupt :
  print("Server : shutdown (CTRL+C)...")

finally :
  print("Server : Clean up...")
  print("Server : Closing all remaining sockets")
  for sock in watch_list : 
    if sock is not server_socket : 
      sock.close() #closing clients fist
  server_socket.close()#closing server





'''
connexion_socket , client_adress = server_socket.accept() #return value is the pair (conn, address) where conn = new socket to send and recv data on the connexion and the address i think is the address of the client
print(f"Server : connexion etablished with client {client_adress}")

client_msg = connexion_socket.recv(1024) #empty string when client close connexion

while client_msg :
  print("Echo :", client_msg.decode("utf-8"))  
  connexion_socket.sendall("F".encode("utf-8"))
  client_msg = connexion_socket.recv(1024)

print("Server : Client closed connexion")
print("Server : Closing all...")
connexion_socket.close()
server_socket.close()

'''