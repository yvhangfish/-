from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QPushButton
from PyQt5.QtCore import QPoint, QTimer, Qt
from PyQt5.QtGui import QPainter, QColor
import sys
import random
import copy


class SnakeGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "贪吃蛇 -- written by fish 2018/04/06"
        self.gap = 20
        self.width = self.gap * 2 + Snake.SIDE_LEN * Snake.RANGE
        self.height = self.gap * 3 + Snake.SIDE_LEN * Snake.RANGE
        self.snake = Snake()
        self.timer = QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.game_on)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.center()
        self.statusBar().showMessage('Ready')
        self.btnStart = QPushButton(self.tr('开始'), self)
        self.btnStart.move((self.width - self.btnStart.width()) // 2, (self.height - self.btnStart.height()) // 2)
        self.btnStart.clicked.connect(self.start_game)
        self.show()

    def start_game(self):
        self.snake = Snake()
        self.btnStart.setVisible(False)
        self.timer.start()

    def end_game(self):
        self.btnStart.setVisible(True)
        self.timer.stop()

    def game_on(self):
        if self.snake.is_alive():
            self.snake.change_dir(self.snake.a_search())
            print("dir:", Snake.dir[self.snake.direction])
            self.snake.move()
        else:
            self.end_game()
        self.update()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def do_drawing(self,qp):
        size = self.size()
        qp.setBrush(Qt.black)
        qp.drawRect(0, 0, size.width(), size.height()-self.gap)
        qp.setBrush(Qt.gray)
        width = self.snake.SIDE_LEN * self.snake.RANGE
        height = self.snake.SIDE_LEN * self.snake.RANGE
        qp.drawRect(self.gap, self.gap, width, height)

    def do_drawing_game(self,qp):
        self.do_drawing(qp)
        side_len = self.snake.SIDE_LEN
        qp.setBrush(Qt.black)
        qp.drawRect(self.gap+side_len*self.snake.head.x(), self.gap+side_len*self.snake.head.y(), side_len, side_len)
        qp.setBrush(QColor(0xFF,0x82,0x47))
        for body_rect in self.snake.body:
            qp.drawRect(self.gap+side_len*body_rect.x(), self.gap+side_len*body_rect.y(), side_len, side_len)
        qp.setBrush(Qt.red)
        qp.drawRect(self.gap+side_len*self.snake.food.x(), self.gap+side_len*self.snake.food.y(), side_len, side_len)

    def paintEvent(self, e):
        qp = QPainter(self)
        # qp.begin(self)
        self.do_drawing_game(qp)
        qp.end()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_W and self.snake.direction != Snake.DOWN:
            self.snake.change_dir(Snake.UP)
        elif e.key() == Qt.Key_S and self.snake.direction != Snake.UP:
            self.snake.change_dir(Snake.DOWN)
        elif e.key() == Qt.Key_A and self.snake.direction != Snake.RIGHT:
            self.snake.change_dir(Snake.LEFT)
        elif e.key() == Qt.Key_D and self.snake.direction != Snake.LEFT:
            self.snake.change_dir(Snake.RIGHT)


class Snake():
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    dir = ["UP", "DOWN", "LEFT", "RIGHT"]

    LIVING = 1
    DEAD = 0

    RANGE = 20
    SIDE_LEN = 20

    def __init__(self):
        self.status = self.LIVING
        self.head = QPoint(10, 10)
        self.length = 4
        self.body = []
        self.direction = self.RIGHT
        self.sum = 10
        self.step = 0
        for i in range(self.length-1):
            self.body.append(QPoint(7+i,10))
        self.food = self.create_food()

    def change_dir(self, direction):
        self.direction = direction

    def judge(self):
        x = self.head.x()
        y = self.head.y()
        if x == 0 and self.direction == Snake.LEFT:
            return False
        if x == Snake.RANGE - 1 and self.direction == Snake.RIGHT:
            return False
        if y == 0 and self.direction == Snake.UP:
            return False
        if y == Snake.RANGE - 1 and self.direction == Snake.DOWN:
            return False

        return x in range(0, self.RANGE) and y in range(0, self.RANGE) and self.head not in self.body

    def create_food(self):
        while True:
            x = random.choice(range(self.RANGE))
            y = random.choice(range(self.RANGE))
            p = QPoint(x, y)
            if p not in self.body and p != self.head:
                break
        self.food = p
        # print("food:", self.food.x(), self.food.y())
        return p

    def move(self):
        self.body.append(copy.copy(self.head))
        pre_head = copy.copy(self.head)
        tail = self.body.pop(0)

        head_x = self.head.x()
        head_y = self.head.y()

        if self.direction == self.UP:
            self.head.setY(head_y-1)
        elif self.direction == self.DOWN:
            self.head.setY(head_y+1)
        elif self.direction == self.LEFT:
            self.head.setX(head_x-1)
        elif self.direction == self.RIGHT:
            self.head.setX(head_x+1)

        if self.head == self.food:
            self.body.insert(0, tail)
            self.step += 1
            self.food = self.create_food()

        if not self.judge():
            self.status = self.DEAD

    def is_alive(self):
        return self.status == self.LIVING

    def a_search(self):
        open_list = []
        close_list = []
        stack = []
        head_node = Node(self.head)
        food_node = Node(self.food)
        head_node.setH(self.dis(head_node, food_node))
        open_list.append(head_node)

        now = Node(QPoint(0, 0))
        while len(open_list) != 0:
            # max = -1
            # for node in open_list:
            #     if node.getF() >= max:
            #         max = node.getF()
            #         now = node
            min = 40
            for node in open_list:
                if node.getF() <= min:
                    min = node.getF()
                    now = node
            # print("now: ", now.point.x(), now.point.y())
            open_list.remove(now)
            close_list.append(now)

            up = Node(QPoint(now.point.x(), now.point.y()-1))
            down = Node(QPoint(now.point.x(), now.point.y()+1))
            left = Node(QPoint(now.point.x()-1, now.point.y()))
            right = Node(QPoint(now.point.x()+1, now.point.y()))
            temp_list = [up, down, left, right]
            for node in temp_list:
                if node in close_list or node.point.x() < 0 or node.point.y() < 0 or node.point.x() >= Snake.RANGE or node.point.y() >= Snake.RANGE or node.point in self.body:
                    continue

                if node not in open_list:
                    node.set_parent(now)
                    node.setG(now.getG() + 1)
                    node.setH(self.dis(node, food_node))
                    open_list.append(node)
                    # print("new node: ", node.point.x(), node.point.y())

                    if node.point.x() == food_node.point.x() and node.point.y() == food_node.point.y():
                        stack.clear()
                        path_node = node.get_parent()
                        stack.append(path_node)
                        while True:
                            if path_node.point.x() == self.head.x() and path_node.point.y() == self.head.y():
                                break
                            stack.append(path_node)
                            path_node = path_node.get_parent()
                        x = stack[-1].point.x()
                        y = stack[-1].point.y()
                        # print("dest: ", x, y)

                        if x < head_node.point.x() and y == head_node.point.y():
                            return Snake.LEFT
                        elif x > head_node.point.x() and y == head_node.point.y():
                            return Snake.RIGHT
                        elif x == head_node.point.x() and y < head_node.point.y():
                            return Snake.UP
                        elif x == head_node.point.x() and y > head_node.point.y():
                            return Snake.DOWN
                        else:
                            print("target: ", x, y)
                            print("head_node: ", head_node.point.x(), head_node.point.y())
                            print("no dir")
                else:
                    if (now.getG() + 1 < node.getG()):
                        node.set_parent(now)
                        node.setG(now.getG()+1)

    def dis(self, src, dest):
        return abs(src.point.x()-dest.point.x()) + abs(src.point.y()-dest.point.y())


class Node:
    def __init__(self, point):
        self.point = point
        self.parent = None
        self.G = 0
        self.H = 0
        self.F = 0

    def set_parent(self, node):
        self.parent = node

    def get_parent(self):
        return self.parent

    def getG(self):
        return self.G

    def setG(self, G):
        self.G = G

    def getH(self):
        return self.H

    def setH(self, H):
        self.H = H

    def getF(self):
        return self.G+self.H


if __name__ == '__main__':
    app = QApplication(sys.argv)
    snake = SnakeGame()
    sys.exit(app.exec_())
