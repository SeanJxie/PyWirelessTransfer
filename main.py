import server, client

def main() -> None:
    mode = input("Would you like this mpachine to be the file sender or receiver? (s/r): ").lower()
    while mode not in ('s', 'r'):
        print("Invalid input. Please try again.")
        mode = input("Would you like this machine to be the file sender or receiver? (s/r): ").lower()

    if mode == 'r':
        print("This machine will be receiving the files.")
        ftserver = server.ReceivingServer(
            input("Enter the path of the directory you would like to transfer your files TO: ")
        )

        ftserver.listen_and_connect_to_client()
        ftserver.handshake()
        ftserver.receive_dir()
        del ftserver

        

    elif mode == 's':
        print("This machine will be sending the files.")
        ftclient = client.SendingClient(
            input("Enter the local IP provided to you by the receiver machine: "), 
            input("Enter the path of the directory you would like to transfer your files FROM: ")
        )

        ftclient.connect_to_server()
        ftclient.handshake()
        ftclient.transfer_dir()
        del ftclient

    print("Transfer complete. You may now exit the program.")
    while 1:
        pass

if __name__ == "__main__":
    main()