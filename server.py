from __future__ import annotations
import os
import socket

class Server:
    def __init__(self, dstdir: str) -> None:
        self.HOST = socket.gethostbyname(socket.gethostname())
        print("In order for the sender machine to locate this machine in the local network, the following internal IP will be needed:", self.HOST)
        self.PORT = 1024       

        self.MSGBYTESIZE  = 3
        self.CLIENTCONF   = b"\x77\x66\x74" # wft
        self.SERVERCONF   = b"\x77\x66\x74" # wft
        self.REJECT       = b"\x00\x00\x00" # 000
        self.FILEINFOCONF = b"\x72\x63\x66" # rcf
        self.DIRINFOCONF  = b"\x72\x63\x64" # rcd

        self.DIRINFOSIZE      = 64
        self.FILESIZEINFOSIZE = 64
        self.FILENAMEINFOSIZE = 1024 * 4

        self.dstdir = dstdir
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind((self.HOST, self.PORT))
        self.client_socket = self._listen_and_connect_to_client()

    def _listen_and_connect_to_client(self) -> socket | int:
        self.listener.listen()
        client_socket, addr = self.listener.accept()

        print(f"Accepted connection from: {addr}")
        print("Confirming connection...")

        if client_socket.recv(self.MSGBYTESIZE) == self.CLIENTCONF:
            client_socket.send(self.SERVERCONF)
            print("Connection confirmed.\n")
            return client_socket
        else:
            client_socket.send(self.REJECT)
            print("Connection could not be confirmed.\n")
            return 0

    def _recieve_file(self, dst: str) -> None:
        print("    Recieving file data...")

        filesizeinfo = self.client_socket.recv(self.FILESIZEINFOSIZE)
        filesize = int.from_bytes(filesizeinfo, byteorder="big")

        filenameinfo = self.client_socket.recv(self.FILENAMEINFOSIZE)
        try:
            filename = filenameinfo.decode()
        except UnicodeDecodeError as e:
            print("Could not decode file name:", e)

        self.client_socket.send(self.FILEINFOCONF)

        print("        File size:", filesize)
        print("        File name:", filename)

        try:
            os.makedirs(os.path.dirname(os.path.join(self.dstdir, filename)), exist_ok=True)
            with open(os.path.join(dst, filename), "wb") as rf:
                rf.write(self.client_socket.recv(filesize))
        except Exception as e: 
            print("Could not write file:", e)

        print("    File received successfully.")
    
    def _recieve_dir(self, dst: str) -> None:
        print("Receiving directory data...")
        dirinfo = self.client_socket.recv(self.DIRINFOSIZE)
        nfiles = int.from_bytes(dirinfo, byteorder="big")
        self.client_socket.send(self.DIRINFOCONF)
        print("There are", nfiles, "files to be transfered.")
        print("Receiving files...")
        for _ in range(nfiles):
            self._recieve_file(dst)

        print("Directory received successfully.")

    def run(self) -> None:
        if self.client_socket:
            self._recieve_dir(self.dstdir)

        self.client_socket.close()

    def __del__(self) -> None:
        self.listener.close()
