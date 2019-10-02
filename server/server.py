import socket
import select

from proxy.proxy import Proxy

REDIRECT_TO = {'host': 'mail.ru', 'port': 80}

UNACCEPTED_CONN_COUNT = 10
BUFFER_SIZE = 4096


class Server:
    input_list = []
    channel = {}

    def __init__(self, config):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((config.host, config.port))
        self.server_socket.listen(UNACCEPTED_CONN_COUNT)

    def start(self):
        print('Server started\n')

        self.input_list.append(self.server_socket)

        while True:
            read_list, _, _ = select.select(self.input_list, [], [])
            for s in read_list:
                if s == self.server_socket:
                    redirect = Proxy().start(REDIRECT_TO.get('host'), REDIRECT_TO.get('port'))

                    client_socket, client_address = self.server_socket.accept()
                    if redirect:
                        print(f'{client_address[0]}:{client_address[1]} is connected')

                        self.input_list.append(client_socket)
                        self.input_list.append(redirect)

                        self.channel[client_socket] = redirect
                        self.channel[redirect] = client_socket
                    else:
                        print(f'Cannot reach remote server, closing connection with client: {client_address[0]}')
                        client_socket.close()
                    break

                data = s.recv(BUFFER_SIZE)
                if len(data) == 0:
                    self.close(s)
                    break
                else:
                    print(data)
                    self.channel[s].send(data)

    def close(self, s):
        print(f'{s.getpeername()[0]}:{s.getpeername()[1]} has disconnected')

        self.input_list.remove(s)
        self.input_list.remove(self.channel[s])
        out = self.channel[s]

        self.channel[out].close()
        self.channel[s].close()

        del self.channel[out]
        del self.channel[s]
