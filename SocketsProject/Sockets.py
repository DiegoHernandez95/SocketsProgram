import socket
import os

# HOW TO RUN
# ensure that the server is running on a separate terminal
# then type 
# python Sockets.py localhost 1234
# 
# when using the put command you have to specify the full path of the file
# for example: "put C:\Users\YourUsername\Desktop\file.txt"
#
# when using the get command just enter: "get file.txt"
# it will automatically download it to your desktop
#
# SIDENOTE: any files uploaded to the server will be printed in the server terminal

# Function to send a command 
def sendCommand(command):
    connSock.sendall(command.encode())

# Function to receive a response
def receiveResponse():
    data = connSock.recv(1024)
    if isinstance(data, str):
        return data.decode()
    return data

# Function to handle the PUT command
def putCommand(fileName):
    # Check if the file exists
    if not os.path.exists(fileName):
        print(f"File '{fileName}' not found.")
        return

    try:
        with open(fileName, "rb") as file:
            fileData = file.read()

        # Create header indicating the size of the data
        dataSizeStr = str(len(fileData))
        header = dataSizeStr.zfill(10)

        # Prepend the header to the file data
        fileData = header.encode() + fileData
        
        sendCommand(f"put {os.path.basename(fileName)}")

        # Send file data
        numSent = 0
        while len(fileData) > numSent:
            numSent += connSock.send(fileData[numSent:])

        print(receiveResponse())
        print("Sent ", numSent, " bytes.")  
    except FileNotFoundError:
        print("File not found.")
    finally:
        file.close()


# Function to handle GET command
def getCommand(fileName):
    sendCommand(f"get {fileName}")

    # Receive file size
    fileSize = int(receiveResponse())
    if fileSize < 0:
        print("File not found.")
        return
    
    desktopPath = os.path.join(os.path.expanduser("~"), "Desktop")

    # Receive file data
    receivedData = b''
    while len(receivedData) < fileSize:
        data = connSock.recv(1024)
        if not data:
            break
        receivedData += data

    # Write received data to file
    filePath = os.path.join(desktopPath, fileName)
    with open(filePath, 'wb') as file:
        file.write(receivedData)

    print(f"Received {fileName} - {len(receivedData)} bytes.")
    file.close()

# Server address and port
serverAddr = "localhost"
serverPort = 1234

# Create a TCP socket
connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to port 0
connSock.bind(('',0))

# Retreive the ephemeral port number
print("I chose ephemeral port: ", connSock.getsockname()[1]) 

# Connect to the server 
connSock.connect((serverAddr, serverPort))

print("ftp> ", end='', flush=True)

# Accept user input and send commands to the server
while True:
    userInput = input().strip()

    if userInput == "quit":
        break

    splitInput = userInput.split()
    command = splitInput[0]

    if command == "ls":
        sendCommand("ls")
        response = receiveResponse()
        print(response.decode())

    elif command == "put":
        if len(splitInput) < 2:
            print("Error: missing file name")
        else:
            putCommand(splitInput[1])

    elif command == "get":
        if len(splitInput) < 2:
            print("Error: missing file name")
        else:
            getCommand(splitInput[1])

    else:
        print("Invalid command. Please use ls, put <file>, get <file>, or quit.")
        
    print("ftp> ", end="", flush = True)

# Close the control socket
connSock.close()
