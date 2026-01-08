import socket
from ClientException import ClientException

import constants as const
import file_manager as explorer

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

DEBUG_PRINTS = True
IP = "127.0.0.1"
PORT = 12345

DEFAULT_DOWNLOAD_DST = explorer.get_downloads_path()

WIDTH = 1280
HEIGHT = 720

FILES_LIST_WIDTH, FILES_LIST_HEIGHT = 800, 720
ACTIONS_LIST_WIDTH, ACTIONS_LIST_HEIGHT = 480, 700

BACKGROUND_COLOR = "#FFFFFF"
BACKGROUND_COLOR2 = "#3d3d3d"
DEFAULT_BUTTON_BG = "#3D3D3D"

BUTTON_COLORS = {"update_file_list": "#296AC9", "quit": "#C94A3D", "upload": "#5CC950"}

TEXT_COLOR = "#FFFFFF"
FONT = ("Unispace", 13)


def debug(*msg)-> None:
    if DEBUG_PRINTS:
        print("Debug print: ", *msg)

#functions that deal with connections with the server:
def upload_file(server: socket.socket, file_path: str)-> None:
    file = explorer.get_file(file_path)
    file_size, file_name = len(file), explorer.get_file_name(file_path)

    if file_size > const.MAXIMUM_FILE_SIZE:
        raise ClientException(f"Maximum file Size Exceeded. All files must be less than {explorer.format_file_size(const.MAXIMUM_FILE_SIZE)}.")

    debug(f"Uploading a file: size = {file_size}, name = {file_name}")

    request = const.DELIMITER.join([const.UPLOAD, file_name, str(file_size)])
    server.sendall(request.encode())# sending to the server the file data so the server could choose the right buffer size to download the file
    debug("first upload request sent. the request:", request)
    response = server.recv(1024).decode()
    response_type, response_msg = response.split(const.DELIMITER)
    debug("server response:", response)
    if response_type == const.ERROR:
        debug("ClientException:", response_msg)
        raise ClientException(response_msg)

    if response_type == const.R_UPLOAD and response_msg == const.ACK:#if the server doesn't acknowledge the file data sent, the function skips the code below and returns False.
        server.sendall(file)
        debug("second upload: the whole file content sent to the server.")
        last_response = server.recv(const.DEFAULT_BUFFER_SIZE).decode()
        _response_type, result = last_response.split(const.DELIMITER)
        debug("last response from the server:", last_response)
        if result != const.SUCCESS:
            raise ClientException("Upload failed, host didn't respond with a success message.")
    else:
        raise ClientException("Upload failed, host didn't respond with an ack message.")

def download_file(server: socket.socket, file_name: str, file_size: int)-> None:
    debug(f"a new request to download a file: filename = {file_name}, file size = {file_size}")
    request = const.DELIMITER.join([const.DOWNLOAD, file_name])
    debug(f"the request message:", request)
    server.sendall(request.encode())
    server_confirmation = server.recv(const.DEFAULT_BUFFER_SIZE).decode()
    response_type, response_msg = server_confirmation.split(const.DELIMITER)
    debug("Server's response for the request:", server_confirmation)

    if response_type == const.R_DOWNLOAD and response_msg == const.ERROR:
        raise ClientException(response_msg)

    if response_type == const.R_DOWNLOAD and response_msg == const.ACK:
        file = server.recv(int(file_size)+const.EXTRA_BUFFER_SIZE)
        #using tkinter file dialog to choose the destination of the file to be downloaded
        destination = filedialog.asksaveasfilename(initialfile=file_name, initialdir=DEFAULT_DOWNLOAD_DST, filetypes=explorer.get_file_types(file_name))
        if not destination:#incase the user canceled file download
            debug("file download canceled.")
            raise ClientException("File download canceled.")
        explorer.create_file(destination, file)
        debug("file downloaded successfully!!")

