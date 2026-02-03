import socket
print("Client : Starting up...")

HOST = "127.0.0.1"
PORT = 5789
SIZE = 1024

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
  

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_message = Message()

try : 
  client_socket.connect((HOST, PORT)) #connect to remote socket at address
except ConnectionRefusedError : 
  print("Client : No server to connect to")
  print("Client : disconnecting...")
  client_socket.close()
  exit(1)

user_message = input("> ")

while user_message : 
  try : 
    payload_bytes = user_message.encode("utf-8")
    length_bytes = len(payload_bytes).to_bytes(client_message.PREFIX_LENGTH, "big")

    client_socket.sendall(length_bytes + payload_bytes) 

  except BrokenPipeError :
    print("Client : Send Fail (broken pipe)")
    break

  data = client_socket.recv(SIZE)  #reading at most 1024 bits and is blocking if no data is to be read

  if not data :
    print("Client : Detected Server Closed")
    break
  
  broadcasted_payloads = client_message.feed(data)
  
  for payload in broadcasted_payloads : 
    message = payload.decode("utf-8")
    print("Other : " , message)

  
  



  user_message = input("> ")

print("Client : disconnecting...")
client_socket.close()
