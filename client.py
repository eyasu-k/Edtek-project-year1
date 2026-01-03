import socket
import constants as const
import file_manager as explorer
from constants import DOWNLOAD, DEFAULT_BUFFER_SIZE

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
    debug(f"Uploading a file: size = {file_size}, name = {file_name}")
    request = const.DELIMITER.join([const.UPLOAD, file_name, str(file_size)])
    server.sendall(request.encode())
    debug("first upload request sent. the request:", request)
    server.sendall(file)
    debug("second upload data sent: the data: ")
    debug(file)

def download_file(server: socket.socket, file_name: str, file_size: int)-> None:
    request = const.DELIMITER.join([DOWNLOAD, file_name])
    server.sendall(request)
    file = server.recv(file_size)
    destination = DEFAULT_DOWNLOAD_DST+'/'+file_name
    explorer.create_file(destination, file)

def get_file_list(server: socket.socket)-> list[dict]:
    request = const.DELIMITER.join([const.LIST])
    server.sendall(request.encode())
    response = server.recv(DEFAULT_BUFFER_SIZE).decode()
    _,  files= response.split(const.DELIMITER)
    files_list = []
    for file_data in files.split(const.FILES_DELIMITER):
        new_file_data = {}
        file_name, file_size = file_data.split(const.FILE_ATTRIBUTE_DELIMITER)
        new_file_data["name"] = file_name
        new_file_data["size"] = file_size
        files_list.append(new_file_data)
    return files_list

def delete_file(server: socket.socket, file_name: str)-> None:
    request = const.DELIMITER.join([const.DELETE, file_name])
    server.sendall(request.encode())

def connect_to_server()-> socket.socket:
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))
        return client_socket
    except Exception as e:
        print("Error connecting to the server. more details:\n", e)

def test():
    server_socket = connect_to_server()
    debug("connected to the server!")
    upload_file(server_socket, r"C:\Users\Cyber_Magshimim\Documents\EdTek stuff\week 11 (project)\Edtek-project-year1\שמירת קבצים על השרת עם ממשק גרפי ללקוח.docx.pdf")
    server_socket.close()

def main():
    test()

if __name__ == '__main__':
    main()


