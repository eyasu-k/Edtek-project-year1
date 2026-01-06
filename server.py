import socket
import constants as const
import file_manager as explorer
from constants import DELIMITER

PORT = 12345
DEBUG_PRINTS = True

def debug(*msg)-> None:
    if DEBUG_PRINTS:
        print("Debug print: ", *msg)

def receive_file(client: socket.socket, file_name: str, file_size: str, *_)-> None:
    debug("The client has chosen to upload a file.")

    client.sendall(const.SUCCESS.encode())

    file_path = const.SERVER_FILES_FOLDER_NAME+'/'+file_name
    explorer.create_new_folder(const.SERVER_FILES_FOLDER_NAME)
    file_content = client.recv(int(file_size))
    explorer.create_file(file_path, file_content)
    client.sendall(const.SUCCESS.encode())

def send_file(client: socket.socket, file_name: str, *_)-> None:
    file_path = const.SERVER_FILES_FOLDER_NAME+'/'+file_name
    file_contents = explorer.get_file(file_path)
    client.sendall(file_contents)

def send_file_list(client: socket.socket, *_)-> None:
    files = []
    for file in explorer.get_files_list(const.SERVER_FILES_FOLDER_NAME):
        file_size = str(explorer.get_file_size(const.SERVER_FILES_FOLDER_NAME+'/'+file))
        files.append(file+const.FILE_ATTRIBUTE_DELIMITER+file_size)
    files_joined = const.FILES_DELIMITER.join(files)
    response = const.R_LIST+DELIMITER+files_joined
    client.sendall(response.encode())

def delete_file(_client: socket.socket, file_name: str,*_)-> None:
    file_path = const.SERVER_FILES_FOLDER_NAME+'/'+file_name
    explorer.delete_file(file_path)

def serve_client(client: socket.socket)-> bool:
    actions = {const.UPLOAD: receive_file, const.DOWNLOAD: send_file, const.LIST: send_file_list, const.DELETE: delete_file}
    try:
        new_request = client.recv(const.DEFAULT_BUFFER_SIZE).decode()
        debug("New client request:", new_request)
        command, *parameters = new_request.split(const.DELIMITER)
        actions[command](client, *parameters)
        return True
    except Exception as e:
        print("Internal server error:\n", e)
        return False #the client disconnected or there is an error in the server
    
    
    
def start_server()-> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as new_socket:
            new_socket.bind(("", PORT))
            new_socket.listen(1)
            client, _ = new_socket.accept()
            debug("Connected to the client.")
            while serve_client(client):
                continue
        return True
    except Exception as e:
        print("Error starting the server. more details:\n", e)
        return False

def main():
    while start_server():#nice
        continue

if __name__ == '__main__':
    main()
        
        
    


