# ClassChat System - README

## Overview
ClassChat is a multi-threaded TCP socket-based chat system that supports private messaging and group chat functionality. 
The system uses a client-server architecture where multiple clients can connect simultaneously to communicate in real-time.

## Features
- **Private Messaging**: Send direct messages to specific users
- **Group Chat Rooms**: Create and join chat rooms for group discussions
- **Multi-threaded**: Handles multiple concurrent users efficiently
- **Real-time Communication**: Asynchronous message sending and receiving
- **JSON Protocol**: Structured message format for reliable communication
- **Error Handling**: Comprehensive error messages and connection management

---

## System Requirements

### Prerequisites
- **Python 3.6 or higher**
- **Operating System**: Windows, macOS, or Linux
- **Network**: TCP/IP networking capability

### Required Python Modules
All required modules are part of Python's standard library:
- `socket`
- `threading`
- `json`
- `sys`

No additional package installation is needed!

---

## File Structure

```
ClassChat/
│
├── Parker_Schemm_901057227_server.py    # Server implementation
├── Parker_Schemm_901057227_client.py    # Client implementation
└── README.txt                           # This file
```

---

## Quick Start Guide

### Step 1: Start the Server

Open a terminal/command prompt and navigate to the project directory:

```bash
cd /path/to/ClassChat
```

Run the server:

```bash
python Parker_Schemm_901057227_server.py
```

**Expected Output:**
```
[SERVER] Server started on 127.0.0.1:5555
[SERVER] Waiting for connections...
```

The server will now listen for client connections on `localhost` (127.0.0.1) at port `5555`.

#### Custom Server Configuration

You can specify a custom host and port:

```bash
python Parker_Schemm_901057227_server.py <HOST> <PORT>
```

Example:
```bash
python Parker_Schemm_901057227_server.py 0.0.0.0 8080
```

---

### Step 2: Start Client(s)

Open **new terminal windows** (one for each client) and run:

```bash
python Parker_Schemm_901057227_client.py
```

#### Client Setup Process

1. **Enter Server IP Address**:
   ```
   Enter server IP address (default: 127.0.0.1): 
   ```
   - Press Enter to use default `127.0.0.1` (localhost)
   - Or enter the server's IP address if running on a different machine

2. **Enter Server Port**:
   ```
   Enter server port (default: 5555): 
   ```
   - Press Enter to use default port `5555`
   - Or enter the custom port if the server is using one

3. **Enter Username**:
   ```
   Enter your username: Alice
   ```
   - Choose a unique username (usernames must be unique per server)

**Expected Output:**
```
[CLIENT] Connected to server at 127.0.0.1:5555
[SUCCESS] Welcome to ClassChat, Alice!

============================================================
ClassChat Commands:
  /private <username> <message>  - Send private message
  /group <room_name> <message>   - Send group message
  /create <room_name>            - Create a chat room
  /join <room_name>              - Join a chat room
  /quit                          - Quit the application
============================================================

You: 
```

---

## Using ClassChat

### Available Commands

#### 1. Create a Chat Room
```
/create <room_name>
```

**Example:**
```
You: /create Networking
[SUCCESS] Chat room 'Networking' created successfully
```

---

#### 2. Join a Chat Room
```
/join <room_name>
```

**Example:**
```
You: /join Networking
[SUCCESS] You have joined 'Networking'
```

Other members will see:
```
[Networking] Alice has joined the chat room
```

---

#### 3. Send a Group Message
```
/group <room_name> <message>
```

**Example:**
```
You: /group Networking Hello everyone! Anyone studying for the CCNA?
```

All members of "Networking" will see:
```
[Networking - Alice] Hello everyone! Anyone studying for the CCNA?
```

---

#### 4. Send a Private Message
```
/private <username> <message>
```

**Example:**
```
You: /private Bob Hey, do you have notes from last class?
```

Bob will see:
```
[Private from Alice] Hey, do you have notes from last class?
```

---

#### 5. Quit the Application
```
/quit
```

This will disconnect you from the server and exit the application.

---

## Testing Scenarios

### Scenario 1: Two-User Private Chat

**Terminal 1 (Server):**
```bash
python Parker_Schemm_901057227_server.py
```

**Terminal 2 (Client - Alice):**
```bash
python Parker_Schemm_901057227_client.py
# Enter username: Alice
```

**Terminal 3 (Client - Bob):**
```bash
python Parker_Schemm_901057227_client.py
# Enter username: Bob
```

**Alice sends to Bob:**
```
You: /private Bob Hey Bob, how are you?
```

**Bob receives and replies:**
```
[Private from Alice] Hey Bob, how are you?
You: /private Alice I'm good! How about you?
```

