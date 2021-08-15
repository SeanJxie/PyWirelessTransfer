import socket
import os

import protocol_consts

class ReceivingServer:
    def __init__(self, dstdir: str) -> None:
        self.DST = dstdir

        self.HOST = socket.gethostbyname(socket.gethostname())
        print("In order for the sender machine to locate this machine in the local network, the following local IP will be needed:", self.HOST)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, protocol_consts.PORT))

    def listen_and_connect_to_client(self) -> None:
        self.server_socket.listen()
        self.transfer_socket, client_addr = self.server_socket.accept()

        print("Client has connected with address:", client_addr)

    def handshake(self) -> bool:
        msg = self.transfer_socket.recv(protocol_consts.BYTESIZE_MSG)
        if msg == protocol_consts.MSG_CLIENT_CONF:
            self.transfer_socket.sendall(protocol_consts.MSG_SERVER_CONF)
            print("Connection has been accepted by client.")
            return True
        else:
            return False

    def _receive_file(self) -> None:
        # File path length
        pathlen_bytes = self.transfer_socket.recv(protocol_consts.BYTESIZE_PATH_SIZE)
        pathlen = int.from_bytes(pathlen_bytes, "big")

        self.transfer_socket.sendall(protocol_consts.MSG_SERVER_CONF)

        # File path
        noprefixpathname_bytes = self.transfer_socket.recv(pathlen)
        noprefixpathname = ''.join(map(chr, noprefixpathname_bytes))

        self.transfer_socket.sendall(protocol_consts.MSG_SERVER_CONF)

        # File size
        filesize_bytes = self.transfer_socket.recv(protocol_consts.BYTESIZE_FILESIZE)
        filesize = int.from_bytes(filesize_bytes, "big")

        self.transfer_socket.sendall(protocol_consts.MSG_SERVER_CONF)

        # File data
        filedata_bytes = self.transfer_socket.recv(filesize)

        self.transfer_socket.sendall(protocol_consts.MSG_SERVER_CONF)

        # Write file
        fulldstpath = os.path.join(self.DST, noprefixpathname)
        print("Received file:", fulldstpath)
        os.makedirs(os.path.dirname(fulldstpath), exist_ok=True) # Make the directories needed in order to write the file.
        with open(fulldstpath, "wb") as dstfile:
            dstfile.write(filedata_bytes)

        
    def receive_dir(self) -> None:
        nfiles_bytes = self.transfer_socket.recv(protocol_consts.BYTESIZE_NFILES)
        self.transfer_socket.sendall(protocol_consts.MSG_SERVER_CONF)
        for _ in range(int.from_bytes(nfiles_bytes, "big")):
            self._receive_file()


    def __del__(self) -> None:
        self.transfer_socket.close()
        self.server_socket.close()
