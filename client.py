import socket
import constants as const
import file_manager as explorer
from constants import DOWNLOAD

DEBUG_PRINTS = True
IP = "127.0.0.1"
PORT = 12345

DEFAULT_DOWNLOAD_DST = explorer.get_downloads_path()


def debug(*msg)-> None:
    if DEBUG_PRINTS:
        print("Debug print: ", *msg)

def upload_file(server: socket.socket, file_path: str)-> None:
    file = explorer.get_file(file_path)
    file_size = len(file)
    file_name = explorer.get_file_name(file_path)
    request = const.DELIMITER.join([const.UPLOAD, file_name, file_size])
    server.sendall(request)
    server.sendall(file)

def download_file(server: socket.socket, file_name: str, file_size: int)-> None:
    request = const.DELIMITER.join([DOWNLOAD, file_name])
    server.sendall(request)
    file = server.recv(file_size)
    destination = DEFAULT_DOWNLOAD_DST+'/'+file_name
    explorer.create_file(destination, file)


def connect_to_server(ip: str, port: int)-> socket.socket:
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        return client_socket
    except Exception as e:
        print("Error connecting to the server. more details:\n", e)


def main():
    pass

if __name__ == '__main__':
    main()


