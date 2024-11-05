import socket
import subprocess
import os

# HOW TO RUN
# python server.py 1234
# 1234 is the port number

# The port on which to listen
listenPort = 1234

# Create a welcome socket
welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
welcomeSock.bind(('', listenPort))

# Start listening on the socket
welcomeSock.listen(1)

# ************************************************
# Receives the specified number of bytes
# from the specified socket
# @param sock - the socket from which to receive
# @param numBytes - the number of bytes to receive
# @return - the bytes received
# *************************************************
def recvAll(sock, numBytes):
    
    # The buffer
    recvBuff = b""
    
    # The temporary buffer
    tmpBuff = b""
    
    # Keep receiving till all is received
    while len(recvBuff) < numBytes:
        
        # Attempt to receive bytes
        tmpBuff = sock.recv(numBytes - len(recvBuff))
        
        # The other side has closed the socket
        if not tmpBuff:
            break
        
        # Add the received bytes to the buffer
        recvBuff += tmpBuff
        
    return recvBuff

# Function to handle client requests
def handleClient(clientSock):
    command = clientSock.recv(1024).decode()
    
    if not command:
            print("Client disconnected")
            return False  

    if command == "quit":
        return False  

    # looking up current directory commands are different depending
    # on operating systems, I'm writing on windows so dir is needed
    elif command == "ls":
        if os.name == 'nt':
            lsOutput = subprocess.getoutput('dir')
        else:
            import commands  
            lsOutput = commands.getoutput('ls -l')
        clientSock.sendall(lsOutput.encode())

    elif command.startswith("get"):
        fileName = command.split()[1]

        # Open the file and get the size
        # Send the size then the data to the client
        try:
            with open(fileName, 'rb') as file:
                fileSize = os.path.getsize(fileName)
                clientSock.sendall(str(fileSize).encode())
                print("File size sent:", fileSize)
                while True:
                    data = file.read(1024)
                    if not data:
                        break
                    clientSock.sendall(data)
                print("File contents sent.")
        except FileNotFoundError:
            clientSock.sendall("File not found".encode())
        finally:
            file.close()

    # Handle PUT command
    elif command.startswith("put"):
        fileName = command.split()[1]

        # Receive the first 10 bytes and the file size
        fileSizeBuff = recvAll(clientSock, 10)
        fileSize = int(fileSizeBuff)

        print("The file size is ", fileSize)

        # Receive the file data
        fileData = recvAll(clientSock, fileSize)

        print("The file data is: ")
        print(fileData.decode('latin-1'))

        # Write received data to file
        with open(fileName, 'wb') as file:
            file.write(fileData)

        clientSock.sendall("SERVER: File received".encode())

    return True

# Accept connections forever
while True:
    print("Waiting for connections...")
    
    # Accept connections
    clientSock, addr = welcomeSock.accept()
    
    print("Accepted connection from client:", addr)
    
    sessionActive = True
    while sessionActive:
        sessionActive = handleClient(clientSock)
    
    # Close our side
    clientSock.close()
    break
