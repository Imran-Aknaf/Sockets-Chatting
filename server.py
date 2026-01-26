import socket
import select
print("Server start up...")

HOST = "127.0.0.1"
PORT = 5789

watch_list = []


def handleClientConnexion(server_socket) :
  connection_socket , client_adress = server_socket.accept()
  print(f"Server : connection etablished with client {client_adress}")

  return connection_socket

def handleClientMessage(client_socket) : 
  client_msg = client_socket.recv(1024)

  if not client_msg : 
    client_socket.close()
    print("Server : Client closed connection")
    return False

  print("Echo :", client_msg.decode("utf-8"))
  client_socket.sendall("F".encode("utf-8"))

  return True

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket_type = SOCK_STREAM = TCP , socket_family = AF_INET => but still no name/address (bind)

server_socket.bind((HOST, PORT)) #address = IP+PORT , port < 1024 = priviliege access needed

server_socket.listen() #listening for active client connection

watch_list.append(server_socket) #will be told when new client connection

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
