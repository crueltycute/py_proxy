import socket
import select
import ssl

from proxy.proxy import Proxy
from proxy.ca import CertificateAuthority

REDIRECT_TO = {'host': 'mail.ru', 'port': 443}

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
                    client_socket, client_address = self.server_socket.accept()
                    proxy = Proxy().start(REDIRECT_TO.get('host'), REDIRECT_TO.get('port'))

                    if proxy:
                        print(f'{client_address[0]}:{client_address[1]} is connected\n')

                        self.input_list.append(client_socket)
                        self.input_list.append(proxy)

                        self.channel[client_socket] = proxy
                        self.channel[proxy] = client_socket
                    else:
                        print(f'Cannot reach remote server, closing connection with client: {client_address[0]}\n')
                        client_socket.close()
                    break

                data = s.recv(BUFFER_SIZE)
                if len(data) == 0:
                    self.close(s)
                    break
                else:
                    if self.has_CONNECT(data):
                        self.wrap_with_ssl(s, proxy)

                    print(data)
                    self.channel[s].send(data)

    @staticmethod
    def has_CONNECT(data):
        try:
            return data.split(b'\n')[0].split()[0] == b'CONNECT'
        except IndexError:
            return False

    @staticmethod
    def wrap_with_ssl(s, proxy):
        print('trying to wrap proxy with ssl')

        ca = CertificateAuthority()

        s.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')
        ss = ssl.wrap_socket(s, certfile=ca.ca_file, server_side=True, do_handshake_on_connect=False)
        ss.do_handshake()

        request = ss.recv(40960)
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        s_sock = context.wrap_socket(proxy, server_hostname=REDIRECT_TO.get('host'))
        s_sock.send(request)

    def close(self, s):
        print(f'{s.getpeername()[0]}:{s.getpeername()[1]} has disconnected\n')

        self.input_list.remove(s)
        self.input_list.remove(self.channel[s])
        out = self.channel[s]

        self.channel[out].close()
        self.channel[s].close()

        del self.channel[out]
        del self.channel[s]
