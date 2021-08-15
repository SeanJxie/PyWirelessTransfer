import server, client

def main() -> None:
    mode = input("Would you like this machine to be the file sender or receiver? (s/r): ").lower()
    while mode not in ('s', 'r'):
        print("Invalid input. Please try again.")
        mode = input("Would you like this machine to be the file sender or receiver? (s/r): ").lower()

    if mode == 'r':
        print("This machine will be receiving the files.")
        ftserver = server.Server(
            input("Enter the path of the directory you would like to transfer your files TO: ")
        )

        ftserver.run()
        del ftserver

    elif mode == 's':
        print("This machine will be sending the files.")
        ftclient = client.Client(
            input("Enter the internal IP provided by the receiver machine: "), 
            input("Enter the path of the directory you would like to transfer your files FROM: ")
        )

        ftclient.run()
        del ftclient

    print("Transfer complete. You may now exit the program.")
    while 1:
        pass

if __name__ == "__main__":
    main()