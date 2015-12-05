import socket
import sys
import threading

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import Queue
import time


class ReadThread (threading.Thread):
    def __init__(self,name,csoc,threadQueue,screenQueue,app):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.nickname = ""
        self.threadQueue = threadQueue
        self.screenQueue = screenQueue #...
        self.app = app

    def incoming_parser(self,data):
        if len(data) == 0:
            return "Error!!!"
        if len(data) > 3 and not data[3] == "":
            response = "ERR"
            self.csoc.send(response)
            return "Error"
        if data[0:3] == "HEL":
            #Yeni Kullanıcı olarak kabul edildiniz
        elif data[0:3] == "REJ":
            #Kullanıcı olarak kabul edilMEdiniz
        elif data[0:3] == "BYE":
            #Çıkış
        elif data[0:3] == "LSA":
            #user List = data[4:] Kullanıcı Listesi geldi
        elif data[0:3] == "TOC":
            #Bağlantı testi başarılı
        elif data[0:3] == "SOK":
            #Genel mesaj gönderme başarılı
        elif data[0:3] == "MOK":
            #Özel mesaj gönderme başarılı
        elif data[0:3] == "MNO":
            #Özel mesaj hedefi bulunamadı
        elif data[0:3] == "ERR":
            #Hatalı Komut gönderdiniz
        elif data[0:3] == "ERL":
            #Giriş yapılaMAdı; login olmalısınız
        #...

    def run(self):
        while True:
            try:
                data = self.csoc.recv(1024)
                self.app.cprint(self.incoming_parser(data))
            except:
                pass
            if data[0:3] == "BYE":
                self.csoc.close()
            #...

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
                    self.csoc.send(queue_message)
                except socket.error:
                    self.csoc.close()

class ClientDialog(QDialog):
    def __init__(self,threadQueue,screenQueue):
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
        self.sender = QLineEdit("",self)

        #the channel region
        self.channel = QTextBrowser()
        self.channel.setMinimumSize(QSize(480,0))

        #the send button
        self.send_button = QPushButton('&Send')

        #the users' section
        self.userList = QListView()

        #connect the Go button to its callback
        self.send_button.click(self.outgoing_parser)

        #add the controls to the vertical layout
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.sender)
        self.vbox.addWidget(self.send_button)
        self.hbox.addWidget(self.channel)
        self.hbox.addWidget(self.userList)

        #start timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateChannelWindow)
        #update every 10 ms
        self.timer.start(10)

        #use the vertical layout for the current window
        self.setLayout(self.vbox)

    def cprint(self,data):
        self.channel.append(data)

    def updateChannelWindow(self):
        if self.screenQueue.qsize() > 0:
            queue_message = self.screenQueue.get()
            #...
            #...
            #...
            #self.channel.append(...)
    def outgoing_parser(self):
        #...
        #...
        #...
    def run(self):
        #run the app and show the main form
        self.show()
        self.qt_app.exec_()

    #connect to the server
    s = socket.socket()
    #host = ...
    #port = ...
    s.connect((host,port))

    #sendQueue = ...
    #screenQueue = ...

    #app = ClientDialog(sendQueue,screenQueue)

    #start threads
    rt = ReadThread("ReadThread",s,sendQueue,screenQueue)
    rt.start()

    wt = WriteThread("WriteThread",s,sendQueue)
    wt.start()

    app.run()
    rt.join()
    wt.join()
    s.close()





