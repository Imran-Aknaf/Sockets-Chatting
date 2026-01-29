# Chat App (Socket Programming)

Doing my own chat app.

## Features/Current 

- Echo Server-Client
- Handling crashing gracefully
- Multiple clients using `select`
- Delimiter-based framing message protocol (not sufficient !)

## Next Step

1. Length-prefixed protocol (with header) [TODO]

2. Note that currently client is blocking with input(), meaning it cannot receive messages while typing
3. Adding semantics (username, ect...)
4. Message broadcasting 
5. Connecting over the internet (NAT/Firewall , IP/Port config)
6. Security (TLS, crypto for end-end encryption)

## Notes

### Networking :

- 127.0.0.1" or ::1 = localhost -> use the loopback interface 
- Data never leaves the host machine
- External hosts cannot connect -> Good for security because => other hosts on the network (outside) can't connect to it

- This means the client and server are simply two processes communicating on the same host.

2 types of interface : 
1. loopback interface = socket connection stays withing host
2. ethernet interface = socket connection to an external network (access to other hosts oustide of your localhost/external machines)

- So depending on the IP adress the server binds to, you will be bounded to either loopback/ethernet interface

### accept() : 

`connection_socket , client_adress = server_socket.accept()`

- is blocking until a client did a connect() to our server HOST||PORT
- return value is the pair (conn, address) where :
1. conn = new socket to send and recv data on the connection
2. address = client's address

### recv() : 

`client_msg = connection_socket.recv(1024)`

- is blocking until there is data to read
- 1024 = buffer size => read at most 1024 bytes
- returns an empty bytes object: `b''` when client close connection !

### select() : 

- A big issue is that when server does socket.recv(), this is blocking until there is data sent by this client. 
- Big issue because then server cannot accept new clients or read from existing clients => basically it's blocked until this client send something
- the OS knows which sockets have data, are blocked or are dead => this is why select() uses. 

`readable, writable, exceptional = select.select(read_list, write_list, exception_list, timeout)`
- read_list/write_list = list of sockets you want to read/write from/to
- exception_list = list of sockets to watch for errors 

- from all these lists, it gives you socket that are ready for you to read/write/handle exception
- it's our traffic light for sockets connecting to server

### I need a message protocol :

I need a message protocol due to these issue : 

1. Message merging 
- When 2 messages arrive as one (and thus read as one by the server) => due to "no delay" in their sending + same connection/socket

2. Message splitting
- Basically a big message (> 1024 bytes) will comes divided into 1024 bytes chunks and will be seen as different messages

3. UTF-8 corruption
- UTF-8 corruption occurs when multibyte characters are split across multiple recv() calls, causing decoding errors if decoded too early 

Our protocol will be a simple minimal contract between the server and the client , basically rules allowing us to indentify a message 

### A minimal message protocol :

We use a type of protocol called "Delimiter-based framing"

We will use this minimal message protocol : 
- MESSAGE := UTF-8 bytes ending with '\n'

But you need to know that for this we must assume these : 

1. Messages are text
2. Messages cannot contain \n as data
3. Message are reasonably small

For a chat app this is reasonable. 

For information, these are the cases where this protocol would not really be enough.

1. Case 1 — Binary data
- This means sending images, encrypted data, compressed data -> I think the issue here is that there could be some bits chunk that naturally gives \n. 

2. Case 2 — Large messages
- If message is too long, the buffering becomes to memory-expensive

3. Case 3 — Multiple message types
- You need here to use a header or something to indicated a TYPE, because each type of message need to be treated differently (file vs text).

After reflection, it's not really reasonable for chat app because user could simply type "hello \n world", and the server will receive "hello \n world\n" which he will treat as 2 different messages.

A simple fix is just to search for all \n in the client input and escape them : "\\n". But this is time-expensive. 

So we will need in Next Step to implement the now necessary "Length-prefixed protocol".



### blocking methods : 

`.accept()`
`.recv()`
`.select()`