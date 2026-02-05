# Chat App (Socket Programming)

Doing my own chat app.

## Features/Current 

- Echo Server-Client
- Handling crashing gracefully
- Multiple clients using `select`
- Delimiter-based framing message protocol (not sufficient !)
- Length-prefixed protocol
- Message broadcasting
- Client is not blocking , can read while typing.

## Steps

1. Length-prefixed protocol (with header) [DONE]
2. Note that currently client is blocking with input(), meaning it cannot receive messages while typing [DONE]
3. Adding semantics (username, ect...) [NEXT]
4. Message broadcasting [DONE]
5. Connecting over the internet (NAT/Firewall , IP/Port config)
6. Security (TLS, crypto for end-end encryption)

## Next Step : 

- Server control and ownershio to implement 
- So that the /rename (and /list) command works


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

Issues i guess can arise : 

1) if a lot of "other", then the last will receive message way too late compared to other and i guess with a lot message this is even worse.[Fairness issue]
2) what happens if other n°3 has disconnected/crash, then sendall fails , error. Need to handle that and let us continue broadcastinf of others [By catching it]
3) Now i don't know how this is possible but imagine a client that is still here but for which sendall is very slow, then everyone after is slowed down
4) what happens if the server itself crash while in broadcast -> is it acceptable that some clients will have receive while other not ? [Partial broadcasting is acceptable for now]

In client pov : 
  
1) if he is blocked at input(), then how will he receive the message broadcasted to him -> need to resolve this later with select i guess [DONE]
2) currently, only if he has just entered an input, he will do sendall and then only will i be able to get him to recv() the broadcasted messages. Then he should decode them and display them.

But issue, client does recv(SIZE) (just like server), but brodcasted message(s) could be bigger than SIZE and thus split through multiple recv()
Client currently does not have any system to handle that/

Maybe he should use also the Message class and i should from server do sendall(length+msg) again to other clients and let them handle this with Message() just like server. [DONE]


Current problem identified : 
- Client 1 sends data , then he becomes block because of recv()
- Server receive Client 1 data and send it to Client 2 (broadcast)
- Client 2 can't see message coming because blocked because of input()

- Thus Client 1 cannot do anything, he is totally dependent on Client 2 action
- Iff Client 2 enter an input, then he goes to recv() and receive Client 1 data and in the other way, his input is broadcasted to Client 1 which allows Client 1 to recv() and and display Client 1 message

Proposed solution : 
1) we need select() now in client-side, only way to have recv() only when needed (only when OS wake us up)
- this allows client to send as many message as it wants and directly when a recv() is available, handle it and print the message

2) but still, if he's not inputing something, he's blocked in the input(). So we need a select() for stdin then too.


- stdin becomes just another FD
- select([socket, stdin])

Now our client process will respond to : 
1. Network events (incoming message -> recv() )
2. User events (keyboard input -> input() )

Apparently ONE big downside is that stdin works well with select on UNIX but not on windows because the console input is special there.
We will deal with portability later, not a priority. 

### About using feed() 2 times : 

Currently what happens is : 
1. Client encodes and sends a message
2. Server receives raw bytes via recv() -> it calls feed() to cut them into as many message as possible (still bytes, no decoding done)
3. If there is messages, he sends these message bytes chunks to other client with length-prefix protocol (broadcasting)
4. Other client receive raw bytes and need to handle potentially many message or partial ones , so again use feed(), then decode to get real messages. 

Now here there is it seems a redudancy because server could just forward all the bytes he gets from recv() directly to other clients and they only use feed() themselves. So currently using feed() in server seems useless. 

But it has it's utilities for futur uses => If server needs to control messages (logging, moderation, commands, etc.) 

Therefore, currently, this part is commented out in server to continue using only the minimal necessary. 

### Remarks on endianness

In our fix-length-prefixed protocol we do 2 things : 

1) We convert the length into bytes with `.to_bytes(PREFIX_LENGTH, "big")` : 

- Because the network/socket can only sends bytes. So we need to encode the integer into bytes 
- And because we need a fix-length in our protocol, we choosed to serialize the integer into exactly 4 bytes (=PREFIX_LENGTH)
- "big" is the byte order/endianness. We choosed "big" arbitrarly.
- If client and server don't agree on the order/endianness, the decoded length will be completely wrong. So we force them to use both "big"

2) We convert the input text into bytes with `user_message.encode("utf-8")`

- Well as said before, we need to send bytes when using network/sockets. So encoding is necessary.
- UTF-8 is a already defined specific byte format. So it has a specific and defined order/endianness. 
- Therefore, there is no ambiguity about byte order in UTF-8. No need to use "big"/"little" here.

Important : 
- if we only transformed the length integer into bytes with no endianness specification, then it's decoding will be OS endianness-dependent
- we could maybe ask why not encode the integer into utf-8 then ? there would be no ambiguity.
- This is True but the issue is we loose the fix length of 4 bytes. Indeed imagine we do this `length_utf8 = str(12).encode("utf-8") ``
- Then for `length_int=12`, our utf-8 encoding is 2 bytes long
- But if `length_int=200`, our utf-8 encoding is 3 bytes long

We need the length to be fix-encoded to then allow easy parsing of the bytes
In our approach we always use 4 bytes and this works for any message_length up to 2^32-1 (as 4 bytes = 4*8 = 32 bits)

### Structured message 

We now want "structured message". The goal is to go from raw bytes messages to structured message wich have a meaning for both the server and the client. 

- Add Username or Client/Socket ID (to know from who comes this message)
- Can also pair this with Server Control (explore what can be done with logging, but a first thing is filtering bad words or commands)

Suggestion of commands : 
- /rename => rename yourself
- /list => list all connected "Others" in this conversation

### Json header communication

We build our structure message as a dictionnary which contains key-value pairs that gives important information : 
- `{ "type": "command", "cmd": "rename", "value": "imran" }`

But as we know , sockets only know raw bytes so we have this encoding flow : 
1) Build structure obj (dictionnary).
2) `json.dumps(x)` will transform the dictionnary into a json string. This becomes our payload.
3) We encode our payload into raw bytes using `.encode("utf-8")` and then `.sendall()`.

and this decoding flow : 
1) `recv()` gets raw bytes that are splitted into payload bytes with `feed()`.
2) Then for each encoded payload, we decode them using `.decode("utf-8")`. This gives us back the json string.
3) Now to get the final dictionnary we use `json.loads(x)`.

### Server control

Before server just did this : bytes in → bytes out.

But now he has to actually pay the cost of decoding everything that comes, because he need to check for commands and other things. [He needs to understand what arrive, to then react correctly]

When the server decodes a payload and check it, if it's important for him he will : 

1) Execute server logic
2) Send a new message to the involved clients of `"type" : "system"`.  

# Server Ownership/Authority

- need to talk about notion of ownership (with an example) and what happens if it's not server owned. [TODO]



### blocking methods : 

`.accept()`
`.recv()`
`.select()`
`input()`