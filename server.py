import socket
import constants as const
import file_manager as explorer
import os

from ServerException import ServerException

PORT = 12345
DEBUG_PRINTS = True

def debug(*msg)-> None:
    if DEBUG_PRINTS:
        print("Debug print: ", *msg)

def error(client_socket: socket.socket, message: str)-> None:
    error_msg = const.DELIMITER.join([const.ERROR, message])
    client_socket.sendall(error_msg.encode())

def receive_file(client: socket.socket, file_name: str, file_size: str, *_)-> None:# this function handles upload requests from the client.
    if int(file_size) > const.MAXIMUM_FILE_SIZE:
        error(client, f"Maximum file upload size is exceeded. The maximum file upload size is {const.MAXIMUM_FILE_SIZE}")
        raise ServerException(f"Maximum file upload size is exceeded. The maximum file upload size is {const.MAXIMUM_FILE_SIZE}")

    debug("The client has chosen to upload a file.")
    ack_response = const.DELIMITER.join([const.R_UPLOAD, const.ACK]).encode()
    client.sendall(ack_response) #sending an acknowledgement message to the client so that it can send the file contents
    debug("Sent an acknowledgement message to the client. the response =", ack_response.decode())

    #preparing a location for the file the server is going to receive
    explorer.create_new_folder(const.SERVER_FILES_FOLDER_NAME)
    file_path = os.path.join(const.SERVER_FILES_FOLDER_NAME, file_name)

    #creating the file after receiving its contents
    file_content = client.recv(int(file_size)+const.EXTRA_BUFFER_SIZE)#the download buffer is increased by EXTRA_BUFFER_SIZE in case the file size is increased when it's transported
    explorer.create_file(file_path, file_content)
    #sending a final message letting the client know that the file is received

    debug("Downloaded the file from the client. the file is now at:", file_path)
    success_message = const.DELIMITER.join([const.R_UPLOAD, const.SUCCESS]).encode()
    client.sendall(success_message)#sending to the client a success message
    debug("Sent a success message to the client. the success message:", success_message.decode())

def send_file(client: socket.socket, file_name: str, *_)-> None:
    debug("Responding to the user downloading a file: ")
    debug("The file to send to the user: ", file_name)
    file_path = const.SERVER_FILES_FOLDER_NAME+'/'+file_name
    if not explorer.file_exists(file_path):
        error(client, "File doesn't exist in the server.")
        raise ServerException("User tried to download a non-existing file.")
    ack_message = const.DELIMITER.join([const.R_DOWNLOAD, const.ACK]).encode()
    client.sendall(ack_message)
    debug("ack message sent to the client, the message:", ack_message)

    file_contents = explorer.get_file(file_path)
    client.sendall(file_contents)

def send_file_list(client: socket.socket, *_)-> None:
    debug("New requests from the client to list a file.")
    files = []
    for file in explorer.get_files_list(const.SERVER_FILES_FOLDER_NAME):
        file_size = str(explorer.get_file_size(const.SERVER_FILES_FOLDER_NAME+'/'+file))
        files.append(file+const.FILE_ATTRIBUTE_DELIMITER+file_size)
    files_joined = const.FILES_DELIMITER.join(files)
    response = const.R_LIST+const.DELIMITER+files_joined
    response_length = len(response)

    debug("Files list response length:", response_length)
    r_list_buffer_size_response = const.DELIMITER.join([const.R_LIST, str(response_length)])
    client.sendall(r_list_buffer_size_response.encode())

    ack_response = client.recv(const.DEFAULT_BUFFER_SIZE).decode()
    if ack_response == const.ACK:
        client.sendall(response.encode())
    else:
        raise ServerException("Error sending files list to the client.")

def delete_file(_client: socket.socket, file_name: str,*_)-> None:
    file_path = const.SERVER_FILES_FOLDER_NAME+'/'+file_name
    explorer.delete_file(file_path)

def serve_client(client: socket.socket)-> bool:
    actions = {const.UPLOAD: receive_file, const.DOWNLOAD: send_file, const.LIST: send_file_list, const.DELETE: delete_file}
    try:
        new_request = client.recv(const.DEFAULT_BUFFER_SIZE).decode()
        debug("New client request:", new_request)
        command, *parameters = new_request.split(const.DELIMITER)
        try:
            actions[command](client, *parameters)
        except ServerException as e:
            debug("Server Exception:", e.value)
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
        
        
    


