import socket
print("Server start up...")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket type = SOCK_STREAM = TCP
#socket has an address family = AF_INET but no name/address
server_socket.bind(("Imran",5789))
#now address = IP+port
server_socket.listen()
#listening for active client connection
connection_socket , client_adress = server_socket.accept() #return value is the pair (conn, address) where conn = new socket to send and recv data on the connection and the address i think is the address of the client
print(f"Server : Connection etablished with client {client_adress}")

client_msg = connection_socket.recv(1024)

while(len(client_msg) != 0):
  print("Echo :", client_msg.decode("utf-8"))  
  connection_socket.sendall("F".encode("utf-8"))
  client_msg = connection_socket.recv(1024)

print("Server : Client closed connection")
print("Server : Closing all...")
connection_socket.close()
server_socket.close()