import sys

from server.server import Server


class Config:
    def __init__(self):
        self.host = ''
        self.port = 8081


if __name__ == '__main__':
    config = Config()
    server = Server(config)

    try:
        server.start()
    except KeyboardInterrupt:
        print('Server stopped')
        sys.exit(1)
