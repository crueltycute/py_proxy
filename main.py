import sys

from server.server import Server


LOCAL_HOST = '0.0.0.0'
DEFAULT_PORT = 8081


class Config:
    def __init__(self, host=LOCAL_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port

    def __str__(self):
        return f'Server starting on {self.host}:{self.port}\n'


if __name__ == '__main__':
    if len(sys.argv) > 1:
        config = Config(port=sys.argv[1])
    else:
        config = Config()

    print(config)

    server = Server(config)

    try:
        server.start()
    except KeyboardInterrupt:
        print('Server stopped')
        sys.exit(1)
