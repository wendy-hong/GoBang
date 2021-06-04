import flask
from flask import Flask
from flask.globals import request
from flask_cors import CORS
from chessboard import *
import json

app = Flask(__name__, static_folder='dist', template_folder='dist', static_url_path='')
CORS(app, supports_credenials=True)
gameServer = None

BLACK = 1
WHITE = 2
RED = 3  # wzy
mode = 0  # 默认两人 wzy


def ReturnMsg(succ, Msg="", win=None):
    msg = {"succ": succ, "msg": Msg, "win": win}
    return msg


class Game:  # 生成一个新棋盘并开始棋局 wzy
    def __init__(self):
        self.chessboard = ChessBoard()
        self.whiteList = []  # 白棋落子顺序
        self.blackList = []
        self.redList = []
        self.blackStep = 0
        self.whiteStep = 0
        self.redStep = 0

    def PutOne(self, x, y, state):  # 落子，state=1表示黑方落子，state=2表示白方落子 state=3 表示红方 wzy
        if not self.chessboard.get_xy_on_logic_state(x, y):
            if state == BLACK:
                self.chessboard.draw_xy(x, y, state)
                self.blackList.append((x, y))
            elif state == WHITE:
                self.chessboard.draw_xy(x, y, state)
                self.whiteList.append((x, y))
            elif state == RED:
                self.chessboard.draw_xy(x, y, state)
                self.redList.append((x, y))
            if (self.chessboard.anyone_win(x, y)):
                gameServer.game_status = state + 1
                return 1  # 有人胜利
            else:
                return 0  # 正常下棋
        else:
            return -1  # 此位置已被占用，不可以落子

    def Restart(self):
        self.chessboard.reset()

    def getLast(self, color):
        if color == BLACK:
            if len(self.blackList) != 0:
                self.blackStep += 1
                return self.blackList[-1]
            else:
                return None
        elif color == WHITE:
            if len(self.whiteList) != 0:
                self.whiteStep += 1
                return self.whiteList[-1]
            else:
                return None
        elif color == RED:
            if len(self.redList) != 0:
                self.redStep += 1
                return self.redList[-1]
            else:
                return None

    def getHistory(self, step):
        return {"black": self.blackList[-step:], "white": self.whiteList[-step:], "red": self.redList[-step:]}


class GameServer:  # server的主体
    def __init__(self):
        self.black = None  # 两方ip
        self.white = None
        self.red = None  # wzy
        self.current = None  # True表示当前是黑方落子，False代表为白方落子 3代表为红方落子
        self.game_status = 0  # 0表示未开始，1表示进行中，2表示黑方胜，3表示白方胜 4代表为红方胜
        self.Game = Game()

    def GetIntoGame(self, ip, color):  # 加入游戏 wzy
        if self.game_status:
            return ReturnMsg(False, "Game has already Start")
        if color == BLACK or color == WHITE or color == RED:
            if color == BLACK:
                if self.black is None or self.black == ip or ip == None:
                    self.black = ip
                    return ReturnMsg(True, "")
                else:
                    return ReturnMsg(False, "Black is already in")  # 当前黑方已经加入
            elif color == WHITE:
                if self.white is None or self.white == ip or ip == None:
                    self.white = ip
                    return ReturnMsg(True, "")
                else:
                    return ReturnMsg(False, "White is already in")  # 当前黑方已经加入
            elif color == RED:
                if self.red is None or self.red == ip or ip == None:
                    self.red = ip
                    return ReturnMsg(True, "")
                else:
                    return ReturnMsg(False, "red is already in")  # 当前黑方已经加入

    def GetBoard(self):  # 获取当前棋盘状态
        return json.dumps({"board": self.Game.chessboard.board()})

    def GameStatus(self):  # 游戏状态
        return ReturnMsg(self.game_status, "")

    def GameStart(self):  # 开始游戏
        self.current = BLACK
        # if self.black and self.white and not self.gameStart:
        if self.black and not self.game_status:
            self.game_status = 1
            self.Game = Game()
            return ReturnMsg(True, "")
        else:
            return ReturnMsg(False, "Wait For People")

    def Putdown(self, x, y, state):  # 落子
        global mode
        if self.current == state:
            result = self.Game.PutOne(x, y, state)
            print("ywe")
            if mode == 0:
                print("333eee")
                self.current = self.current % 2 + 1  # 切换持方
            elif mode == 1:
                if self.current == 1:
                    self.current = 2
                elif self.current == 2:
                    self.current = 3
                elif self.current == 3:
                    self.current = 1
        if result == 1:
            return ReturnMsg(True, "Game End", state)
        elif result == 0:
            return ReturnMsg(True, "")
        else:
            return ReturnMsg(False, "This position was occupied")


