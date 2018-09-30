import socket
from threading import Thread
import time
import os
import hashlib
import random
import sys

threads = []
base = 1
base = int(base)
hiack = -1
hiack = int(hiack)
nextsegnum = 1
nextsegnum = int(base)
lastackedtime = -1
lastackedtime = float(lastackedtime)
stime = 0
stime = int(stime)
numofpacket = input("Number of packets: ")
# numofpacket=100
numofpacket = int(numofpacket)
windowsize = input("Size of window: ")
# windowsize=10
windowsize = int(windowsize)
timeouttime = input("Time for timeout: ")
# timeouttime=4
timeouttime = float(timeouttime)


def check_sum(data):
    hash_md5 = hashlib.md5()
    hash_md5.update(data)
    return hash_md5.hexdigest()



class ACKRecievingThread(Thread):
    def __init__(self, name , ip, port, sock):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        self.logfile = ''
        self.name = name
        self.kill_received = False

    def run(self):
        while not self.kill_received:
            global base
            global nextsegnum
            global numofpacket
            global stime
            fname="serverAcklog.txt"
            self.logfile=open(os.curdir + "/" + fname, "w+")

            while nextsegnum <= numofpacket+1 :
                conn, addr = self.sock.accept()
                ackpk = conn.recv(1024)
                conn.close()
                ackpk = ackpk.split(':')
                acknum = int(ackpk[1])
                print "ACK Num recieved:"+' '+ackpk[1]
                self.logfile.write(time.ctime(time.time()) + "\t" + "Packet Number "+
                        str(ackpk[1]) + " has been acknowledged.\n")
                self.logfile.flush()

                if base <= acknum+1:
                    base = acknum+1
                if base == nextsegnum:
                    stime = 0


class SenderThread(Thread):
    def __init__(self,name, ip, port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.name = name
        self.kill_received = False
    # def __init__(self, name):
    #     Thread.__init__(self)



    def make_pkt(self, num):
        int size = random.randint(512,2024)
        #pkt = ("SeqNum:"+num + ":size")
        pkt = ("SeqNum:"+num )
        return pkt

    def run(self):
        while not self.kill_received:
            print ("Sender is up and running")
            global nextsegnum
            global base
            global windowsize
            global lastackedtime
            global stime
            fname="serverSentlog.txt"
            self.logfile=open(os.curdir + "/" + fname, "w+")

            while base <= numofpacket+1:
                    # print nextsegnum
                    # print base+windowsize
                if nextsegnum < base+windowsize and nextsegnum <= numofpacket:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((self.ip, self.port))
                    temp = str(nextsegnum)
                    data = self.make_pkt(temp)
                    print (nextsegnum)
                    print ("Sending"+' '+str(nextsegnum))
                    self.logfile.write(time.ctime(time.time()) + "\t" + "Packet Number "+
                        str(nextsegnum) + " has been sent.\n")
                    self.logfile.flush()
                    s.sendall(data)
                    if base == nextsegnum:
                        lastackedtime = time.time()
                        stime = 1
                    nextsegnum = nextsegnum+1
                    s.close()
            quit()


class TimerThread(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name
        self.kill_received = False

    def run(self):
        while not self.kill_received:
            global stime
            global base
            global nextsegnum
            
            # print str(time.time())+' '+str(lastackedtime)+' '+str(stime)
            # print time.time()-lastackedtime
            if time.time()-lastackedtime > timeouttime and stime == 1:
                print ("TimeOut")
                nextsegnum = base
                stime = 0


def has_live_threads(threads):
    return True in [t.isAlive() for t in threads]

# def parse_options():
#     parser = OptionParser()
#     parser.add_option("-t", action="store", type="int", dest="threadNum", default=1,
#                       help="thread count [1]")
#     (options, args) = parser.parse_args()
#     return options

# options = parse_options()  

ACKSIP = 'localhost'
ACKPORT = 9001
SenderIP = 'localhost'
SenderPORT = 10001

# Binding Port for ACKReciever
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((ACKSIP, ACKPORT))
sock.listen(5)
ackr = ACKRecievingThread("thread# 1",ACKSIP, ACKPORT, sock)
ackr.daemon = True
ackr.start()
threads.append(ackr)
#time.sleep(1)

# Starting SenderThread
timer = TimerThread("thread# 2")
timer.daemon = True
timer.start()
threads.append(timer)
sender = SenderThread("thread# 3",SenderIP, SenderPORT)
sender.daemon = True
sender.start()
threads.append(sender)




while has_live_threads(threads):
    try:
        # synchronization timeout of threads kill
        [t.join() for t in threads
            if t is not None and t.isAlive()]
    except KeyboardInterrupt:
        # Ctrl-C handling and send kill to threads
        print "Sending kill to threads..."
        for t in threads:
            t.kill_received = True
# for t in threads:
#     t.join()

print "Code Finished."
sock.close()