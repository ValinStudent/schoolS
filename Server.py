'''
Script for server
@author: hao
'''

import config
import protocol
import os
import threading
from socket import *
class server(threading.Thread):

    # Constructor: load the server information from config file
    def __init__(self, threadID):
        self.port, self.path=config.config().readServerConfig()

        ##Attempting to try threading
        threading.Thread.__init__(self)
        self.threadID=threadID
    # Get the file names from shared directory
    def getFileList(self):
        return os.listdir(self.path)
    
    # Function to send file list to client       
    def listFile(self, serverSocket):
        serverSocket.send(protocol.prepareFileList(protocol.HEAD_LIST, self.getFileList()))

    # Function to send a file to client       
    def sendFile(self,serverSocket,fileName):
        f = open(fileName,'rb')
        l = f.read(1024) # each time we only send 1024 bytes of data
        while (l):
            serverSocket.send(l)
            l = f.read(1024)

    # Function to send a file to client       
    def receiveFile(self,uploadSocket,fileName):
        if not os.path.exists(self.path+"/"+fileName):
            open(self.path+"/"+fileName, 'x').close()
        with open(self.path+"/"+fileName, 'wb') as f:
            print ('file opened')
            while True:
                #print('receiving data...')
                data = uploadSocket.recv(1024)
                #print('data=%s', (data))
                if not data:
                    break
            # write data to a file
                f.write(data)
        print(fileName+" has been downloaded!")
        uploadSocket.close()

    # A new function to handle connected clients
    # the if statement and data handling was moved from below to here
    def connectedClient(self, connectionSocket, threadID):
        dataRec = connectionSocket.recv(1024)
        header,msg=protocol.decodeMsg(dataRec.decode()) # get client's info, parse it to header and content
        # Main logic of the program, send different content to client according to client's requests
        if(header==protocol.HEAD_REQUEST):
            self.listFile(connectionSocket)
        elif(header==protocol.HEAD_DOWNLOAD):
            self.sendFile(connectionSocket, self.path+"/"+msg)
        elif(header==protocol.HEAD_UPLOAD):
            self.receiveFile(connectionSocket, msg)
        else:
            connectionSocket.send(protocol.prepareMsg(protocol.HEAD_ERROR, "Invalid Message"))
        connectionSocket.close()


    # Main function of server, start the file sharing service
    def start(self):
        serverPort=self.port
        serverSocket=socket(AF_INET,SOCK_STREAM)
        serverSocket.bind(('',serverPort))
        serverSocket.listen(20)
        threads = []
        threadID = 0
        print('The server is ready to receive')
        while True:
            connectionSocket, addr = serverSocket.accept()
            print('Connection from : ', addr)
            # Start a new thread to handle the client
            clientThread = threading.Thread(target=self.connectedClient, args=(connectionSocket,threadID))
            clientThread.start()
            threads.append(clientThread)
            threadID = len(threads)

def main():
    s=server(threadID=0)
    s.start()

if __name__ == "__main__":
    main()
