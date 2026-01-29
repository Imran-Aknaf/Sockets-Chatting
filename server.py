import socket
import select
print("Server : Starting up...")

HOST = "127.0.0.1"
PORT = 5789
SIZE = 1024

watch_list = []

clients_buffer = {}

def handleClientConnexion(server_socket) :
  connection_socket , client_adress = server_socket.accept()
  print(f"Server : connection etablished with client {client_adress}")

  return connection_socket

def handleClientMessage(client_socket) : 
  print("*"*40)
  buffer = clients_buffer[client_socket]
  data = client_socket.recv(SIZE) #these are bytes 

  if not data : 
    client_socket.close()
    print("Server : Client closed connection")
    return False
  
  buffer += data #the new bytes extends the stream of bytes currently in buffer
  
  '''print("Received:", data)
  print("Buffer now:", buffer)
  print("Contains newline?", b"\n" in buffer)'''

  #extract message by message : 
  while b"\n" in buffer : 
    encoded_msg, buffer = buffer.split(b"\n", 1) #split at the 1st \n occurence
    message = encoded_msg.decode("utf-8") #Because UTF-8 may be split >> if we decode immediately after recv() -> utf-8 can crash (see README)
    
    print("Echo : ", message)

  #either buffer is empty , or it contains the start of the next message
  clients_buffer[client_socket] = buffer

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
        clients_buffer[newClientSocket] = b""

      else : 
        state = handleClientMessage(sock)
        if not state : 
          watch_list.remove(sock)
          del clients_buffer[sock]

except KeyboardInterrupt :
  print("Server : shutdown (CTRL+C)...")

except ConnectionResetError : 
  print("Server : Client did CTRL+C")

finally :
  print("Server : Clean up...")
  print("Server : Closing all remaining sockets")
  for sock in watch_list : 
    if sock is not server_socket : 
      sock.close() #closing clients fist
  server_socket.close()#closing server
