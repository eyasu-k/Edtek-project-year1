import socket
import constants as const

PORT = 12345
DEBUG_PRINTS = False

def debug(*msg)-> None:
    if DEBUG_PRINTS:
        print("Debug print: "*msg)


def foo(*_)-> any:#placeholder
    pass

def serve_client(client: socket.socket)-> bool:#TODO: add exceptions
    actions = {const.UPLOAD: foo, const.DOWNLOAD: foo, const.LIST: foo, const.DELETE: foo}
    try:
        new_request = client.recv(const.DEFAULT_BUFFER_SIZE)
        command, *parameters = new_request.split(const.DELIMITER)
        response = actions[command](parameters)
        client.sendall(response.encode())
        return True
    except:
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
    except:
        return False

def main():
    while start_server():#nice
        continue

if __name__ == '__main__':
    main()
        
        
    


