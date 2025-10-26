import socket
import threading
import json
import sys

class ChatServer:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Dictionary to store connected clients {username: socket}
        self.clients = {}
        # Dictionary to store chat rooms {room_name: [list of usernames]}
        self.chat_rooms = {}
        # Lock for thread-safe operations
        self.lock = threading.Lock()
        
    def start(self):
        """Start the server and listen for connections"""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"[SERVER] Server started on {self.host}:{self.port}")
            print("[SERVER] Waiting for connections...")
            
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"[SERVER] New connection from {client_address}")
                
                # Start a new thread to handle this client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down server...")
            self.server_socket.close()
        except Exception as e:
            print(f"[SERVER ERROR] {e}")
            self.server_socket.close()
    
    def handle_client(self, client_socket, client_address):
        """Handle communication with a connected client"""
        username = None
        
        try:
            # Receive username from client
            username_data = client_socket.recv(1024).decode('utf-8')
            username = username_data.strip()
            
            if not username:
                client_socket.close()
                return
            
            # Register the client
            with self.lock:
                if username in self.clients:
                    error_msg = json.dumps({
                        "status": "error",
                        "sender": "SERVER",
                        "receiver": username,
                        "text": "Username already taken. Please try another."
                    })
                    client_socket.send((error_msg + '\n').encode('utf-8'))
                    client_socket.close()
                    return
                
                self.clients[username] = client_socket
                print(f"[SERVER] User '{username}' registered successfully")
            
            # Send success confirmation
            welcome_msg = json.dumps({
                "status": "success",
                "sender": "SERVER",
                "receiver": username,
                "text": f"Welcome to ClassChat, {username}!"
            })
            client_socket.send((welcome_msg + '\n').encode('utf-8'))
            
            # Listen for messages from this client
            while True:
                message_data = client_socket.recv(4096).decode('utf-8')
                
                if not message_data:
                    break
                
                # Handle multiple messages or partial messages
                message_data = message_data.strip()
                if not message_data:
                    continue
                
                # Parse JSON message
                try:
                    message = json.loads(message_data)
                    self.process_message(message, username)
                except json.JSONDecodeError as je:
                    print(f"[SERVER ERROR] JSON decode error: {je}")
                    error_msg = json.dumps({
                        "status": "error",
                        "sender": "SERVER",
                        "receiver": username,
                        "text": "Invalid message format"
                    })
                    client_socket.send((error_msg + '\n').encode('utf-8'))
                    
        except Exception as e:
            print(f"[SERVER ERROR] Error handling client {username}: {e}")
        finally:
            # Clean up when client disconnects
            self.disconnect_client(username)
    
    def process_message(self, message, sender):
        """Process different types of messages"""
        status = message.get('status')
        
        if status == 'private':
            self.handle_private_message(message, sender)
        elif status == 'group':
            self.handle_group_message(message, sender)
        elif status == 'create':
            self.handle_create_room(message, sender)
        elif status == 'join':
            self.handle_join_room(message, sender)
        elif status == 'quit':
            self.disconnect_client(sender)
        else:
            # Send error for unknown status
            error_msg = json.dumps({
                "status": "error",
                "sender": "SERVER",
                "receiver": sender,
                "text": "Unknown message type"
            })
            if sender in self.clients:
                try:
                    self.clients[sender].send((error_msg + '\n').encode('utf-8'))
                except:
                    pass
    
    def handle_private_message(self, message, sender):
        """Handle private messages between two users"""
        receiver = message.get('receiver')
        text = message.get('text')
        
        with self.lock:
            if receiver not in self.clients:
                # Recipient not found
                error_msg = json.dumps({
                    "status": "error",
                    "sender": "SERVER",
                    "receiver": sender,
                    "text": f"User '{receiver}' not found or offline"
                })
                try:
                    self.clients[sender].send((error_msg + '\n').encode('utf-8'))
                except:
                    pass
            else:
                # Forward message to recipient
                forward_msg = json.dumps({
                    "status": "private",
                    "sender": sender,
                    "receiver": receiver,
                    "text": text
                })
                try:
                    self.clients[receiver].send((forward_msg + '\n').encode('utf-8'))
                    print(f"[SERVER] Private message from {sender} to {receiver}")
                except:
                    pass
    
    def handle_group_message(self, message, sender):
        """Handle group chat messages"""
        room_name = message.get('receiver')
        text = message.get('text')
        
        with self.lock:
            if room_name not in self.chat_rooms:
                # Chat room doesn't exist
                error_msg = json.dumps({
                    "status": "error",
                    "sender": "SERVER",
                    "receiver": sender,
                    "text": f"Chat room '{room_name}' does not exist"
                })
                try:
                    self.clients[sender].send((error_msg + '\n').encode('utf-8'))
                except:
                    pass
            elif sender not in self.chat_rooms[room_name]:
                # Sender is not a member of the room
                error_msg = json.dumps({
                    "status": "error",
                    "sender": "SERVER",
                    "receiver": sender,
                    "text": f"You are not a member of '{room_name}'"
                })
                try:
                    self.clients[sender].send((error_msg + '\n').encode('utf-8'))
                except:
                    pass
            else:
                # Broadcast message to all members of the room
                group_msg = json.dumps({
                    "status": "group",
                    "sender": sender,
                    "receiver": room_name,
                    "text": text
                })
                
                for member in self.chat_rooms[room_name]:
                    if member in self.clients:
                        try:
                            self.clients[member].send((group_msg + '\n').encode('utf-8'))
                        except:
                            pass
                
                print(f"[SERVER] Group message from {sender} to {room_name}")
    
    def handle_create_room(self, message, sender):
        """Handle chat room creation"""
        room_name = message.get('receiver')
        
        with self.lock:
            if room_name in self.chat_rooms:
                # Room already exists
                error_msg = json.dumps({
                    "status": "error",
                    "sender": "SERVER",
                    "receiver": sender,
                    "text": f"Chat room '{room_name}' already exists"
                })
                try:
                    self.clients[sender].send((error_msg + '\n').encode('utf-8'))
                except:
                    pass
            else:
                # Create new room and add sender as first member
                self.chat_rooms[room_name] = [sender]
                success_msg = json.dumps({
                    "status": "success",
                    "sender": "SERVER",
                    "receiver": sender,
                    "text": f"Chat room '{room_name}' created successfully"
                })
                try:
                    self.clients[sender].send((success_msg + '\n').encode('utf-8'))
                    print(f"[SERVER] Chat room '{room_name}' created by {sender}")
                except:
                    pass
    
    def handle_join_room(self, message, sender):
        """Handle user joining a chat room"""
        room_name = message.get('receiver')
        
        with self.lock:
            if room_name not in self.chat_rooms:
                # Room doesn't exist
                error_msg = json.dumps({
                    "status": "error",
                    "sender": "SERVER",
                    "receiver": sender,
                    "text": f"Chat room '{room_name}' does not exist"
                })
                try:
                    self.clients[sender].send((error_msg + '\n').encode('utf-8'))
                except:
                    pass
            elif sender in self.chat_rooms[room_name]:
                # User already in room
                error_msg = json.dumps({
                    "status": "error",
                    "sender": "SERVER",
                    "receiver": sender,
                    "text": f"You are already a member of '{room_name}'"
                })
                try:
                    self.clients[sender].send((error_msg + '\n').encode('utf-8'))
                except:
                    pass
            else:
                # Add user to room
                self.chat_rooms[room_name].append(sender)
                success_msg = json.dumps({
                    "status": "success",
                    "sender": "SERVER",
                    "receiver": sender,
                    "text": f"You have joined '{room_name}'"
                })
                try:
                    self.clients[sender].send((success_msg + '\n').encode('utf-8'))
                except:
                    pass
                
                # Notify other members
                notification = json.dumps({
                    "status": "group",
                    "sender": "SERVER",
                    "receiver": room_name,
                    "text": f"{sender} has joined the chat room"
                })
                
                for member in self.chat_rooms[room_name]:
                    if member != sender and member in self.clients:
                        try:
                            self.clients[member].send((notification + '\n').encode('utf-8'))
                        except:
                            pass
                
                print(f"[SERVER] User '{sender}' joined chat room '{room_name}'")
    
    def disconnect_client(self, username):
        """Handle client disconnection"""
        if username:
            with self.lock:
                if username in self.clients:
                    # Remove from active clients
                    try:
                        self.clients[username].close()
                    except:
                        pass
                    del self.clients[username]
                    
                    # Remove from all chat rooms and notify members
                    for room_name, members in self.chat_rooms.items():
                        if username in members:
                            members.remove(username)
                            
                            # Notify remaining members
                            notification = json.dumps({
                                "status": "group",
                                "sender": "SERVER",
                                "receiver": room_name,
                                "text": f"{username} has left the chat room"
                            })
                            
                            for member in members:
                                if member in self.clients:
                                    try:
                                        self.clients[member].send((notification + '\n').encode('utf-8'))
                                    except:
                                        pass
                    
                    print(f"[SERVER] User '{username}' disconnected")

if __name__ == "__main__":
    # You can customize host and port here
    HOST = '127.0.0.1'
    PORT = 5555
    
    if len(sys.argv) == 3:
        HOST = sys.argv[1]
        PORT = int(sys.argv[2])
    
    server = ChatServer(HOST, PORT)
    server.start()