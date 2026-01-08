#this file contains the declaration constant variables used by the client and the server.

#commands:
SUCCESS, ACK, R_UPLOAD,R_DOWNLOAD, R_LIST, ERROR= "success", "ack", "r_upload","r_download", "r_list", "error"
UPLOAD, DOWNLOAD, LIST, DELETE = "upload", "download", "list", "delete"
CLIENT_COMMANDS = (UPLOAD, DOWNLOAD, LIST, DELETE)
RESPONSES = (SUCCESS, R_DOWNLOAD, R_LIST, ERROR)

#error codes:
INVALID_COMMAND, FILE_EXISTS, FILE_NOT_FOUND = 0, 1, 2


DELIMITER = ':'
FILE_ATTRIBUTE_DELIMITER = ';'
FILES_DELIMITER = ','
DEFAULT_BUFFER_SIZE = 1024
EXTRA_BUFFER_SIZE = 500
MAXIMUM_FILE_SIZE = 16_777_216 #the maximum file size allowed is 16Mb (like said in the instructions)

SERVER_FILES_FOLDER_NAME = "server_files"
