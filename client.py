import socket
import os
from typing import Tuple

import protocol_consts
import protocol_exceptions

import utils

class SendingClient:
    def __init__(self, host_ip: str, srcdir: str) -> None:
        self._HOST = host_ip
        self._SRC  = srcdir

        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self) -> None:
        self._client_socket.connect((self._HOST, protocol_consts.PORT))
        print("Connected to receiver.")

    def handshake(self) -> None:
        # Send client confirmation.
        self._client_socket.sendall(protocol_consts.MSG_CLIENT_CONF)

        # Receive and evaluate server response.
        response = self._client_socket.recv(protocol_consts.BYTESIZE_MSG)
        if response == protocol_consts.MSG_SERVER_CONF:
            print("Connection has been accepted by receiver.")
        else:
            raise protocol_exceptions.ServerCouldNotConfirmError("The receiver did not confirm the connection.")

    def _count_files(self) -> int:
        # Count all files in the directory tree with os.walk().
        ret = 0
        for _, _, f in os.walk(self._SRC):
            ret += len(f)
        return ret
    
    def _get_path_byte_data(self, path) -> Tuple[bytes, bytes]:
        path_no_src_prefix = os.path.relpath(path, self._SRC)

        return (
            len(path_no_src_prefix).to_bytes(protocol_consts.BYTESIZE_PATHLEN, "big"), 
            bytes(map(ord, path_no_src_prefix))
        )

    def _get_file_byte_data(self, path) -> Tuple[bytes, bytes]:
        filesize = os.path.getsize(path)

        with open(path, "rb") as f:
            return (
                filesize.to_bytes(protocol_consts.BYTESIZE_FILESIZE, "big"),
                f.read()
            )

    def _send_file_copy(self, path) -> None:
        print(f"Sending file: {path}\n")

        # Load byte data into a tuple of 2-tuples in the form (data, description).
        pathlen_bytes,  path_bytes = self._get_path_byte_data(path)
        filesize_bytes, file_bytes = self._get_file_byte_data(path)
        
        payload_desc_map = (
            (pathlen_bytes , "path length data"),
            (path_bytes    , "path data"       ),
            (filesize_bytes, "file size data"  ),
            (file_bytes    , "file data"       )
        )

        # Iterate through each element in payload_desc_map and send its data.
        for i in range(len(payload_desc_map)):
            payload, desc = payload_desc_map[i]

            utils.indent_print(4, f"sending {desc}.")
            self._client_socket.sendall(payload)

            server_response = self._client_socket.recv(protocol_consts.BYTESIZE_MSG)
            if server_response == protocol_consts.MSG_SERVER_CONF: # The data has been accepted.
                utils.indent_print(4, f"{desc} has been accepted by receiver.\n")

            else: # The data has been rejected.
                raise protocol_exceptions.ServerCouldNotConfirmError(f"Receiver did not confirm {desc} reception.")

        print("File transfer complete.\n")

    def send_dir_copy(self) -> None:
        nfiles = self._count_files()
        print(nfiles, "files to be transfered in total.")
        
        # Send the number of files to be recieved.
        self._client_socket.sendall(nfiles.to_bytes(protocol_consts.BYTESIZE_NFILES, "big"))

        # Check server confirmation for file quantity data.
        response = self._client_socket.recv(protocol_consts.BYTESIZE_MSG)
        if response == protocol_consts.MSG_SERVER_CONF:

            print("File quantity data has been accepted by receiver.")

            # Iterate through the directory with os.walk() and send every file.
            for root, _, fnames in os.walk(self._SRC):
                for fname in fnames:
                    fullpath = os.path.join(root, fname)
                    self._send_file_copy(fullpath)

        else:
            raise protocol_exceptions.ServerCouldNotConfirmError("Receiver did not confirm directory file quantity data reception.")


    def __del__(self):
        self._client_socket.close()