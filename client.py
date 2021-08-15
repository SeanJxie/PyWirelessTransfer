from posixpath import basename
import socket
import os


class Client:
    def __init__(self, host_server_ip: str, srcdir: str) -> None:
        self.SERVERHOST = host_server_ip
        self.PORT = 1024

        self.MSGBYTESIZE = 3
        self.CLIENTCONF = b"\x77\x66\x74"  # wft
        self.SERVERCONF = b"\x77\x66\x74"  # wft
        self.REJECT = b"\x00\x00\x00"  # 000
        self.FILEINFOCONF = b"\x72\x63\x66"  # rcf
        self.DIRINFOCONF = b"\x72\x63\x64"  # rcd

        self.DIRINFOSIZE = 64
        self.FILESIZEINFOSIZE = 64
        self.FILENAMEINFOSIZE = 1024 * 4

        self.srcdir = srcdir
        self.connector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _connect_to_server(self) -> int:
        self.connector.connect((self.SERVERHOST, self.PORT))
        # Handshake
        self.connector.send(self.CLIENTCONF)
        response = self.connector.recv(self.MSGBYTESIZE)
        if response == self.SERVERCONF:
            print("Connected to destination machine.")
            return 1
        elif response == self.REJECT:
            print("Server has refused connection.")
            return 0

    def _send_file(self, filepath: str) -> None:
        print("        Sending file:", filepath)
        fsize = os.path.getsize(filepath)
        self.connector.send(
            fsize.to_bytes(self.FILESIZEINFOSIZE, byteorder="big")
        )

        strpayload = bytearray(
            map(ord, filepath.replace(self.srcdir, "")[1:])
        )
        self.connector.send(strpayload)

        response = self.connector.recv(self.MSGBYTESIZE)

        if response == self.FILEINFOCONF:
            print("            File info send success.")
            print("            Sending file data...")
            with open(filepath, "rb") as payload:
                self.connector.send(payload.read())
            print("            File data send success.")

        elif response == self.REJECT:
            print("Server has ended communication.")
        else:
            print("Server isn't following protocol.")

        print("        File transfer success.")

    def _send_dir(self, dirpath: str) -> None:
        print("Transfering directory contents...")

        nfiles = 0
        for _, _, fnames in os.walk(dirpath):
            nfiles += len(fnames)

        print("    Sending directory info...")
        self.connector.send(nfiles.to_bytes(self.DIRINFOSIZE, byteorder="big"))

        response = self.connector.recv(self.MSGBYTESIZE)
        if response == self.DIRINFOCONF:
            print("    Directory info send success.")
            print("    Sending files...")

            for root, _, fnames in os.walk(dirpath):
                for fname in fnames:
                    fullpath = os.path.join(root, fname)
                    self._send_file(fullpath)

        elif response == self.REJECT:
            print("Server has ended communication.")
        else:
            print("Server isn't following the specified protocol.")

        print("Directory transfer success.")

    def run(self) -> None:
        if self._connect_to_server():
            self._send_dir(self.srcdir)

    def __del__(self) -> None:
        self.connector.close()
