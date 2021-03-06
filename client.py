import socket
import sys
import threading
import os
import time
import json
import pickle
import random
import uuid
from utility import message as m
from datetime import datetime

servers = []

configData = None
clientSock = None
clientPID = None
lock = threading.Lock()

hintedLeader = None
receiveACK = False

sendDelay = 3
timeoutDelay = 18
leaderDelay = 10


def doExit():
    global servers
    global clientSock

    sys.stdout.flush()
    clientSock.close()
    for sock in servers:
        sock[0].close()
    os._exit(1)


def userInput():
    while True:
        x = input()

        commandList = x.split(" ", 2)
        command = commandList[0].strip()
        if(command == 'connect'):
            threading.Thread(target=connectToServers).start()
        elif(command == 'sendall'):
            test = "testing from client " + str(clientPID)
            send = m(test, clientPID).getReadyToSend()
            for sock in servers:
                sock[0].sendall(send)
        elif(command == 'send'):
            pid = commandList[1]
            msg = commandList[2].split(" ")
            uniqueID = str(uuid.uuid4().hex)
            send = m(msg[0], clientPID, uniqueID)
            send.operation = commandList[2]
            send = send.getReadyToSend()
            time.sleep(sendDelay)
            for sock in servers:
                if(sock[1] == str(pid)):
                    sock[0].sendall(send)
        elif(command == 'sendleader' or command == 'sendLeader'):
            # example: sendleader 1
            pid = commandList[1]
            time.sleep(sendDelay)
            message = m("leader", clientPID).getReadyToSend()
            for sock in servers:
                if(sock[1] == str(pid)):
                    sock[0].sendall(message)
        elif(command == 'hintedLeader' or command == 'hintedleader'):
            print("Current Leader:", hintedLeader)
        elif(command == 'exit' or command == 'failProcess'):
            doExit()
        elif(command == 'put' or command == 'get'):
            uniqueID = str(uuid.uuid4().hex)
            msg = m(command, clientPID, uniqueID)
            msg.operation = x

            threading.Thread(target=onPutOrGetCommand,
                             args=(msg, [hintedLeader])).start()


def onPutOrGetCommand(msg, serversTried):
    global hintedLeader
    global receiveACK
    receiveACK = False
    time.sleep(sendDelay)
    if(hintedLeader == None):
        selectedServer = str(random.randint(1, 5))
        for sock in servers:
            if sock[1] == selectedServer:
                sock[0].sendall(msg.getReadyToSend())
    else:
        for sock in servers:
            if sock[1] == hintedLeader:
                try:
                    sock[0].sendall(msg.getReadyToSend())
                except socket.error:
                    sock[0].close()
    time.sleep(timeoutDelay)
    print("receivedACK:", receiveACK)
    if not receiveACK:
        for sock in servers:
            if sock[1] not in serversTried and hintedLeader not in serversTried:
                serversTried.append(sock[1])
                hintedLeader = sock[1]
                leaderMsg = m("leader", clientPID).getReadyToSend()
                sock[0].sendall(leaderMsg)
                time.sleep(leaderDelay)
                threading.Thread(target=onPutOrGetCommand,
                                 args=(msg, serversTried)).start()
                break
    else:
        receiveACK = False


def onNewServerConnection(serverSocket, addr):
    global hintedLeader
    global receiveACK
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print(f'{datetime.now().strftime("%H:%M:%S")} connection from', addr)
    while True:
        try:
            msg = serverSocket.recv(2048)
        except socket.error:
            serverSocket.close()
        if not msg:
            serverSocket.close()
        if (msg != b''):
            msg = pickle.loads(msg)
            print(
                f'{datetime.now().strftime("%H:%M:%S")} From {msg.senderPID}:', msg.command)
            if(msg.command == 'hintedLeader'):
                lock.acquire()
                hintedLeader = msg.senderPID
                lock.release()
            if(msg.command == "info"):
                print("get command result", msg.val)
            if (msg.command == "ack"):
                receiveACK = True


def watch():
    global clientSock
    global servers
    clientSock = socket.socket()
    clientSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    clientSock.bind((socket.gethostname(), configData[sys.argv[1]]))
    clientSock.listen(32)
    while True:
        c, addr = clientSock.accept()
        threading.Thread(target=onNewServerConnection,
                         args=(c, addr)).start()


def connectToServers():
    print("connecting to servers")
    # connect to servers here, afterwards set up bind
    # put connections in array
    for i in range(1, 6):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((socket.gethostname(), configData[str(i)]))
        msg = 'client ' + str(clientPID)
        sock.sendall(msg.encode())
        servers.append([sock, str(i)])


def main():
    global configData
    global clientSock
    global clientPID

    f = open('config.json')
    configData = json.load(f)
    f.close()

    clientPID = sys.argv[1]

    try:
        threading.Thread(target=userInput).start()
        # threading.Thread(target=connectToServers).start()

        threading.Thread(target=watch).start()
    except Exception as error:
        print(error, flush=True)
    while True:
        try:
            pass
        except KeyboardInterrupt:
            doExit()


if __name__ == "__main__":
    main()
