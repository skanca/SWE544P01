import socket
import threading
import Queue
import time
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ReadThread (threading.Thread):
    def __init__(self, name,csoc,threadQueue,screenQueue,app):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.nickname = ""
        self.threadQueue = threadQueue
        self.screenQueue = screenQueue #...
        self.app = app

    #incoming parser
    def incoming_parser(self,data):
        print ('INCOMING DATA: ', data)

        if len(data) == 0:
            return "Error!!!"
        if len(data) < 3 and not data[3] == "":
            response = "ERR"
            self.csoc.send(response)
            return "Error"
        if data[0:3] == "HEL":
            inMessage=  'Yeni Kullanici olarak kabul edildiniz'
        elif data[0:3] == "REJ":
            inMessage = 'Kullanici olarak kabul edilMEdiniz'

        elif data[0:3] == "BYE":
            inMessage = 'Cikis'

        elif data[0:3] == "LSA":
            inMessage = 'LSA'

        elif data[0:3] == "TOC":
            inMessage = 'Baglanti testi basarili'

        elif data[0:3] == "SOK":
            inMessage = 'Genel mesaj gonderme basarili'

        elif data[0:3] == "MOK":
            inMessage = 'Ozel mesaj gonderme basarili'

        elif data[0:3] == "MNO":
            inMessage = 'Ozel mesaj hedefi bulunamadi'

        elif data[0:3] == "ERR":
            inMessage = 'Hatali Komut gonderdiniz'

        elif data[0:3] == "ERL":
            inMessage = 'Giris yapilaMAdi; login olmalisiniz'

        else:
            response = "ERR"
            self.csoc.send(response)
            return "Error"
        inMessage = time.strftime("[%H:%M:%S]", time.gmtime()) + inMessage
        print("inMessage = ",inMessage)
        return inMessage


#
    def run(self):
        while True:
            try:
                data = self.csoc.recv(1024)
                self.app.cprint(self.incoming_parser(data))
            except:
                pass
            if data[0:3] == "BYE":
                self.csoc.close()

class WriteThread (threading.Thread):
    def __init__(self,name,csoc, threadQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.threadQueue = threadQueue
    def run(self):
        while True:
            if self.threadQueue.qsize() > 0:
                queue_message = self.threadQueue.get()
                try:
                    print("queue_message= ",str(queue_message))
                    self.csoc.send(queue_message)
                except socket.error:
                    self.csoc.close()
                    break

#
class ClientDialog(QDialog):

    def __init__(self,threadQueue,screenQueue):
        """

        :rtype: object
        """
        self.threadQueue = threadQueue
        self.screenQueue = screenQueue

        #create a Qt application
        self.qt_app = QApplication(sys.argv)

        #call the parent constructor on the current object
        QDialog.__init__(self,None)

        #setup the window
        self.setWindowTitle('IRC Client')
        self.setMinimumSize(500,200)
        self.resize(640,480)

        #add a vertical layout
        self.vbox = QVBoxLayout()
        self.vbox.setGeometry(QRect(10,10,621,461))

        #add a horizontal layout
        self.hbox = QHBoxLayout()

        #the sender textbox
        self.sendMessage = QLineEdit("",self)


        #the channel region
        self.messageArea = QTextBrowser()
        self.messageArea.setMinimumSize(QSize(480,0))

        #the send button
        self.send_button = QPushButton('&Send')

        #the users' section
        self.userList = QListView()

        #connect the Go button to its callback
        self.send_button.connect(self.send_button,SIGNAL('clicked()'),self.outgoing_parser)

        #add the controls to the vertical layout
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.sendMessage)
        self.vbox.addWidget(self.send_button)
        self.hbox.addWidget(self.messageArea)

        self.hbox.addWidget(self.userList)

        #start timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateChannelWindow)
        #update every 10 ms
        self.timer.start(10)

        #use the vertical layout for the current window
        self.setLayout(self.vbox)

    def cprint(self,data):
        #self.screenQueue.put(data)
        self.messageArea.append(data)

    def updateChannelWindow(self):
        if self.screenQueue.qsize() > 0:
            queue_message = self.screenQueue.get()
            print('queue_message: ',queue_message)
            # #...
            # #...
            # #...
            # #self.channel.append(...)


    def outgoing_parser(self):
        #self.messageArea.append("Hello QTextBrowser")
        #self.messageArea.append(self.sendMessage.text())
        outMessage = self.sendMessage.text()
        print(outMessage)
        self.threadQueue.put(str(outMessage))
        self.sendMessage.clear()


    def run(self):
        #run the app and show the main form
        self.show()
        self.qt_app.exec_()


#connect to the server
s = socket.socket()
host = '178.233.19.205'
port = 12345
s.connect((host,port))
sendQueue = Queue.Queue()
screenQueue = Queue.Queue()
app = ClientDialog (sendQueue,screenQueue)
#start threads
rt = ReadThread("ReadThread",s,sendQueue,screenQueue,app)
rt.start()
    #
wt = WriteThread("WriteThread",s,sendQueue)
wt.start()
    #
app.run()

rt.join()
wt.join()
s.close()





