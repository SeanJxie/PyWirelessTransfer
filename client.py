import socket
import os

import protocol_consts

class SendingClient:
    def __init__(self, host_ip: str, srcdir: str) -> None:
        self.HOST = host_ip
        self.SRC  = srcdir

        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self) -> None:
        self._client_socket.connect((self.HOST, protocol_consts.PORT))
        print("Connected to receiver.")

    def handshake(self) -> bool:
        self._send_confirm()
        is_confirm = self._receive_confirm()
        if is_confirm:
            print("Connection has been accepted by receiver.")
        else:
            print("Connection has been rejected by receiver.")

        return is_confirm

    def _count_files(self) -> int:
        return sum(len(f) for (_, _, f) in os.walk(self.SRC))

    def _transfer_file(self, path: str) -> bool:
        print(f"Transferring file: {path}")

        # We want to transfer the path of the file with self.SRC prefix removed.
        nosrcprefix = os.path.relpath(path, self.SRC)
        pathlen = len(nosrcprefix)

        self._send_as_bytes(pathlen)
        if not self._receive_confirm():
            print("    Path length data has been rejected by receiver.")
            return False

        print("    Path length data has been accepted by receiver.")
        self._send(bytearray(map(ord, nosrcprefix)))

        if not self._receive_confirm():
            print("    Path data has been rejected by receiver.")
            return False

        print("    Path data has been accepted by receiver.")

        filesize = os.path.getsize(path)
        self._send_as_bytes(filesize)

        if not self._receive_confirm():
            print("    File size data has been rejected by receiver.")

        print("    File size data has been accepted by receiver.")
        with open(path, "rb") as payload:
            self._send(payload.read())

        if not self._receive_confirm():
            print("    File data has been rejected by receiver.")
            return False

        print("    File data has been accepted by receiver.")
        print("File transfer complete.\n")
        return True

    def _receive_confirm(self) -> bool:
        response = self._client_socket.recv(protocol_consts.BYTESIZE_MSG)
        return response == protocol_consts.MSG_SERVER_CONF

    def _send_confirm(self) -> None:
        self._send(protocol_consts.MSG_CLIENT_CONF)

    def _send(self, bytes_data: bytes) -> None:
        self._client_socket.sendall(bytes_data)

    def _send_as_bytes(self, data: int) -> None:
        bytes_data = data.to_bytes(protocol_consts.BYTESIZE_FILESIZE, "big")
        self._send(bytes_data)

    def transfer_dir(self) -> bool:
        files_count = self._count_files()
        print(files_count, "files to be transfered in total.")

        self._send_as_bytes(files_count)
        if not self._receive_confirm():
            print("File quantity data has been rejected by receiver.")
            return False

        print("File quantity data has been accepted by receiver.")
        for root, _, files_names in os.walk(self.SRC):
            for filename in files_names:
                fullpath = os.path.join(root, filename)
                if not self._transfer_file(fullpath):
                    print("An error has occurred.")
                    return False

        return True
