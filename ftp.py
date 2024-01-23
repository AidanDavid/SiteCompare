# to host FTP server, having trouble with success
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from socket import gethostbyname, gethostname

server = None


def start_server(*, port=4444):
    authorizer = DummyAuthorizer()
    authorizer.add_user("user", "abc123", "C:/Users/aidan/OneDrive/Desktop/CodeFiles/set1", perm="elradfmwMT")
    authorizer.add_anonymous("C:/Users/aidan/OneDrive/Desktop/CodeFiles/set1")

    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = ''

    address = gethostbyname(gethostname())

    server = FTPServer((address, port), handler)
    server.serve_forever()


def close_server():
    if server == None:
        print('Server has not started yet!')
        return

    server.close_all()


start_server()
