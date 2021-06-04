#!/usr/bin/env python
# -*- coding:utf-8 -*-


from chessboard import ChessBoard
from client import GameStart
from ai import searcher

WIDTH = 540
HEIGHT = 540
MARGIN = 22
GRID = (WIDTH - 2 * MARGIN) / (15 - 1)
PIECE = 34
EMPTY = 0
BLACK = 1
WHITE = 2
RED = 3
import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QPainter
#from PyQt5.QtMultimedia import QSound

Game_mode = 0
last_current =4
# ----------------------------------------------------------------------
# 定义线程类执行AI的算法
# ----------------------------------------------------------------------
class AI(QtCore.QThread):
    finishSignal = QtCore.pyqtSignal(int, int)

    # 构造函数里增加形参
    def __init__(self, board, parent=None):
        super(AI, self).__init__(parent)
        self.board = board

    # 重写 run() 函数
    def run(self):
        self.ai = searcher()
        self.ai.board = self.board
        score, x, y = self.ai.search(1, 2)
        self.finishSignal.emit(x, y)


# ----------------------------------------------------------------------
# 重新定义Label类
# ----------------------------------------------------------------------
class LaBel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMouseTracking(True)

    def enterEvent(self, e):
        e.ignore()


class GoBang(QWidget):
    def __init__(self,color,ip,server_ip,mode):  #wzy
        super().__init__()
        self.InfoExchange = GameStart(self,color,ip,server_ip)
        self.initUI(color)
        global Game_mode
        Game_mode = mode

    def initUI(self,color):
        
        self.chessboard = ChessBoard()  # 棋盘类
    
        palette1 = QPalette()  # 设置棋盘背景
        palette1.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap('img/chessboard.jpg')))
        self.setPalette(palette1)

        # self.setStyleSheet("board-image:url(img/chessboard.jpg)")  # 不知道这为什么不行
        self.setCursor(Qt.PointingHandCursor)  # 鼠标变成手指形状
        #self.sound_piece = QSound("sound/luozi.wav")  # 加载落子音效
        #self.sound_win = QSound("sound/win.wav")  # 加载胜利音效
        #self.sound_defeated = QSound("sound/defeated.wav")  # 加载失败音效

        self.resize(WIDTH, HEIGHT)  # 固定大小 540*540
        self.setMinimumSize(QtCore.QSize(WIDTH, HEIGHT))
        self.setMaximumSize(QtCore.QSize(WIDTH, HEIGHT))

        self.setWindowTitle("GoBang")  # 窗口名称
        self.setWindowIcon(QIcon('img/black.png'))  # 窗口图标

        # self.lb1 = QLabel('            ', self)
        # self.lb1.move(20, 10)

        self.black = QPixmap('img/black.png')
        self.white = QPixmap('img/white.png')
        self.red = QPixmap('img/red.png')

        self.step = 0  # 步数
        self.x, self.y = 1000, 1000

        self.mouse_point = LaBel(self)  # 将鼠标图片改为棋子
        self.mouse_point.setScaledContents(True)
        self.color = color
        if color == BLACK:
            self.mouse_point.setPixmap(self.black)  # 加载黑棋
        elif color == WHITE:
            self.mouse_point.setPixmap(self.white)  # 加载白棋
        elif color == RED:
            self.mouse_point.setPixmap(self.red)  # 加载白棋
        self.mouse_point.setGeometry(270, 270, PIECE, PIECE)
        self.pieces = [LaBel(self) for i in range(1000)]  # 新建棋子标签，准备在棋盘上绘制棋子
        for piece in self.pieces:
            piece.setVisible(True)  # 图片可视
            piece.setScaledContents(True)  # 图片大小根据标签大小可变

        self.mouse_point.raise_()  # 鼠标始终在最上层
        self.ai_down = True  # AI已下棋，主要是为了加锁，当值是False的时候说明AI正在思考，这时候玩家鼠标点击失效，要忽略掉 mousePressEvent

        self.setMouseTracking(True)
        self.show()

    def paintEvent(self, event):  # 画出指示箭头
        qp = QPainter()
        qp.begin(self)
        self.drawLines(qp)
        qp.end()

    def mouseMoveEvent(self, e):  # 黑色棋子随鼠标移动
        # self.lb1.setText(str(e.x()) + ' ' + str(e.y()))
        self.mouse_point.move(e.x() - 16, e.y() - 16)

    def mousePressEvent(self, e):  # 玩家下棋
        if not self.myturn:
            return
        if e.button() == Qt.LeftButton and self.ai_down == True:
            x, y = e.x(), e.y()  # 鼠标坐标
            i, j = self.coordinate_transform_pixel2map(x, y)  # 对应棋盘坐标
            if not i is None and not j is None:  # 棋子落在棋盘上，排除边缘
                if self.chessboard.get_xy_on_logic_state(i, j) == EMPTY:  # 棋子落在空白处
                    self.InfoExchange.PutDown(i,j)
                    self.draw(i, j,self.color)
                    self.myturn = False
                    


    def remote_draw(self, i, j):
        if self.step != 0:
            self.draw(i, j)  # AI
            self.x, self.y = self.coordinate_transform_map2pixel(i, j)
        self.update()

    def currentInfo(self,msg):
        global Game_mode
        global last_current
        if msg["current"] == self.color and last_current != self.color:
            self.myturn = True
            board = self.chessboard.board()
            self.AI = AI(board)  # 新建线程对象，传入棋盘参数
            self.AI.finishSignal.connect(self.AI_draw)  # 结束线程，传出参数
            self.AI.start()  # run
        last_current = msg["current"]
        self.status = msg["status"]
        last = msg["last"]
        if Game_mode == 0:
            if last is not None:
                if self.color ==1:
                    self.draw(last[0],last[1],2)
                else:
                    self.draw(last[0],last[1],1)
            else:
                self.piece_now = msg["current"]

        elif Game_mode == 1:
            last = msg["last"]
            if last is not None:
                if self.color ==1:
                    self.draw(last[0],last[1],2)
                elif self.color ==2:
                    self.draw(last[0],last[1],1)
                elif self.color ==3:
                    self.draw(last[0],last[1],2)
            else:
                self.piece_now = msg["current"]
 
            last = msg["last1"]
            if last is not None:
                if self.color ==1:
                    self.draw(last[0],last[1],3)
                elif self.color ==2:
                    self.draw(last[0],last[1],3)
                elif self.color ==3:
                    self.draw(last[0],last[1],1)
            else:
                self.piece_now = msg["current"]
 
        winner = msg["status"]
        if winner > 1:
            self.mouse_point.clear()
            self.gameover(winner-1)

    def AI_draw(self, i, j):
        #if self.step != 0:
        self.InfoExchange.PutDown(i,j)
        self.draw(i, j,self.color)  # AI
        self.x, self.y = self.coordinate_transform_map2pixel(i, j)
        self.ai_down = True
        self.update()

    def draw(self, i, j,color):
        global Game_mode
        x, y = self.coordinate_transform_map2pixel(i, j)
        if color == BLACK:
            self.pieces[self.step].setPixmap(self.black)  # 放置黑色棋子
            self.chessboard.draw_xy(i, j, BLACK)
            #self.step += 1  # 步数+1
        elif color == WHITE:
            self.pieces[self.step].setPixmap(self.white)  # 放置白色棋子
            self.chessboard.draw_xy(i, j, WHITE)
            #self.step += 1  # 步数+1
        elif color == RED:
            self.pieces[self.step].setPixmap(self.red)  # 放置黑色棋子
            self.chessboard.draw_xy(i, j, RED)
            #self.step += 1  # 步数+1
        self.pieces[self.step].setGeometry(x, y, PIECE, PIECE)  # 画出棋子
        #self.sound_piece.play()  # 落子音效
        self.step += 1  # 步数+1

        # winner = self.chessboard.anyone_win(i, j)  # 判断输赢      不在本机进行
        # if winner != EMPTY:
        #     self.mouse_point.clear()
        #     print(winner-1,self.color)
        #     self.gameover(winner)

    def drawLines(self, qp):  # 指示AI当前下的棋子
        if self.step != 0:
            pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawLine(self.x - 5, self.y - 5, self.x + 3, self.y + 3)
            qp.drawLine(self.x + 3, self.y, self.x + 3, self.y + 3)
            qp.drawLine(self.x, self.y + 3, self.x + 3, self.y + 3)

    def coordinate_transform_map2pixel(self, i, j):
        # 从 chessMap 里的逻辑坐标到 UI 上的绘制坐标的转换
        return MARGIN + j * GRID - PIECE / 2, MARGIN + i * GRID - PIECE / 2

    def coordinate_transform_pixel2map(self, x, y):
        # 从 UI 上的绘制坐标到 chessMap 里的逻辑坐标的转换
        i, j = int(round((y - MARGIN) / GRID)), int(round((x - MARGIN) / GRID))
        # 有MAGIN, 排除边缘位置导致 i,j 越界
        if i < 0 or i >= 15 or j < 0 or j >= 15:
            return None, None
        else:
            return i, j

    def gameover(self, winner):
        if winner == self.color:
            #self.sound_win.play()
            reply = QMessageBox.question(self, 'You Win!', 'Continue?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        else:
            #sound_defeated.play()
            reply = QMessageBox.question(self, 'You Lost!', 'Continue?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:  # 复位
            self.piece_now = BLACK
            self.mouse_point.setPixmap(self.black)
            self.step = 0
            for piece in self.pieces:
                piece.clear()
            self.chessboard.reset()
            self.update()
        else:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GoBang()
    sys.exit(app.exec_())
