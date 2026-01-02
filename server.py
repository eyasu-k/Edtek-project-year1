import socket
import constants as const

PORT = 12345
DEBUG_PRINTS = False

def debug(*msg: any)-> None:
    if DEBUG_PRINTS:
        print("Debug print: "*msg)


def ph(*_)-> any:#ph = place holder
    pass

def serve_client(client: socket.socket)-> bool:#TODO: add exceptions
    actions = {const.UPLOAD: ph, const.DOWNLOAD: ph, const.LIST: ph, const.DELETE: ph}
    try:
        new_request = client.recv(const.DEFAULT_BUFFER_SIZE)
        command, *parameters = new_request.split(const.DELIMITER)
        response = actions[command](parameters)
        client.sendall(response.encode())
        return True
    except:
        return False #the client disconnected or there is an error in the server
    
    
    
def start_server()-> bool:#TODO: add exceptions if neseccary...
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as new_socket:
            new_socket.bind(("", PORT))
            ear_socket = new_socket.listen(1)
            client, _ = ear_socket.accept()
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
        
        
    


