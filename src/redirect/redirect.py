import socket


class Redirect:
    def __init__(self):
        self.redirection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        self.redirection.connect((host, port))
        return self.redirection
