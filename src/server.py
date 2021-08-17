import socket
import os

import protocol_consts
import protocol_exceptions

class ReceivingServer:
    def __init__(self, dstdir: str) -> None:
        self._DST = dstdir

        self._HOST = socket.gethostbyname(socket.gethostname())
        print("In order for the sender machine to locate this machine in the local network, the following local IP will be needed:", self._HOST)

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((self._HOST, protocol_consts.PORT))
        self._transfer_socket = None

    def listen_and_connect_to_client(self) -> None:
        self._server_socket.listen()
        self._transfer_socket, client_addr = self._server_socket.accept()

        print("Sender has connected with address:", client_addr)

    def handshake(self) -> None:
        msg = self._transfer_socket.recv(protocol_consts.BYTESIZE_MSG)
        if msg == protocol_consts.MSG_CLIENT_CONF:
            self._transfer_socket.sendall(protocol_consts.MSG_SERVER_CONF)
            print("Connection has been accepted by sender.")
        else:
            raise protocol_exceptions.ServerCouldNotConfirmError("The receiver did not confirm the connection.")

    def _receive_file(self) -> None:
        # File path length
        pathlen_bytes = self._transfer_socket.recv(protocol_consts.BYTESIZE_PATHLEN)
        pathlen = int.from_bytes(pathlen_bytes, "big")
        self._transfer_socket.sendall(protocol_consts.MSG_SERVER_CONF)

        # File path
        noprefixpathname_bytes = self._transfer_socket.recv(pathlen)
        noprefixpathname = ''.join(map(chr, noprefixpathname_bytes))
        self._transfer_socket.sendall(protocol_consts.MSG_SERVER_CONF)

        # File size
        filesize_bytes = self._transfer_socket.recv(protocol_consts.BYTESIZE_FILESIZE)
        filesize = int.from_bytes(filesize_bytes, "big")
        self._transfer_socket.sendall(protocol_consts.MSG_SERVER_CONF)

        # File data
        filedata_bytes = self._transfer_socket.recv(filesize)
        self._transfer_socket.sendall(protocol_consts.MSG_SERVER_CONF)

        # Construct local path with self._DST prefix.
        fulldstpath = os.path.join(self._DST, noprefixpathname)
        print("Received file:", fulldstpath)

        # Make the directories needed in order to write the file and send it.
        os.makedirs(os.path.dirname(fulldstpath), exist_ok=True)

        with open(fulldstpath, "wb") as dstfile:
            dstfile.write(filedata_bytes)

    def receive_dir(self) -> None:
        nfiles_bytes = self._transfer_socket.recv(protocol_consts.BYTESIZE_NFILES)
        self._transfer_socket.sendall(protocol_consts.MSG_SERVER_CONF)

        for _ in range(int.from_bytes(nfiles_bytes, "big")):
            self._receive_file()

    def __del__(self) -> None:
        self._transfer_socket.close()
        self._server_socket.close()
