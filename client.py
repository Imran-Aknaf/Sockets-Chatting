import socket
print("Client : Starting up...")

HOST = "127.0.0.1"
PORT = 5789
SIZE = 1024

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try : 
  client_socket.connect((HOST, PORT)) #connect to remote socket at address
except ConnectionRefusedError : 
  print("Client : No server to connect to")
  print("Client : disconnecting...")
  client_socket.close()
  exit(1)

user_input = input("> ")

while user_input : 
  try : 
    complete_msg = user_input + "\n"
    client_socket.sendall(complete_msg.encode("utf-8"))

  except BrokenPipeError :
    print("Client : Send Fail (broken pipe)")
    break

  received_msg = client_socket.recv(SIZE)  #reading at most 1024 bits and is blocking if no data is to be read

  if not received_msg :
    print("Client : Detected Server Closed")
    break

  ack = received_msg.decode("utf-8")
  if ack == "F" : 
    print("Client : connection processed well")
    
  user_input = input("> ")

print("Client : disconnecting...")
client_socket.close()
