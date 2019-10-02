import socket


class Proxy:
    def __init__(self):
        self.proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        self.proxy_socket.connect((host, port))
        return self.proxy_socket
