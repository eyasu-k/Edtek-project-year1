import os

#this module deals with all file modifications the server requires.

def file_exists(filepath: str)-> bool:
    return os.path.exists(filepath)

def get_file(filepath: str)-> str:
    with open(filepath, 'rb') as file:
        return file.read().decode()

def create_file(filename: str, file_contents: str)-> False:
    if os.path.exists(filename):
        return False
    with open(filename, 'wb') as new_file:
        new_file.write(file_contents.encode())
    
def get_files_list(folder_path: str)-> list[str]:
    files = os.listdir(folder_path)
    return files

def delete_file(filename: str)-> bool:
    if os.path.exists(filename):
        os.remove(filename)
        return True
    return False
