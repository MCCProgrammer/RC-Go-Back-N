import sys
import os
from socket import *
import threading
import time
import queue
import pickle
import random
import select

blocksInWindow = 0
window = []

def sendDatagram( blockNo, contents, sock, end ):
    rand = random.randint(0,9)
    if rand > 1:
        toSend = (blockNo, contents)
        msg = pickle.dumps( toSend)
        sock.sendto( msg, end)
        
def waitForAck( s, seg ):
    rx, tx, er = select.select( [s], [],[], seg)
    return rx!=[]


def tx_thread( s, receiver, windowSize, cond, timeout ):
    global blocksInWindow, window
    
    expectedAck = 1
    lastAckTime = time.time()
    
    while True:
        currentTime = time.time()
        if currentTime - lastAckTime > timeout and len(window) > 0:
            print(f"Timeout: Resending {len(window)} blocks in window")
            for block in window:
                sendDatagram(block[0], block[1], s, receiver)
            lastAckTime = currentTime
        
        a = waitAndRecvAck(s, 0.1) 
        
        if a is not None and a >= expectedAck:
            print(f"Received ACK {a}, expected {expectedAck}")
            
            with cond:
                newWindow = []
                for block in window:
                    if block[0] > a:
                        newWindow.append(block)
                window = newWindow
                blocksInWindow = len(window)
                
                cond.notify()
            
            expectedAck = a + 1
            lastAckTime = currentTime
            print(f"Updated expected ACK to {expectedAck}, window size: {blocksInWindow}")
        

        with cond:
            if len(window) == 0 and blocksInWindow == 0:
                print("tx_thread: All blocks sent and acknowledged, terminating")
                break
    
    print("tx_thread terminating")

def waitAndRecvAck(s, timeout):
    """Wait for an ACK with timeout"""
    try:
        rx, tx, er = select.select([s], [], [], timeout)
        if rx != []:
            buf, addr = s.recvfrom(128)
            ack = pickle.loads(buf)
            return ack[0]
        return None
    except:
        return None
            

def sendBlock( seqNo, fileBytes, s, receiver, windowSize, cond ): 
    global blocksInWindow, window
    
    with cond:
        while blocksInWindow >= windowSize:
            cond.wait()
        
        block = (seqNo, fileBytes)
        window.append(block)
        blocksInWindow = len(window)
        
        sendDatagram(seqNo, fileBytes, s, receiver)
        print(f"Sent block {seqNo}, window size: {blocksInWindow}/{windowSize}")

def main(hostname, senderPort, windowSize, timeOutInSec):
    s = socket( AF_INET, SOCK_DGRAM)
    s.bind((hostname, senderPort))
    # interaction with receiver; no datagram loss
    buf, rem = s.recvfrom( 256 )
    req = pickle.loads( buf)
    fileName = req[0]
    blockSize = req[1]
    result = os.path.exists(fileName)
    if not result:
        print(f'file {fileName} does not exist in server')
        reply = ( -1, 0 )
        rep=pickle.dumps(reply)
        s.sendto( rep, rem )
        sys.exit(1)
    fileSize = os.path.getsize(fileName)
    reply = ( 0, fileSize)
    rep=pickle.dumps(reply)
    s.sendto( rep, rem )
    # file transfer; datagram loss possible
    windowCond = threading.Condition()
    tid = threading.Thread( target=tx_thread,
                            args=(s,rem,windowSize, windowCond,timeOutInSec))
    tid.start()
    f = open( fileName, 'rb')
    blockNo = 1
    
    while True:
        b = f.read( blockSize  )
        sizeOfBlockRead = len(b)
        if sizeOfBlockRead > 0:
            sendBlock( blockNo, b, s, rem, windowSize, windowCond)
        if sizeOfBlockRead == blockSize:
            blockNo=blockNo+1
        else:
            break
    f.close()
    tid.join()


if __name__ == "__main__":
    # python sender.py senderPort windowSize timeOutInSec
 

    if len(sys.argv) != 4:
        print("Usage: python sender.py senderPort windowSize timeOutInSec")
    else:
        senderPort = int(sys.argv[1])
        windowSize = int(sys.argv[2])
        timeOutInSec = int(sys.argv[3])
        hostname = gethostbyname(gethostname())
        random.seed( 5 )
        main( hostname, senderPort, windowSize, timeOutInSec)
