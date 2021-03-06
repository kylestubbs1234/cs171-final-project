import pickle
import hashlib
import os.path
import string
import random


class blockchain:
    def __init__(self, fname):
        self.blockchain = []
        self.operationIDs = set()
        self.fname = fname
        self.readFromFile()

    # input: operation as a string
    # adds operation block to blockchain
    def mine(self, op, uid):
        operation = str(op)
        hash = None
        nonce = None

        # calculate hash
        if(len(self.blockchain) == 0):
            hash = ""
        else:
            lastBlock = self.blockchain[-1]
            if lastBlock != None:
                hash = str(lastBlock[0]) + \
                    str(lastBlock[1]) + str(lastBlock[2])
                hash = hashlib.sha256(hash.encode()).hexdigest()
            else:
                hash = ""

        # calculate nonce
        foundNonce = False
        valid = ['0', '1', '2']
        while(not foundNonce):
            letters = string.ascii_lowercase
            randomNonce = ''.join(random.choice(letters) for i in range(10))
            testHash = operation + str(randomNonce)
            testHash = hashlib.sha256(testHash.encode()).hexdigest()
            if(testHash[-1] in valid):
                nonce = randomNonce
                foundNonce = True

        # everything should be strings
        print("**** Generate Block ****")
        print("operation:", operation)
        print("nonnce:", nonce)
        print("hash:", hash)
        print("uid:", uid)
        print("*************************")
        block = (operation, nonce, hash, uid)
        return block

    def add(self, block, index, uid):
        # need to account for if server missed out on an index?
        if(uid not in self.operationIDs):
            self.operationIDs.add(uid)
            emptyData = ("operation", "nonce", "hash")
            while(len(self.blockchain) < index + 1):
                self.blockchain.append(emptyData)

            self.blockchain[index] = block

            self.writeToFile()

    # writes blockchain to file
    def writeToFile(self):
        dbfile = open(self.fname, 'wb')
        pickle.dump(self, dbfile)
        dbfile.close()

    # reads blockchain from file
    def readFromFile(self):
        if os.path.isfile(self.fname):
            bc = open(self.fname, 'rb')
            data = pickle.load(bc)
            self.blockchain = data.blockchain
            bc.close()

    def recreateKV(self):
        tempDict = {}

        for block in self.blockchain:

            blockOP = ""
            if(block):
                blockOP = block[0].split(" ")
            if(blockOP != None and blockOP != "" and blockOP[0] == "put"):
                tempDict[blockOP[1]] = blockOP[2]
        return tempDict

    def print(self):
        for i in self.blockchain:
            print(i)

    def getLength(self):
        return len(self.blockchain)

    def checkUID(self, uid):
        if(uid in self.operationIDs):
            return True
        else:
            return False
