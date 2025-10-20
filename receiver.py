import sys
from socket import *
import threading
import time
import queue
import pickle
import random

def sendAck( ackNo, sock, end ):
    rand = random.randint(0,9)
    if rand > 1:
        toSend = (ackNo,)
        msg = pickle.dumps( toSend)
        sock.sendto( msg, end)

def rx_thread( s, sender, que, bSize):
    nSeq = 1 
    
    while True:
        try:
            buf, addr = s.recvfrom(bSize + 20)
            block = pickle.loads(buf)
            blockNo = block[0]
            data = block[1] 
            
            print(f"Received block {blockNo}, expecting {nSeq}")
            
            if blockNo == nSeq:
                que.put(data)
                sendAck(nSeq, s, sender)  
                nSeq += 1 
                print(f"ACK sent for block {nSeq-1}, now expecting {nSeq}")
            else:
                print(f"Out-of-order block {blockNo} received, sending ACK for {nSeq-1}")
                sendAck(nSeq - 1, s, sender)
            
        except Exception as e:
            print(f"Error in rx_thread: {e}")
            continue
    
def receiveNextBlock( q ):
    return q.get()

def main(sIP, sPort, fNameRemote, fNameLocal, blockSize):

    s = socket( AF_INET, SOCK_DGRAM)
    request = (fNameRemote, blockSize)
    req = pickle.dumps(request)
    sender = (sIP, sPort)
    print("sending request")
    s.sendto( req, sender)
    print("waiting for reply")
    rep, ad = s.recvfrom(128)
    reply = pickle.loads(rep)
    print(f"Received reply: code = {reply[0]} fileSize = {reply[1]}")
    if reply[0]!=0:
        print(f'file {fNameRemote} does not exist in sender')
        sys.exit(1)
    fileSize = reply[1]
    q = queue.Queue( )
    tid = threading.Thread( target=rx_thread, args=(s, sender, q, blockSize))
    tid.start()
    f = open( fNameLocal, 'wb')
    noBytesRcv = 0
    while noBytesRcv < fileSize:
        print(f'Going to receive; noByteRcv={noBytesRcv}')
        b = receiveNextBlock( q )
        sizeOfBlockReceived = len(b)
        if sizeOfBlockReceived > 0:
            f.write(b)
            noBytesRcv += sizeOfBlockReceived

    f.close()
    tid.join()
       

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python receiver.py senderIP senderPort fileNameRemote fileNameLocal blockSize")
        sys.exit(1)
    senderIP = sys.argv[1]
    senderPort = int(sys.argv[2])
    fileNameRemote = sys.argv[3]
    fileNameLocal = sys.argv[4]
    blockSize = int(sys.argv[5])
    random.seed( 7 )
    main( senderIP, senderPort, fileNameRemote, fileNameLocal, blockSize)
    
