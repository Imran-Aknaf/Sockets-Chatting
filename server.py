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
    payloads = []

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
      #messages.append(payload.decode("utf-8")) 
      payloads.append(payload)

      self.buffer = self.buffer[self.remaining_bytes:]
      self.awaiting_length = True
      self.remaining_bytes = 0

    return payloads


def handleClientConnexion(server_socket) :
  connection_socket , client_adress = server_socket.accept()
  print(f"Server : connection etablished with client {client_adress}")

  return connection_socket

def handleClientMessage(client_socket) : 

  data = client_socket.recv(SIZE) #read bytes (ConnectionReset if client closed)
  
  if not data : 
    return False
  
  client_msg = clients_buffer[client_socket]
  payloads = client_msg.feed(data)
  
  for other in watch_list : 
    if other is not client_socket and other is not server_socket : 
        for payload in payloads :
          length= len(payload).to_bytes(client_msg.PREFIX_LENGTH, "big")
          other.sendall(length + payload) 
    
  '''
  Issues i guess can arise :

  1) if a lot of "other", then the last will receive message way too late compared to other and i guess with a lot message this is even worse. [Fairness issue]
  2) what happens if other n°3 has disconnected/crash, then sendall fails , error. Need to handle that and let us continue broadcastinf of others [By catching it]
  3) Now i don't know how this is possible but image a client that is still here but for which sendall is very slow, then everyone after is slowed down
  4) what happens if the server itself crash while in broadcast -> is it acceptable that some clients will have receive while other not ? [Partial broadcasting is acceptable for now]

  In client pov : 
  
  1) if he is blocked at input(), then how will he receive the message broadcasted to him -> need to resolve this later with select i guess
  2) currently, only if he has just entered an input, he will do sendall and then only will i be able to get him to recv() the broadcasted messages. Then he should decode them and display them.

  But issue, client does recv(SIZE) (just like server), but brodcasted message(s) could be bigger than SIZE and thus split through multiple recv()
  Client currently does not have any system to handle that

  Maybe he should use also the Message class and i should from server do sendall(length+msg) again to other clients and let them handle this with Message() just like server
   
  
  '''
  


  #client_socket.sendall("F".encode("utf-8")) #send ack (BrokenPipe if client closed)

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
