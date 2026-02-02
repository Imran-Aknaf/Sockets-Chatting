import socket
import select
print("Server : Starting up...")

HOST = "127.0.0.1"
PORT = 5789
SIZE = 1024


watch_list = [] 
clients_buffer = {}


class Message :
  PREFIX_LENGTH = 4

  def __init__(self) :
    self.buffer = b""
    self.remaining_bytes  = 0 
    self.awaiting_length = True

  def feed(self, data) : 
    self.buffer += data
    messages = []

    while True : 
      if self.awaiting_length : 
        if len(self.buffer) < self.PREFIX_LENGTH : 
          break #need to wait/read for more data

        length_encoding = self.buffer[:self.PREFIX_LENGTH]
        self.remaining_bytes = int.from_bytes(length_encoding, "big")
        self.awaiting_length = False
        self.buffer = self.buffer[self.PREFIX_LENGTH:]

      if len(self.buffer) < self.remaining_bytes : 
        break #need to wait/read for more data

      payload = self.buffer[:self.remaining_bytes]
      messages.append(payload.decode("utf-8")) 

      self.buffer = self.buffer[self.remaining_bytes:]
      self.awaiting_length = True
      self.remaining_bytes = 0

    return messages


def handleClientConnexion(server_socket) :
  connection_socket , client_adress = server_socket.accept()
  print(f"Server : connection etablished with client {client_adress}")

  return connection_socket

def handleClientMessage(client_socket) : 

  data = client_socket.recv(SIZE) #read bytes (ConnectionReset if client closed)
  
  if not data : 
    return False
  
  client_msg = clients_buffer[client_socket]
  messages = client_msg.feed(data)
  
  for msg in messages : 
    print("Echo : ", msg)
 
  client_socket.sendall("F".encode("utf-8")) #send ack (BrokenPipe if client closed)

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
        new_client_socket = handleClientConnexion(sock)
        watch_list.append(new_client_socket)
        clients_buffer[new_client_socket] = Message()

      else : 
        try : 
          client_connected = handleClientMessage(sock)
        except (ConnectionResetError, BrokenPipeError) :
          print(f"Server : Client {sock.getpeername()} disconnected unexpectedly")
          client_connected = False
        finally : 
          if not client_connected : 
            print(f"Server : Client {sock.getpeername()} closed connection")
            watch_list.remove(sock)
            del clients_buffer[sock]
            sock.close()


except KeyboardInterrupt :
  print("Server : shutdown (CTRL+C)...")

finally :
  print("Server : Clean up...")
  print("Server : Closing all remaining sockets")

  for sock in watch_list : 
    if sock is not server_socket : 
      sock.close() #closing clients fist
  server_socket.close()#closing server
