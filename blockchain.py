import pickle
import hashlib
import os.path
import string
import random

# blockchain class roots


class blockchain:
    def __init__(self, fname):
        self.blockchain = []
        self.fname = fname
        self.readFromFile()

    # input: operation as a string
    # adds operation block to blockchain
    def add(self, op):
        operation = str(op)
        hash = None
        nonce = None
        # calculate hash
        if(len(self.blockchain) == 0):
            hash = ""
        else:
            lastBlock = self.blockchain[-1]
            hash = str(lastBlock[0]) + str(lastBlock[1]) + str(lastBlock[2])
            hash = hashlib.sha256(hash.encode()).hexdigest()

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
        block = (operation, nonce, hash)
        self.blockchain.append(block)

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

    def print(self):
        for i in self.blockchain:
            print(i)