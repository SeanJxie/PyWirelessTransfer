import socket
import os

import protocol_consts

class SendingClient:
    def __init__(self, host_ip: str, srcdir: str) -> None:
        self.HOST = host_ip
        self.SRC  = srcdir

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self) -> None:
        self.client_socket.connect((self.HOST, protocol_consts.PORT))
        print("Connected to server.")

    def handshake(self) -> bool:
        self.client_socket.sendall(protocol_consts.MSG_CLIENT_CONF)
        response = self.client_socket.recv(protocol_consts.BYTESIZE_MSG)
        if response == protocol_consts.MSG_SERVER_CONF:
            print("Connection has been accepted by server.")
            return True
        else:
            print("Connection has been rejected by server.")
            return False

    def _count_files(self) -> int:
        ret = 0
        for _, _, f in os.walk(self.SRC):
            ret += len(f)
        return ret

    def _transfer_file(self, path) -> bool:
        print("Transferring file:", path)

        nosrcprefix = os.path.relpath(path, self.SRC) # We want to transfer the path of the file with self.SRC prefix removed.
        pathlen = len(nosrcprefix)

        self.client_socket.sendall(pathlen.to_bytes(protocol_consts.BYTESIZE_PATH_SIZE, "big"))
        response = self.client_socket.recv(protocol_consts.BYTESIZE_MSG)
        if response == protocol_consts.MSG_SERVER_CONF:
            print("    Path length data has been accepted by server.")
            self.client_socket.sendall(bytearray(map(ord, nosrcprefix)))
        else:
            print("    Path length data has been rejected by server.")
            return False

        response = self.client_socket.recv(protocol_consts.BYTESIZE_MSG)
        if response == protocol_consts.MSG_SERVER_CONF:
            print("    Path data has been accepted by server.")

            filesize = os.path.getsize(path)
            self.client_socket.sendall(filesize.to_bytes(protocol_consts.BYTESIZE_FILESIZE, "big"))

        else:
            print("    Path data has been rejected by server.")
            return False

        response = self.client_socket.recv(protocol_consts.BYTESIZE_MSG)
        if response == protocol_consts.MSG_SERVER_CONF:
            print("    File size data has been accepted by server.")
            with open(path, "rb") as payload:
                self.client_socket.sendall(payload.read())

        else:
            print("    File size data has been rejected by server.")

        response = self.client_socket.recv(protocol_consts.BYTESIZE_MSG)
        if response == protocol_consts.MSG_SERVER_CONF:
            print("    File data has been accepted by server.")
        else:
            print("    File data has been rejected by server.")
            return False

        print("File transfer complete.\n")
        return True

    def transfer_dir(self) -> bool:
        nfiles = self._count_files()
        print(nfiles, "files to be transfered in total.")
        
        self.client_socket.sendall(nfiles.to_bytes(protocol_consts.BYTESIZE_NFILES, "big"))
        response = self.client_socket.recv(protocol_consts.BYTESIZE_MSG)

        if response == protocol_consts.MSG_SERVER_CONF:
            print("File quantity data has been accepted by server.")
            for root, _, fnames in os.walk(self.SRC):
                for fname in fnames:
                    fullpath = os.path.join(root, fname)
                    if not self._transfer_file(fullpath):
                        print("An error has occurred.")
                        return False
            return True
        else:
            print("File quantity data has been rejected by server.")
            return False