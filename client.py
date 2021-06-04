# -*- coding: utf-8 -*-
from server import Game
import sys
from typing import Text

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import gobangGUI
import requests
import json
import time
import threading

server_ip = None
client_ip = None
BLACK = 1
WHITE = 2
RED = 3
Game_mode = 0

import socket


def get_host_ip():
    """
    查询本机ip地址
    :return:
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def connectServer(ip):  # 查看服务器是否在线并连接服务器
    try:
        r = requests.get("http://" + ip + ":8088" + "/Game/Ready/feedback")

        global server_ip
        server_ip = ip
        return True, r.text
    except Exception as e:
        print(e)
        return False, None


def GetIntoGame(ip, color):
    try:
        req = {"ip": ip, "color": color}
        req = json.dumps(req)
        r = requests.post("http://" + server_ip + ":8088" + "/Game/GetIn", req)
        print("r:", r.text)
        return True, r.text
    except Exception as e:
        print(e)
        return False, None


class Home(QMainWindow):

    def __init__(self):
        super(Home, self).__init__()
        # QtGui.QWidget.__init__(self)
        self.style = """ 
                        QPushButton{background-color:grey;color:white;} 
                        #window{ background-image: url(background1.jpg); }
                    """
        self.setStyleSheet(self.style)
        self.initUI()

    def initUI(self):

        self.resize(650, 480)
        self.statusBar().showMessage('Ready')
        self.setObjectName("window")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.center()

        widget = QWidget()
        label = QLabel()
        label.setText("<font size=%s><B>%s</B></font>" % ("15", "五子棋对战系统"))
        self.ipInput = QLineEdit(self)
        self.ipInput.setPlaceholderText('输入服务器ip')
        connect = QPushButton("connect", self)
        connect.clicked.connect(self.connect_server)
        widget.setStatusTip('  ')
        # start.resize(50, 25)
        quit = QPushButton("Quit", self)
        # quit.resize(50,25)
        quit.clicked.connect(self.quitClicked)
        self.mode = QLineEdit(self)
        self.mode.setPlaceholderText('输入模式0双人1三人')
        # quit.resize(50,25)
        # quit.clicked.connect(self.quitClicked)
        vbox1 = QVBoxLayout()  # 垂直布局
        vbox2 = QVBoxLayout()
        vbox3 = QVBoxLayout()
        vbox4 = QVBoxLayout()

        # 两边空隙填充
        label1 = QLabel()
        label1.resize(50, 50)
        label2 = QLabel()
        label2.resize(50, 50)
        vbox1.addWidget(label1)
        # vbox2.addWidget(label)
        vbox4.addWidget(self.ipInput)
        vbox4.addWidget(self.mode)
        vbox4.addWidget(connect)
        vbox4.addWidget(quit)
        vbox3.addWidget(label2)
        # 按钮两边空隙填充
        label3 = QLabel()
        label3.resize(50, 50)
        label4 = QLabel()
        label4.resize(50, 50)
        hbox1 = QHBoxLayout()
        hbox1.addWidget(label3)
        hbox1.addLayout(vbox4)
        hbox1.addWidget(label4)
        # 标题与两个按钮上下协调
        label5 = QLabel()
        label5.resize(1, 1)
        label6 = QLabel()
        label6.resize(1, 1)
        label7 = QLabel()
        label7.resize(1, 1)
        vbox2.addWidget(label5)
        vbox2.addWidget(label)
        vbox2.addWidget(label6)
        vbox2.addLayout(hbox1)
        vbox2.addWidget(label7)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox1)
        hbox.addLayout(vbox2)
        hbox.addLayout(vbox3)
        widget.setLayout(hbox)

        self.setCentralWidget(widget)

    def connect_server(self):
        global Game_mode
        text = self.ipInput.text()
        text_mode = self.mode.text()  # wzy
        if text_mode == "1":
            Game_mode = 1
        succ, _ = connectServer(text)
        if succ:
            msg = {"mode": text_mode}
            r = requests.post("http://" + text + ":8088" + "/Game/choose", json.dumps(msg))
            self.hide()
            self.ui = ChooseColor()  # 必须将另一个界面改为成员变量，负责MainPage会与函数调用周期一样一闪而过
            self.ui.show()
        else:
            QMessageBox.warning(self, "警告信息", "服务器未开启", QMessageBox.Yes, QMessageBox.Yes)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            QApplication.postEvent(self, QEvent(174))
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def quitClicked(self):
        reply = QMessageBox.question(self, 'Warning',
                                     'Are you sure to quit?', QMessageBox.Yes,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            quit()

    def center(self):
        qr = self.frameGeometry()  # 得到该主窗口的矩形框架qr
        cp = QDesktopWidget().availableGeometry().center()  # 屏幕中间点的坐标cp
        qr.moveCenter(cp)  # 将矩形框架移至屏幕正中央
        self.move(qr.topLeft())  # 应用窗口移至矩形框架的左上角点


class ChooseColor(Home):
    def __init__(self):
        super(ChooseColor, self).__init__()

    def initUI(self):
        global Game_mode
        self.resize(600, 200)
        self.statusBar().showMessage('Ready')
        self.setObjectName("window")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.center()
        self.get_status()
        widget = QWidget()
        label = QLabel()
        label.setText("<font size=%s><B>%s</B></font>" % ("15", "持方选择"))
        black_label = QLabel()
        black_label.setText("<font size=%s><B>%s</B></font>" % ("10", "黑方"))
        self.black_ip = QLabel()
        self.black_ip.setText("<font size=%s><B>%s</B></font>" % ("6", self.black))
        black_in = QPushButton("加入", self)
        black_in.clicked.connect(self.BlackGetIn)
        widget.setStatusTip('  ')
        # start.resize(50, 25)
        white_label = QLabel()
        white_label.setText("<font size=%s><B>%s</B></font>" % ("10", "白方"))
        self.white_ip = QLabel()
        self.white_ip.setText("<font size=%s><B>%s</B></font>" % ("6", self.white))
        white_in = QPushButton("加入", self)
        white_in.clicked.connect(self.WhiteGetIn)
        # ****************************wzy
        print(Game_mode)
        if Game_mode == 1:
            red_label = QLabel()
            red_label.setText("<font size=%s><B>%s</B></font>" % ("10", "红方"))
            self.red_ip = QLabel()
            self.red_ip.setText("<font size=%s><B>%s</B></font>" % ("6", self.red))
            red_in = QPushButton("加入", self)
            red_in.clicked.connect(self.redGetIn)
        # *****************************
        start = QPushButton("Start", self)
        start.clicked.connect(self.startClicked)
        quit = QPushButton("Quit", self)
        quit.clicked.connect(self.quitClicked)
        refresh = QPushButton("刷新", self)
        refresh.clicked.connect(self.refreshClicked)
        # quit.resize(50,25)
        # start.clicked.connect(self.startClicked)
        # quit.clicked.connect(self.quitClicked)

        vbox1 = QVBoxLayout()  # 垂直布局
        vbox2 = QVBoxLayout()
        vbox3 = QVBoxLayout()
        vbox4 = QVBoxLayout()
        vbox5 = QVBoxLayout()
        vbox6 = QVBoxLayout()

        # 两边空隙填充
        label1 = QLabel()
        label1.resize(50, 50)
        label2 = QLabel()
        label2.resize(50, 50)
        vbox1.addWidget(label1)
        # vbox2.addWidget(label)

        vbox4.addWidget(black_label)
        vbox4.addWidget(self.black_ip)
        vbox4.addWidget(black_in)

        vbox5.addWidget(white_label)
        vbox5.addWidget(self.white_ip)
        vbox5.addWidget(white_in)
        if Game_mode == 1:
            vbox5.addWidget(red_label)
            vbox5.addWidget(self.red_ip)
            vbox5.addWidget(red_in)

        vbox3.addWidget(label2)
        # 按钮两边空隙填充
        label3 = QLabel()
        label3.resize(100, 50)
        label4 = QLabel()
        label4.resize(100, 50)
        hbox1 = QHBoxLayout()
        hbox1.addLayout(vbox4)
        hbox1.addWidget(label3)
        hbox1.addWidget(label4)
        hbox1.addLayout(vbox5)

        # 标题与两个按钮上下协调
        label5 = QLabel()
        label5.resize(1, 1)
        label6 = QLabel()
        label6.resize(1, 1)
        label7 = QLabel()
        label7.resize(1, 1)
        vbox2.addWidget(label5)
        vbox2.addWidget(label)
        vbox2.addWidget(label6)
        vbox2.addLayout(hbox1)
        vbox2.addWidget(label7)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox1)
        hbox.addLayout(vbox2)
        hbox.addLayout(vbox3)

        vbox6.addWidget(refresh)
        vbox6.addWidget(start)
        vbox6.addWidget(quit)
        hbox.addLayout(vbox6)
        widget.setLayout(hbox)

        self.setCentralWidget(widget)

    def refreshClicked(self):
        self.get_status()
        self.black_ip.setText("<font size=%s><B>%s</B></font>" % ("6", self.black))
        self.black_ip.repaint()
        self.white_ip.setText("<font size=%s><B>%s</B></font>" % ("6", self.white))
        self.white_ip.repaint()
        if Game_mode == 1:
            self.red_ip.setText("<font size=%s><B>%s</B></font>" % ("6", self.red))
            self.red_ip.repaint()

    def get_status(self):
        conn, msg = connectServer(server_ip)
        if conn:
            msg = json.loads(msg)
            print(msg["white"])
            if msg["black"] is not None:
                self.black = msg["black"]
            else:
                self.black = "Wait For client"
            if msg["white"] is not None:
                self.white = msg["white"]
            else:
                self.white = "Wait For client"
            if msg["red"] is not None:
                self.red = msg["red"]
            else:
                self.red = "Wait For client"
        else:
            pass

    def BlackGetIn(self):
        if hasattr(self, "color") and self.color == WHITE:
            GetIntoGame(None, WHITE)  # 重置ip

        succ, msg = GetIntoGame(client_ip, BLACK)
        if succ:
            msg = json.loads(msg)
            if msg["succ"]:
                self.get_status()
                self.black_ip.setText("<font size=%s><B>%s</B></font>" % ("6", self.black))
                self.black_ip.repaint()
                self.white_ip.setText("<font size=%s><B>%s</B></font>" % ("6", self.white))
                self.white_ip.repaint()
                if Game_mode == 1:
                    self.red_ip.setText("<font size=%s><B>%s</B></font>" % ("6", self.red))
                    self.red_ip.repaint()
                self.color = BLACK

    def redGetIn(self):
        if hasattr(self, "color") and self.color == RED:
            GetIntoGame(None, RED)  # 重置ip

        succ, msg = GetIntoGame(client_ip, RED)
        if succ:
            msg = json.loads(msg)
            if msg["succ"]:
                self.get_status()
                self.black_ip.setText("<font size=%s><B>%s</B></font>" % ("6", self.black))
                self.black_ip.repaint()
                self.white_ip.setText("<font size=%s><B>%s</B></font>" % ("6", self.white))
                self.white_ip.repaint()
                self.red_ip.setText("<font size=%s><B>%s</B></font>" % ("6", self.red))
                self.red_ip.repaint()
                self.color = RED

    def WhiteGetIn(self):
        if hasattr(self, "color") and self.color == BLACK:
            GetIntoGame(None, BLACK)  # 重置ip
        succ, msg = GetIntoGame(client_ip, WHITE)
        if succ:
            msg = json.loads(msg)
            if msg["succ"]:
                self.get_status()
                self.black_ip.setText("<font size=%s><B>%s</B></font>" % ("6", self.black))
                self.black_ip.repaint()
                self.white_ip.setText("<font size=%s><B>%s</B></font>" % ("6", self.white))
                self.white_ip.repaint()
                if Game_mode == 1:
                    self.red_ip.setText("<font size=%s><B>%s</B></font>" % ("6", self.red))
                    self.red_ip.repaint()
                self.color = WHITE

    def startClicked(self):
        global Game_mode
        self.hide()
        self.ui = gobangGUI.GoBang(self.color, client_ip, server_ip,
                                   Game_mode)  # 必须将另一个界面改为成员变量，负责MainPage会与函数调用周期一样一闪而过
        self.ui.show()
        # self.Game = GameStart(self.ui,self.color,client_ip)


class GameStart:
    def __init__(self, GoBang, color, client_ip, server_ip):
        self.current = None
        self.status = 0
        self.GoBang = GoBang
        self.MyColor = color  # True
        self.client_ip = client_ip
        self.server_ip = server_ip
        self.StartGame()
        monitor_thread = threading.Thread(target=self.CheckStatus_thread)
        monitor_thread.start()

    def StartGame(self):
        r = requests.get("http://" + self.server_ip + ":8088" + "/Game/Start")

    def CheckStatus_thread(self):
        while self.status < 2:
            req = {"color": self.MyColor}
            r = requests.post("http://" + self.server_ip + ":8088" + "/Game/Status/feedback", json.dumps(req))
            msg = json.loads(r.text)
            print(msg)
            self.status = msg["status"]
            self.GoBang.currentInfo(msg)
            time.sleep(0.5)

    def PutDown(self, x, y):
        msg = {"x": x, "y": y, "color": self.MyColor}
        r = requests.post("http://" + self.server_ip + ":8088" + "/board/Put", json.dumps(msg))
        result = json.loads(r.text)


def main():
    app = QApplication(sys.argv)
    main = Home()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    # client_ip = get_host_ip()    #查询本机IP地址
    client_ip = "1.2.3.5"  # 利用固定IP地址
    main()
