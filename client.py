import socket
print("Client start up...")


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("Imran",5789))
#connect to remote socket at address

user_input = input("> ")

while user_input : 
  client_socket.sendall(user_input.encode("utf-8"))
  received_msg = client_socket.recv(1024) 
  #reading at most 1024 bits and is blocking if no data is to be read
  if received_msg.decode("utf-8") == "F" : 
    print("Client : connection processed well")
  user_input = input("> ")

print("Client : Disconnecting...")
client_socket.close()