@app.route("/Game/Ready/feedback", methods=['GET'])  # 获取当前游戏准备状态wzy
def game_ready_fdb():
    msg = {"black": gameServer.black, "white": gameServer.white, "red": gameServer.red,
           "status": gameServer.game_status}
    return json.dumps(msg)


@app.route("/Game/Status/feedback", methods=['POST'])  # 获取当前的游戏状态 WZY
def game_status_fdb():  # wzy\
    global mode
    msg = {"current": gameServer.current, "status": gameServer.game_status}
    print(request.get_data())
    req = json.loads(request.get_data())
    color = req["color"]
    if color == BLACK:
        msg["last"] = gameServer.Game.getLast(WHITE)
        msg["last1"] = gameServer.Game.getLast(RED)
    if color == WHITE:
        msg["last"] = gameServer.Game.getLast(BLACK)
        msg["last1"] = gameServer.Game.getLast(RED)
    if color == RED:
        msg["last"] = gameServer.Game.getLast(WHITE)
        msg["last1"] = gameServer.Game.getLast(BLACK)
    return json.dumps(msg)


# @app.route("/GameStatus/check",methods=['GET'])
# def check_status():
#     global gameServer
#     return json.dumps(gameServer.GameStatus())

@app.route("/Game/Start", methods=["GET"])  # 开始游戏
def game_start():
    return json.dumps(gameServer.GameStart())


@app.route("/Game/GetIn", methods=['POST'])  # 进入游戏
def AccessGame():
    msg = json.loads(request.get_data())
    ip = msg["ip"]
    color = msg["color"]
    res = gameServer.GetIntoGame(ip, color)
    return json.dumps(res)


@app.route("/board/Get", methods=['GET'])  # 获取棋盘
def get_board():
    return gameServer.GetBoard()


@app.route("/board/getHistory/<step>", methods=["GET"])  # 获取历史步
def get_history(step):
    step = int(step)
    return json.dumps(gameServer.Game.getHistory(step))


@app.route("/board/Put", methods=['POST'])  # 下棋WZY
def PutOnce():
    msg = json.loads(request.get_data())
    color = msg["color"]
    x = msg["x"]
    y = msg["y"]
    if color == BLACK:
        return json.dumps(gameServer.Putdown(x, y, BLACK))
    elif color == WHITE:
        return json.dumps(gameServer.Putdown(x, y, WHITE))
    elif color == RED:
        return json.dumps(gameServer.Putdown(x, y, RED))
    else:
        return ReturnMsg(False, "You Are Not In This Game")


@app.route("/Game/Reset", methods=["GET"])
def Reset():  # 重新开始游戏
    """
    需要自行完成
    """
    pass


@app.route("/Game/choose", methods=['POST'])  # WZY
def choose_mode():
    global mode
    msg = json.loads(request.get_data())
    if msg["mode"] == "1":
        mode = 1  # mode 0 双人 mode 1三人
    print(mode)
    return ReturnMsg(False, "OK")


if __name__ == '__main__':
    gameServer = GameServer()
    app.run(
        host='0.0.0.0',
        port='8088',
        debug=True
    )
