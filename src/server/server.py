import socket
import select

from src.redirect.redirect import Redirect

REDIRECT_TO = {'host': 'mail.ru', 'port': 80}

UNACCEPTED_CONN_COUNT = 10
BUFFER_SIZE = 4096

ALLOWED_REQUESTS = [b'GET', b'POST']
ALLOWED_RESPONSES = [b'200', b'301', b'302']


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
                    self.accept_request()
                    break

                data = s.recv(BUFFER_SIZE)
                if len(data) == 0:
                    self.close(s)
                    break
                else:
                    self.send_response(s, data)

    def accept_request(self):
        redirect = Redirect().start(REDIRECT_TO.get('host'), REDIRECT_TO.get('port'))

        client_socket, client_address = self.server_socket.accept()
        if redirect:
            print(f'{client_address[0]}:{client_address[1]} is connected')

            self.input_list.append(client_socket)
            self.input_list.append(redirect)

            self.channel[client_socket] = redirect
            self.channel[redirect] = client_socket
        else:
            print('Cant establish connection with remote server'),
            print('Closing connection with client side', client_address[0])
            client_socket.close()

    def close(self, s):
        print(f'{s.getpeername()[0]}:{s.getpeername()[1]} has disconnected')

        self.input_list.remove(s)
        self.input_list.remove(self.channel[s])
        out = self.channel[s]

        self.channel[out].close()

        self.channel[s].close()

        del self.channel[out]
        del self.channel[s]

    def send_response(self, s, data):
        print(self.parse_data(data))
        self.channel[s].send(data)

    def parse_data(self, data):
        data_first_line = data.split(b'\n')[0].split()

        if data_first_line[0] in ALLOWED_REQUESTS:
            print('\n')
            return self.parse_request(data)

        elif data_first_line[1] in ALLOWED_RESPONSES:
            return self.parse_response(data)
        else:
            print('Unknown request/response')
            return data_first_line

    @staticmethod
    def parse_request(request) -> str:
        request = request.split(b'\n')
        first_line = request[0].split()

        return first_line[0] + b' ' + first_line[1] + b' ' + first_line[2]

    def parse_response(self, response) -> str:
        response = response.split(b'\n')
        first_line = response[0].split()
        print('\n')

        return first_line[0] + b' ' + first_line[1]