def get_file_list(server: socket.socket)-> dict:
    debug("a new request to receive the files list.")
    request = const.DELIMITER.join([const.LIST])
    debug("the request message:", request)
    server.sendall(request.encode())

    #sending a 'list' request to the server to receive the buffer size to receive the files list
    buffer_size_response = server.recv(const.DEFAULT_BUFFER_SIZE).decode()
    _response_type, buffer_size = buffer_size_response.split(const.DELIMITER)
    buffer_size = int(buffer_size)

    server.sendall(const.ACK.encode())#sending an ack message to the server so it can send the files list now
    response = server.recv(buffer_size+const.EXTRA_BUFFER_SIZE).decode()#receiving the files list with the adjusted buffer size
    debug(f"servers response for the files list request: {response}")
    _,  files= response.split(const.DELIMITER)
    files_data = {}
    if not files:
        return files_data #returns an empty dict if the files list is empty
    for file_data in files.split(const.FILES_DELIMITER):
        file_name, file_size = file_data.split(const.FILE_ATTRIBUTE_DELIMITER)
        files_data[file_name] = file_size
    debug("the extracted data from the server response:", files_data)
    return files_data

def delete_file(server: socket.socket, file_name: str)-> None:
    debug("new request from the client to delete a file: file name:", file_name)
    request = const.DELIMITER.join([const.DELETE, file_name])
    debug("the request sent to the server:", request)
    server.sendall(request.encode())
    debug("request sent successfully")

def connect_to_server()-> socket.socket:
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))
        return client_socket
    except Exception as e:
        print("Error connecting to the server. more details:\n", e)

#functions that deal with the gui
def update_files_list(main_frame: tk.Frame, server: socket.socket)-> None:
    for widget in main_frame.winfo_children():
        if not isinstance(widget, tk.Scrollbar):
            widget.destroy()
    main_frame.place(y=0, x = 0)
    my_canvas = tk.Canvas(main_frame, width= FILES_LIST_WIDTH-20, height=FILES_LIST_HEIGHT, bg=BACKGROUND_COLOR)
    my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    my_scrollbar = tk.ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=my_canvas.yview)
    my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    my_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
    second_frame = tk.Frame(my_canvas, bg=BACKGROUND_COLOR, height = FILES_LIST_HEIGHT)
    my_canvas.create_window((0, 0), window=second_frame, anchor="nw")

    files_list = get_file_list(server)
    row = 0
    for row, file_data in enumerate(files_list.items()):

        file_name, file_size = file_data
        file_data = f"{explorer.format_file_name(file_name, 40):<40}|{explorer.format_file_size(int(file_size)):<10}"

        tk.Label(second_frame, text = file_data, font = FONT).grid(row = row, column = 0, pady = 10, padx = 10)


        download_button = tk.Button(second_frame, text="download", font = FONT, highlightthickness=0, borderwidth=0,
                                    relief=tk.FLAT, width = 10,
                                    command = lambda name = file_name, size = file_size: download_file_dialog(server, name, size))
        download_button.grid(row = row, column = 1, pady=0, padx = 10)


        delete_button = (tk.Button(second_frame, text="delete", font = FONT, highlightthickness=0, borderwidth=0,
                                   relief=tk.FLAT, width = 10,
                                   command = lambda name = file_name: delete_file_dialog(server, name, main_frame)))
        delete_button.grid(row = row, column = 2, pady=0, padx = 10)

    tk.Label(second_frame, text="", font=FONT).grid(row=row+1, column=0, pady=10, padx=10)#adding an empty label at the end of the files list so no file will be hidden from the user when the files list is a lot
def upload_file_dialog(server: socket.socket, files_list_frame: tk.Frame)-> None:
    file_name = tk.filedialog.askopenfilename(initialdir='/', title="Select a file", filetypes=(("all files", "*.*"), ("", "")))
    debug(f"Chosen file--> filename: {file_name}")
    try:
        upload_file(server, file_name)
    except ClientException as e:
        messagebox.showerror("Client Exception", f"File upload failed. more details:\n{e.value}")
    except Exception as e:
        messagebox.showerror("Error Uploading file", f"details about the error: {str(e)}")
    else:
        messagebox.showinfo("File Uploaded Successfully", "Your file has been uploaded successfully.")
        update_files_list(files_list_frame, server)#refreshing the files list

