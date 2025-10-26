import socket
import threading
import json
import sys

class ChatClient:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        self.running = False
        
    def connect(self):
        """Connect to the server"""
        try:
            self.client_socket.connect((self.host, self.port))
            print(f"[CLIENT] Connected to server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[CLIENT ERROR] Could not connect to server: {e}")
            return False
    
    def register(self, username):
        """Register username with the server"""
        try:
            self.username = username
            self.client_socket.send((username + '\n').encode('utf-8'))
            
            # Wait for server response with timeout
            self.client_socket.settimeout(5.0)
            response = self.client_socket.recv(1024).decode('utf-8').strip()
            self.client_socket.settimeout(None)
            
            if not response:
                print("[ERROR] No response from server")
                return False
            
            message = json.loads(response)
            
            if message.get('status') == 'error':
                print(f"[ERROR] {message.get('text')}")
                return False
            else:
                print(f"[SUCCESS] {message.get('text')}")
                return True
                
        except socket.timeout:
            print("[CLIENT ERROR] Registration timeout - no response from server")
            return False
        except json.JSONDecodeError as e:
            print(f"[CLIENT ERROR] Invalid response from server: {e}")
            return False
        except Exception as e:
            print(f"[CLIENT ERROR] Registration failed: {e}")
            return False
    
    def start(self):
        """Start the client threads"""
        self.running = True
        
        # Thread for receiving messages
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        # Main thread handles sending messages
        self.send_messages()
    
    def receive_messages(self):
        """Continuously receive messages from server"""
        buffer = ""
        
        while self.running:
            try:
                data = self.client_socket.recv(4096).decode('utf-8')
                
                if not data:
                    print("\n[CLIENT] Disconnected from server")
                    self.running = False
                    break
                
                # Add to buffer
                buffer += data
                
                # Process complete messages (ending with newline)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    
                    if line:
                        try:
                            message = json.loads(line)
                            self.display_message(message)
                        except json.JSONDecodeError:
                            print(f"\n[CLIENT ERROR] Invalid message format")
                
            except Exception as e:
                if self.running:
                    print(f"\n[CLIENT ERROR] Error receiving message: {e}")
                break
    
    def display_message(self, message):
        """Display received messages appropriately"""
        status = message.get('status')
        sender = message.get('sender')
        receiver = message.get('receiver')
        text = message.get('text')
        
        if status == 'private':
            print(f"\n[Private from {sender}] {text}")
        elif status == 'group':
            if sender == "SERVER":
                print(f"\n[{receiver}] {text}")
            else:
                print(f"\n[{receiver} - {sender}] {text}")
        elif status == 'success':
            print(f"\n[SUCCESS] {text}")
        elif status == 'error':
            print(f"\n[ERROR] {text}")
        else:
            print(f"\n{sender}: {text}")
        
        # Re-print prompt
        print("You: ", end='', flush=True)
    
    def send_messages(self):
        """Handle sending messages from user input"""
        print("\n" + "="*60)
        print("ClassChat Commands:")
        print("  /private <username> <message>  - Send private message")
        print("  /group <room_name> <message>   - Send group message")
        print("  /create <room_name>            - Create a chat room")
        print("  /join <room_name>              - Join a chat room")
        print("  /quit                          - Quit the application")
        print("="*60 + "\n")
        
        while self.running:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Parse command
                if user_input.startswith('/'):
                    self.parse_command(user_input)
                else:
                    print("[ERROR] Invalid command. Use /private, /group, /create, /join, or /quit")
                    
            except KeyboardInterrupt:
                print("\n[CLIENT] Exiting...")
                self.disconnect()
                break
            except Exception as e:
                print(f"[CLIENT ERROR] {e}")
    
    def parse_command(self, command):
        """Parse and execute user commands"""
        parts = command.split(maxsplit=2)
        
        if not parts:
            return
        
        cmd = parts[0].lower()
        
        if cmd == '/quit':
            self.disconnect()
        
        elif cmd == '/private':
            if len(parts) < 3:
                print("[ERROR] Usage: /private <username> <message>")
                return
            
            receiver = parts[1]
            text = parts[2]
            
            message = {
                "status": "private",
                "sender": self.username,
                "receiver": receiver,
                "text": text
            }
            self.send_message(message)
        
        elif cmd == '/group':
            if len(parts) < 3:
                print("[ERROR] Usage: /group <room_name> <message>")
                return
            
            room_name = parts[1]
            text = parts[2]
            
            message = {
                "status": "group",
                "sender": self.username,
                "receiver": room_name,
                "text": text
            }
            self.send_message(message)
        
        elif cmd == '/create':
            if len(parts) < 2:
                print("[ERROR] Usage: /create <room_name>")
                return
            
            room_name = parts[1]
            
            message = {
                "status": "create",
                "sender": self.username,
                "receiver": room_name,
                "text": ""
            }
            self.send_message(message)
        
        elif cmd == '/join':
            if len(parts) < 2:
                print("[ERROR] Usage: /join <room_name>")
                return
            
            room_name = parts[1]
            
            message = {
                "status": "join",
                "sender": self.username,
                "receiver": room_name,
                "text": ""
            }
            self.send_message(message)
        
        else:
            print(f"[ERROR] Unknown command: {cmd}")
    
    def send_message(self, message):
        """Send a JSON message to the server"""
        try:
            message_json = json.dumps(message)
            self.client_socket.send((message_json + '\n').encode('utf-8'))
        except Exception as e:
            print(f"[CLIENT ERROR] Failed to send message: {e}")
            self.running = False
    
    def disconnect(self):
        """Disconnect from the server"""
        self.running = False
        
        try:
            # Send quit message
            quit_message = {
                "status": "quit",
                "sender": self.username,
                "receiver": "",
                "text": ""
            }
            self.client_socket.send(json.dumps(quit_message).encode('utf-8'))
        except:
            pass
        
        try:
            self.client_socket.close()
        except:
            pass
        
        print("[CLIENT] Disconnected from server")
        sys.exit(0)

def main():
    print("="*60)
    print("Welcome to ClassChat!")
    print("="*60)
    
    # Get connection details
    host = input("Enter server IP address (default: 127.0.0.1): ").strip()
    if not host:
        host = '127.0.0.1'
    
    port_input = input("Enter server port (default: 5555): ").strip()
    if not port_input:
        port = 5555
    else:
        try:
            port = int(port_input)
        except ValueError:
            print("[ERROR] Invalid port number. Using default 5555")
            port = 5555
    
    # Get username
    username = input("Enter your username: ").strip()
    while not username:
        username = input("Username cannot be empty. Enter your username: ").strip()
    
    # Create and connect client
    client = ChatClient(host, port)
    
    if not client.connect():
        return
    
    if not client.register(username):
        return
    
    # Start client
    client.start()

if __name__ == "__main__":
    main()