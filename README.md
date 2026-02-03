# Chat App (Socket Programming)

Doing my own chat app.

## Features/Current 

- Echo Server-Client
- Handling crashing gracefully
- Multiple clients using `select`
- Delimiter-based framing message protocol (not sufficient !)
- Length-prefixed protocol (without header)
- 

## Steps

1. Length-prefixed protocol (with header) [DONE]

2. Note that currently client is blocking with input(), meaning it cannot receive messages while typing
3. Adding semantics (username, ect...)

4. Message broadcasting 

5. Connecting over the internet (NAT/Firewall , IP/Port config)
6. Security (TLS, crypto for end-end encryption)

## Next Step : 

- I don't need to advance further into the protocol for now
- So we will focus on the next step which is message brodcasting as well as all its challenges 

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

### A length based protocol :

- MESSAGE := (4 bytes containing the length of the payload) + (bytes of the payload)

- Client just sends MESSAGE
- Server tries to read 4 bytes to know length, then tries to read the length to get the payload, if successfull he can then decode it.

- The current protocol is minimal but from this we can go towards a more compelete one that supports images, files, even audio, ect.. (with header)

### Message Class : 

CONSTANTS : 
- PREFIX_LENGTH = 4 : indicate the number of bytes to read at the beggining of a new message to know the length of the payload

VARIABLES :
- self.buffer : contains all the currently but not treated bytes through recv()
- self.remaining_bytes : remaining bytes to read to have the whole payload
- self.awaiting_length : Bool indicating if we need to read the 4 first bytes to get the length => this happens if we have just finished treating the previous message

METHODS : 
- feed(self, data) : add data to buffer -> extracts & decode as many message as possible 

### Message broadcasting : 

Some notes for now [To formalize] : 

Issues i guess can arise :

1) if a lot of "other", then the last will receive message way too late compared to other and i guess with a lot message this is even worse.[Fairness issue]
2) what happens if other n°3 has disconnected/crash, then sendall fails , error. Need to handle that and let us continue broadcastinf of others [By catching it]
3) Now i don't know how this is possible but image a client that is still here but for which sendall is very slow, then everyone after is slowed down
4) what happens if the server itself crash while in broadcast -> is it acceptable that some clients will have receive while other not ? [Partial broadcasting is acceptable for now]

In client pov : 
  
1) if he is blocked at input(), then how will he receive the message broadcasted to him -> need to resolve this later with select i guess
2) currently, only if he has just entered an input, he will do sendall and then only will i be able to get him to recv() the broadcasted messages. Then he should decode them and display them.

But issue, client does recv(SIZE) (just like server), but brodcasted message(s) could be bigger than SIZE and thus split through multiple recv()
Client currently does not have any system to handle that/

Maybe he should use also the Message class and i should from server do sendall(length+msg) again to other clients and let them handle this with Message() just like server.


### blocking methods : 

`.accept()`
`.recv()`
`.select()`
`input()`