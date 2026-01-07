import socket
from fileinput import filename

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
BACKGROUND_COLOR2 = "#FFFFFF"
DEFAULT_BUTTON_BG = "#3D3D3D"

BUTTON_COLORS = {"update_file_list": "#296AC9", "quit": "#C94A3D", "upload": "#5CC950"}

TEXT_COLOR = "#FFFFFF"
FONT = ("Unispace", 13)


def debug(*msg)-> None:
    if DEBUG_PRINTS:
        print("Debug print: ", *msg)

#functions that deal with connections with the server:
def upload_file(server: socket.socket, file_path: str)-> bool:
    file = explorer.get_file(file_path)
    file_size = len(file)
    file_name = explorer.get_file_name(file_path)
    debug(f"Uploading a file: size = {file_size}, name = {file_name}")
    request = const.DELIMITER.join([const.UPLOAD, file_name, str(file_size)])
    server.sendall(request.encode())
    debug("first upload request sent. the request:", request)
    response = server.recv(1024).decode()
    if response == const.SUCCESS:
        server.sendall(file)
        debug("second upload data sent: the data: ")
        debug(file)
        return True
    return False

def download_file(server: socket.socket, file_name: str, file_size: int)-> None:
    debug(f"a new request to download a file: filename = {file_name}, file size = {file_size}")
    request = const.DELIMITER.join([const.DOWNLOAD, file_name])
    debug(f"the request message:", request)
    server.sendall(request.encode())
    file = server.recv(file_size)
    destination = DEFAULT_DOWNLOAD_DST+'/'+file_name
    explorer.create_file(destination, file)
    debug("file downloaded successfully!!")

def get_file_list(server: socket.socket)-> dict:
    debug("a new request to receive the files list.")
    request = const.DELIMITER.join([const.LIST])
    debug("the request message:", request)
    server.sendall(request.encode())
    response = server.recv(const.DEFAULT_BUFFER_SIZE).decode()
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
    my_canvas = tk.Canvas(main_frame, width= FILES_LIST_WIDTH-20, height=FILES_LIST_HEIGHT, bg=BACKGROUND_COLOR2)
    my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    my_scrollbar = tk.ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=my_canvas.yview)
    my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    my_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
    second_frame = tk.Frame(my_canvas, bg=BACKGROUND_COLOR2, height = FILES_LIST_HEIGHT)
    my_canvas.create_window((0, 0), window=second_frame, anchor="nw")

    files_list = get_file_list(server)
    for row, file_data in enumerate(files_list.items()):

        file_name, file_size = file_data
        file_data = f"{file_name:<40}|{file_size:<10}"

        tk.Label(second_frame, text = file_data, font = FONT).grid(row = row, column = 0, pady = 10, padx = 10)


        download_button = tk.Button(second_frame, text="download", font = FONT, highlightthickness=0, borderwidth=0,
                                    relief=tk.FLAT,
                                    command = lambda name = file_name, size = file_size: tk.messagebox.showinfo( "download",f"download {name}, size: {size}"))
        download_button.grid(row = row, column = 1, pady=0, padx = 10)


        delete_button = (tk.Button(second_frame, text="delete", font = FONT, highlightthickness=0, borderwidth=0,
                                   relief=tk.FLAT,
                                   command = lambda name = file_name: tk.messagebox.showinfo("delete", f"delete {name}")))
        delete_button.grid(row = row, column = 2, pady=0, padx = 10)

def upload_file_dialog(server: socket.socket)-> str:
    file_name = tk.filedialog.askopenfilename(initialdir='/', title="Select a file", filetypes=(("all files", "*.*"), ("", "")))
    debug(f"Chosen file--> filename: {file_name}")
    upload_file(server, file_name)
    return file_name

#functions that deal with both the gui and the client-server connections:
def quit_app(window_root: tk.Tk, server_socket: socket.socket)-> None:
    server_socket.close()
    window_root.quit()

def main():

    server_socket = connect_to_server()


    root = tk.Tk()
    root.title("Eyasu Drive 1.0")
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.configure(bg=BACKGROUND_COLOR)
    root.resizable(False, False)

    files_list_frame = tk.Frame(root, bg = BACKGROUND_COLOR2,height= FILES_LIST_HEIGHT, width = FILES_LIST_WIDTH)
    files_list_frame.pack(padx = 10, pady = 10, side = tk.LEFT)

    main_files_list_frame = tk.Frame(files_list_frame, width = FILES_LIST_WIDTH, height = FILES_LIST_HEIGHT)

    actions_list_frame = tk.Frame(root, bg = BACKGROUND_COLOR,height= ACTIONS_LIST_HEIGHT, width = ACTIONS_LIST_WIDTH)
    actions_list_frame.pack(padx = 10, pady = 10, side = tk.LEFT)
    actions_list_frame.pack_forget()
    actions_list_frame.pack(padx = 10, pady = 10, side = tk.LEFT)

    get_files_list_btn = tk.Button(actions_list_frame, text = "Update files list", fg = TEXT_COLOR, font = FONT,
                                   bg=BUTTON_COLORS["update_file_list"], width = ACTIONS_LIST_WIDTH - 30
                                   , borderwidth=0, command = lambda : update_files_list(main_files_list_frame, server_socket))
    get_files_list_btn.pack(padx = 15, pady = 20, side=tk.TOP)

    upload_file_btn = tk.Button(actions_list_frame, text = "Upload a file", fg = TEXT_COLOR, font = FONT,
                                   bg=BUTTON_COLORS["upload"], width = ACTIONS_LIST_WIDTH - 30
                                   , borderwidth=0, command = lambda: upload_file_dialog(server_socket))
    upload_file_btn.pack(padx = 15, pady = 20, side=tk.TOP)

    quit_btn = tk.Button(actions_list_frame, text = "Quit", fg = TEXT_COLOR, font = FONT,
                                   bg=BUTTON_COLORS["quit"], width = 450, borderwidth=0, command = lambda: quit_app(root, server_socket))
    quit_btn.pack(padx = 15, pady = 20, side=tk.TOP)



    root.mainloop()

if __name__ == '__main__':
    main()


