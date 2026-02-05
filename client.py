import socket
import select
import sys
import json

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

watch_list = [client_socket, sys.stdin.fileno()]


try : 
  client_socket.connect((HOST, PORT)) #connect to remote socket at address
except ConnectionRefusedError : 
  print("Client : Server not available")
  print("Client : disconnecting...")
  client_socket.close()
  exit(1)

connected = True

try :
  while connected : 
    readable, _, _ = select.select(watch_list, [], []) #blocking until input() or recv() ready
    
    for fd in readable : 
      if fd == sys.stdin.fileno() : 
        
        user_message = sys.stdin.readline().rstrip()
        
        if not user_message : 
          connected = False
          break
        
        if user_message[0] == "/" : 
          cmd = user_message.split(" ", 1)


          payload = {
            "type" : "command",
            "cmd" : cmd[0], #part with /
            "value" : cmd[1] #the rest
          }

        else : 
          payload = {
              "type" : "chat",
              "username" : client_socket.getsockname(),
              "text" : user_message
          }

        #serialise the srtuct into a json string
        json_expr = json.dumps(payload)

        #payload_bytes = user_message.encode("utf-8", errors="replace") #invalid Unicode char replaced by "?"
        payload_bytes = json_expr.encode("utf-8")
        length_bytes = len(payload_bytes).to_bytes(client_message.PREFIX_LENGTH, "big")
        
        try : 
          client_socket.sendall(length_bytes + payload_bytes) 

        except BrokenPipeError :
          print("Client : Send Fail (broken pipe)")
          connected = False
          break
        
      elif fd == client_socket : 
        data = client_socket.recv(SIZE)

        if not data :
          print("Client : Detected Server Closed")
          connected = False
          break
      
        broadcasted_payloads = client_message.feed(data)
      
        for payload in broadcasted_payloads : 
          #message = payload.decode("utf-8")
          json_expr = payload.decode("utf-8")
          payload = json.loads(json_expr)

          print(f"{payload['username']} : {payload['text']}")


except KeyboardInterrupt :
  print("Client : forced shutdown (CTRL+C)...")
finally : 
  print("Client : disconnecting...")
  client_socket.close()

