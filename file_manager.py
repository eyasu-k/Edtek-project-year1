import os

#this module deals with all file modifications the server requires.

def create_new_folder(folder_path: str)-> None:
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)

def file_exists(filepath: str)-> bool:
    return os.path.exists(filepath)

def get_file(filepath: str)-> bytes:
    with open(filepath, 'rb') as file:
        return file.read()

def create_file(filename: str, file_contents: bytes)-> False:
    if os.path.exists(filename):
        return False
    with open(filename, 'wb') as new_file:
        new_file.write(file_contents)
    
def get_files_list(folder_path: str)-> list[str]:
    files = os.listdir(folder_path)
    return files

def delete_file(filename: str)-> bool:
    if os.path.exists(filename):
        os.remove(filename)
        return True
    return False

def get_file_size(filename: str)-> int:
    return os.path.getsize(filename)

def get_downloads_path():
    return os.path.join(os.path.expanduser('~'), "Downloads")

def get_file_name(file_path: str)-> str:
    return os.path.basename(file_path)

def get_file_types(file_name: str)-> tuple[tuple[str,str], tuple[str,str]]:
    all_files = ("All files", '*.*')
    if '.' not in file_name:
        return all_files, all_files
    else:
        file_name_extension = file_name.split('.')[-1]
        file_type = file_name_extension.upper() + " File"
        return (file_type, "*."+file_name_extension), all_files

def format_file_name(file_name: str, max_len: int)-> str:
    if len(file_name) <= max_len:
        return file_name
    file_type = ''
    if '.' in file_name:
        file_type = '.'+file_name.split('.')[-1]
    file_type_length = len(file_type)
    file_name_prefix = '...'
    new_file_length = max_len - len(file_name_prefix) - file_type_length
    formatted_file_name = file_name[:new_file_length]+file_name_prefix+file_type
    return formatted_file_name

def format_file_size(file_size: int)-> str:
    if file_size <= 1_000:
        return str(file_size) + "Bytes"
    if 1_000 <= file_size < 1_000_000:
        return str(round(file_size/1_024, 2)) + "Kb"
    if 1_000_000 <= file_size < 1_000_000_00:
        return str(round(file_size/1_048_576, 2)) + "Mb"
    return str(file_size)


