from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit
from PyQt5 import QtGui
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor
from PyQt5.QtCore import Qt
import sys
import os
import csv

class colors:
    def getcolor(self, name):
        color_list = {
        "white": "#ffffff",
        "black": '#000000',
        "red": '#ff0000',
        "orange" : '#ffb600',
        "yellow": '#fff700',
        "green": '#09ff00',
        "blue": '#0059ff',
        "purple": '#9d00ff',
        "pink" : '#ff00e1',
        "darkred" : '#a10000',
        "darkorange" : '#bd8700',
        "darkyellow" : '#c9c300',
        "darkgreen" : '#07c900',
        "darkblue" : '#003fb5',
        "darkpurple" : '#7300ba',
        "darkpink": '#bd00a6'
        }
        return color_list.get(name)


class SchedData:
    def __init__(self):
        self.days = ('mon','tue', 'wed', 'thu', 'fri', 'sat', 'sun')
        self.data = [list() for i in range(8)]
    def readCSV(self, sched_name):
        f = open(sched_name+'.csv')
        reader = csv.reader(f)
        for a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y in reader:
            data_values = [b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y]
            data_id = int(a)
            self.data[data_id] = data_values
    def writeCSVLine(self, sched_name, line):
        f = open(sched_name+'.csv', 'a')
        f.write(line+'\n')
        f.close()
    def editCSVLine(self, sched_name, line_num, line):
        sched =  open(sched_name+'.csv')
        lines_before = ""
        lines_after = ""
        num = 0
        for line_read in sched.readlines():
            if num < line_num:
                lines_before += line_read
            if num > line_num:
                lines_after += line_read
            num+=1
        edit = f"{line_num},"+line
        content = lines_before +  edit + lines_after


class SchedDraw():
    def __init__(self, xpos, ypos, square_size, font_size, margin):
        self.colors = colors()
        self.sched_pos_x = xpos
        self.sched_pos_y = ypos
        self.square_size = square_size
        self.font_size = font_size
        self.margin = margin

    def drawSquare(self, painter, x, y, color):
        color_code = self.colors.getcolor("black")
        painter.setPen(QPen(QColor(color_code), 1, Qt.SolidLine))
        painter.setBrush(QBrush(QColor(color), Qt.SolidPattern))
        painter.drawRect(x, y, self.square_size, self.square_size)

    def drawMessage(self, painter,  x, y, color, text):
        painter.setPen(QColor(color))
        painter.setFont(QtGui.QFont('Arial', self.font_size))
        painter.drawText(x, y, text)

    def draw(self, painter, sdata):
        for i in range(len(sdata.days)):
            x = self.sched_pos_x + 0
            y = self.sched_pos_y + self.square_size + self.font_size + (self.square_size + self.margin) * (i + 1)
            day_name = sdata.days[i]
            color_code = self.colors.getcolor("black")
            self.drawMessage(painter,  x, y, color_code, day_name)
        for i in range(1, len(sdata.data)):
            y = self.sched_pos_y + self.square_size + (self.square_size + self.margin) * i
            day_info = sdata.data[i]
            for j in range(len(day_info)):
                color = day_info[j]
                x = self.sched_pos_x + 2 * self.square_size + self.margin + (self.square_size + self.margin) * j
                self.drawSquare(painter, x, y, self.colors.getcolor(color))
        times = sdata.data[0]
        painter.rotate(-90)
        for i in range(len(times)):
            x = self.sched_pos_x + 3 * self.square_size + self.margin + (self.square_size + self.margin) * i
            y = self.sched_pos_y + 2 * self.square_size
            time_mark = times[i]
            self.drawMessage(painter, -y, x, self.colors.getcolor("black"), time_mark)
        

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.SchedDraw = SchedDraw(20, 20, 20, 20, 10)
        self.SchedData = SchedData()
        self.SchedData.readCSV('ex')
        self.InitWindow()
        self.show()

    def InitWindow(self):
        self.setWindowTitle("my app")
        self.setGeometry(0, 0, 900, 400)
        self.btn = QPushButton("Get Sched", self)
        self.btn.move(50, 300)
        self.txt = QLineEdit("Name", self)
        self.txt.move(200, 300)
        self.btn.clicked.connect(self.loadSched)

    def loadSched(self):
        name = self.txt.text()
        if name != "Name":
            self.SchedData.readCSV(name)
        self.update()
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.SchedDraw.draw(painter, self.SchedData)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
