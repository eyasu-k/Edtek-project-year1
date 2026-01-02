#this file contains the declaration contant variables used by the client and the server.

#commands:
SUCESS, R_DOWNLOAD, R_LIST, ERROR= "success", "r_download", "r_list", "error"
UPLOAD, DOWNLOAD, LIST, DELETE = "upload", "download", "list", "delete"
CLIENT_COMMANDS = (UPLOAD, DOWNLOAD, LIST, DELETE)
RESPONSES = (SUCESS, R_DOWNLOAD, R_LIST, ERROR)

#error codes:
INVALID_COMMAND, FILE_EXISTS, FILE_NOT_FOUND = 0, 1, 2


DELIMITER = ':'
FILE_ATTRIBUTE_DELIMITER = ';'
DEFAULT_BUFFER_SIZE = 1024

SERVER_FILES_FOLDER_NAME = "server_files"
