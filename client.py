import socket
print("Client start up...")

HOST = "127.0.0.1"
PORT = 5789

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
#connect to remote socket at address

user_input = input("> ")

while user_input : 
  try : 
    client_socket.sendall(user_input.encode("utf-8"))
  except BrokenPipeError :
    print("Client : Send Fail (broken pipe)")
    break

  received_msg = client_socket.recv(1024)  #reading at most 1024 bits and is blocking if no data is to be read

  if not received_msg :
    print("Client : Detected Server Closed")
    break

  if received_msg.decode("utf-8") == "F" : 
    print("Client : connexion processed well")
  user_input = input("> ")

print("Client : disconnecting...")
client_socket.close()
