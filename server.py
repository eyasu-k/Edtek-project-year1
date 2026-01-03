import socket
import constants as const
import file_manager as explorer

PORT = 12345
DEBUG_PRINTS = False

def debug(*msg)-> None:
    if DEBUG_PRINTS:
        print("Debug print: ", *msg)

def receive_file(client: socket.socket, file_name: str, file_size: str, *_)-> None:
    file_path = const.SERVER_FILES_FOLDER_NAME+'/'+file_name
    explorer.create_new_folder(const.SERVER_FILES_FOLDER_NAME)
    file_content = client.recv(int(file_size))
    explorer.create_file(file_path, file_content)
    client.sendall(const.SUCCESS)

def send_file(client: socket.socket, file_name: str, *_)-> None:
    file_path = const.SERVER_FILES_FOLDER_NAME+'/'+file_name
    file_contents = explorer.get_file(file_path)
    client.sendall(file_contents)

def send_file_list(client: socket.socket, *_)-> None:
    files = explorer.get_files_list(const.SERVER_FILES_FOLDER_NAME)
    files = const.FILES_DELIMITER.join(files)
    client.sendall(files.encode())

def delete_file(client: socket.socket, file_name: str,*_)-> None:
    file_path = const.SERVER_FILES_FOLDER_NAME+'/'+file_name
    explorer.delete_file(file_path)

def serve_client(client: socket.socket)-> bool:#TODO: add exceptions
    actions = {const.UPLOAD: receive_file, const.DOWNLOAD: send_file, const.LIST: send_file_list, const.DELETE: delete_file}
    try:
        new_request = client.recv(const.DEFAULT_BUFFER_SIZE)
        command, *parameters = new_request.split(const.DELIMITER)
        actions[command](client, parameters)
        return True
    except Exception as e:
        print("Internal server error:\n", e)
        return False #the client disconnected or there is an error in the server
    
    
    
def start_server()-> bool:#TODO: add exceptions if necessary...
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as new_socket:
            new_socket.bind(("", PORT))
            new_socket.listen(1)
            client, _ = new_socket.accept()
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
        
        
    