def download_file_dialog(server: socket.socket, file_name: str, file_size: int)-> None:
    debug("Download file dialog:")
    try:
        download_file(server, file_name, file_size)
    except ClientException as e:
        messagebox.showerror("File Download Error", f"The file download failed. more details:\n{e.value}")
    else:
        messagebox.showinfo("File Download Info", f"File downloaded successfully")
        debug(f"the file '{file_name}' downloaded successfully!. updating the files list")

def delete_file_dialog(server: socket.socket, file_name: str, files_list_frame: tk.Frame)-> None:
    delete_choice = messagebox.askyesno("Delete File", f"Files are permanently deleted only in the server.\nAre you sure you want to delete '{explorer.get_file_name(file_name)}?'")
    if delete_choice == tk.NO:
        return
    try:
        delete_file(server, file_name)
        update_files_list(files_list_frame, server)
    except ClientException as e:
        debug("ClientException:", str(e))
        messagebox.showerror("File Deletion Error", "Encountered an error while trying to delete a file. more details:"+str(e))

#functions that deal with both the gui and the client-server connections:
def quit_app(window_root: tk.Tk, server_socket: socket.socket)-> None:
    server_socket.close()
    window_root.quit()

def main():

    try:
        server_socket = connect_to_server()
        if server_socket is None:
            raise Exception("Host server not found.")
    except Exception as e:
        root =tk.Tk()#a tkinter root for the message box below
        root.withdraw()#hiding the root widow so only the message box will be shown
        messagebox.showerror("Connection Error.", "Error Connecting to the Eyasu drive server. More details:\n"+str(e))
        root.quit()
        exit(-1)

    update_list = lambda : update_files_list(files_list_frame, server_socket)

    root = tk.Tk()
    root.title("Eyasu Drive 1.0")
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.configure(bg=BACKGROUND_COLOR)
    root.resizable(False, False)

    files_list_frame = tk.Frame(root, bg = BACKGROUND_COLOR,height= FILES_LIST_HEIGHT, width = FILES_LIST_WIDTH)
    files_list_frame.pack(padx = 10, pady = 10, side = tk.LEFT)

    files_list_frame = tk.Frame(files_list_frame, width = FILES_LIST_WIDTH, height = FILES_LIST_HEIGHT)

    actions_list_frame = tk.Frame(root, bg = BACKGROUND_COLOR2,height= ACTIONS_LIST_HEIGHT, width = ACTIONS_LIST_WIDTH)
    actions_list_frame.place(x = FILES_LIST_WIDTH +10, y = 10)#pack(padx = 10, pady = 10, side = tk.LEFT)

    get_files_list_btn = tk.Button(actions_list_frame, text = "Update files list", fg = TEXT_COLOR, font = FONT,
                                   bg=BUTTON_COLORS["update_file_list"], width = 45
                                   , borderwidth=0, command = update_list)
    get_files_list_btn.pack(padx = 5, pady = 10, side=tk.TOP)

    upload_file_btn = tk.Button(actions_list_frame, text = "Upload a file", fg = TEXT_COLOR, font = FONT,
                                   bg=BUTTON_COLORS["upload"], width = 45
                                   , borderwidth=0, command = lambda: upload_file_dialog(server_socket, files_list_frame))
    upload_file_btn.pack(padx = 5, pady = 10, side=tk.TOP)

    quit_btn = tk.Button(actions_list_frame, text = "Quit", fg = TEXT_COLOR, font = FONT,
                                   bg=BUTTON_COLORS["quit"], width = 45
                                   , borderwidth=0, command = lambda: quit_app(root, server_socket))
    quit_btn.pack(padx = 5, pady = 10, side=tk.TOP)

    update_list()

    root.mainloop()


if __name__ == '__main__':
    main()