---

### Scenario 2: Group Chat

**Terminal 1 (Server):**
```bash
python Parker_Schemm_901057227_server.py
```

**Terminal 2 (Alice):**
```bash
python Parker_Schemm_901057227_client.py
# Username: Alice
You: /create CS350
[SUCCESS] Chat room 'CS350' created successfully
You: /group CS350 Welcome to the CS350 study group!
```

**Terminal 3 (Bob):**
```bash
python Parker_Schemm_901057227_client.py
# Username: Bob
You: /join CS350
[SUCCESS] You have joined 'CS350'
[CS350] Bob has joined the chat room
You: /group CS350 Thanks Alice! Excited to study together.
```

**Terminal 4 (Charlie):**
```bash
python Parker_Schemm_901057227_client.py
# Username: Charlie
You: /join CS350
[SUCCESS] You have joined 'CS350'
[CS350] Charlie has joined the chat room
You: /group CS350 Hey everyone!
```

All members see each other's messages in real-time!

---

## Network Configuration

### Running on the Same Machine (Localhost)
- **Server**: Run on `127.0.0.1:5555`
- **Clients**: Connect to `127.0.0.1:5555`

### Running on Different Machines (LAN)

**On the Server Machine:**
1. Find your local IP address:
   - **Windows**: `ipconfig` (look for IPv4 Address)
   - **Mac/Linux**: `ifconfig` or `ip addr show`
   
2. Start server with that IP:
   ```bash
   python firstName_lastName_RUID_server.py 0.0.0.0 5555
   ```
   (0.0.0.0 allows connections from any network interface)

3. **Configure Firewall**: Ensure port 5555 is open

**On Client Machines:**
- Connect using the server's local IP address (e.g., `192.168.1.100`)

---

## Troubleshooting

### Problem: "Connection refused" error

**Solution:**
- Ensure the server is running before starting clients
- Check that the IP address and port are correct
- Verify firewall settings aren't blocking the connection

---

### Problem: "Username already taken"

**Solution:**
- Each user must have a unique username
- Choose a different username or disconnect the existing user

---

### Problem: "User not found or offline"

**Solution:**
- Verify the recipient's username is spelled correctly
- Ensure the recipient is currently connected to the server
- Check the server logs to see active users

---

### Problem: "Chat room does not exist"

**Solution:**
- Create the room first using `/create <room_name>`
- Check the spelling of the room name
- Ask someone to create the room if you don't have permission

---

### Problem: Messages not appearing

**Solution:**
- Check your network connection
- Restart the client
- Ensure you've joined the group before sending group messages

---

## Server Monitoring

The server logs all activities to the console:

```
[SERVER] Server started on 127.0.0.1:5555
[SERVER] Waiting for connections...
[SERVER] New connection from ('127.0.0.1', 54321)
[SERVER] User 'Alice' registered successfully
[SERVER] User 'Bob' registered successfully
[SERVER] Private message from Alice to Bob
[SERVER] Chat room 'CS350' created by Alice
[SERVER] User 'Bob' joined chat room 'CS350'
[SERVER] Group message from Alice to CS350
[SERVER] User 'Alice' disconnected
```

---

## Message Protocol

All messages use JSON format:

```json
{
    "status": "private|group|create|join|quit",
    "sender": "username",
    "receiver": "recipient_or_room_name",
    "text": "message_content"
}
```

---

## Stopping the System

### Stopping a Client
- Type `/quit` and press Enter
- Or press `Ctrl+C` in the terminal

### Stopping the Server
- Press `Ctrl+C` in the server terminal
- All connected clients will be disconnected



## Error Messages Reference

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| Username already taken | Someone is using that username | Choose a different username |
| User not found or offline | Recipient doesn't exist | Check spelling or wait for them to connect |
| Chat room does not exist | Room hasn't been created | Create it with `/create` |
| You are not a member of room | Haven't joined the room | Use `/join <room_name>` first |
| Invalid message format | Command syntax error | Check command format |
| Already a member of room | You've already joined | No action needed |

---

## Technical Details

### Server Architecture
- **Threading Model**: One thread per client connection
- **Data Structures**:
  - `clients`: Dictionary mapping usernames to socket connections
  - `chat_rooms`: Dictionary mapping room names to lists of usernames
- **Concurrency**: Thread-safe operations using locks
- **Protocol**: TCP with newline-delimited JSON messages

### Client Architecture
- **Threading Model**: 
  - Main thread: Handles user input and sending messages
  - Receive thread: Continuously listens for incoming messages
- **Buffering**: Messages are buffered to handle partial receives
- **Timeout**: 5-second timeout on registration

---

**Happy Chatting!**