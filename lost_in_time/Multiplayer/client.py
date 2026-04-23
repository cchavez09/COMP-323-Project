import socket
import json

port = 5555

class Client:
    def __init__(self, server_ip):
        self.port = port
        self.server_ip = server_ip
        self.server_addr = (self.server_ip, self.port)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.player_id = None
        self.game_state = None
        self.paused = False
        self.menu = False
        self.disconnected = False
        self.level = None

        # Does not need to wait for response to send next message
        # Prevent Freezing
        self.client.setblocking(False)

    def send(self, type, data):
        # Send data to server
        message = {"type": type, "data": data}
        message = json.dumps(message).encode("ascii")
        self.client.sendto(message, self.server_addr)

    def receive(self):
        # Receive data from server call handle response to handle data
        while True:
            try:
                data, addr = self.client.recvfrom(4096)
                message = json.loads(data.decode("ascii"))
                self.handle_response(message)
            except socket.error:
                break

    def handle_response(self, message):
        type = message.get("type")
        data = message.get("data")

        # Check to see type of message and handle based on message
        if type == "connect":
            self.player_id = data.get("player_id")
        elif type == "disconnect":
            self.game_state = None
            self.disconnected = True
        elif type == "state":
            self.game_state = data
        elif type == "pause":
            self.paused = data.get("pause")
        elif type == "menu":
            self.menu = True
        elif type == "level_select":
            self.level = data.get("level")
    