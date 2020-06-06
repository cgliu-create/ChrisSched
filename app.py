from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit
from PyQt5 import QtGui
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor
from PyQt5.QtCore import Qt
import sys
import os
import csv

# this is a dictionary of color codes
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

# reads and writes csv files that represent a schedule
class SchedData:
    def __init__(self):
        self.days = ('mon','tue', 'wed', 'thu', 'fri', 'sat', 'sun')
        self.data = [list() for i in range(8)]
        self.color_data = {}
    def readCSV(self, sched_name):
        self.data = [list() for i in range(8)]
        self.color_data = {}
        f = open(sched_name+'.csv')
        reader = csv.reader(f)
        line_num = 0
        for line in reader:
            if line_num < 8:
                self.data[line_num] = line
            if line_num >= 8:
                color = line[0]
                item = line[1]
                self.color_data[color] = item
            line_num += 1
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
        content = lines_before +  line + lines_after

# this displays the schedule based off SchedData
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

    def drawSched(self, painter, sdata):
        black = self.colors.getcolor("black")
        # draws the day abbreviations 
        for i in range(len(sdata.days)):
            x = self.sched_pos_x + 0
            y = self.sched_pos_y + self.square_size + self.font_size + (self.square_size + self.margin) * (i + 1)
            day_name = sdata.days[i]
            self.drawMessage(painter,  x, y, black, day_name)
       # draws the squares representing an hour in that day
        for i in range(1, len(sdata.data)):
            y = self.sched_pos_y + self.square_size + (self.square_size + self.margin) * i
            day_info = sdata.data[i]
            for j in range(len(day_info)):
                color = day_info[j]
                x = self.sched_pos_x + (self.square_size + self.margin) * (j + 2)
                self.drawSquare(painter, x, y, self.colors.getcolor(color))
        # draws the hour marks
        times = sdata.data[0]
        painter.rotate(-90)
        for i in range(len(times)):
            x = self.sched_pos_x + 3 * self.square_size + self.margin + (self.square_size + self.margin) * i
            y = self.sched_pos_y + 2 * self.square_size
            time_mark = times[i]
            self.drawMessage(painter, -y, x, black, time_mark)
        painter.rotate(90)

    def drawColors(self, painter, sdata):
        # draws what the colors mean
        y = self.sched_pos_y +  4 * self.square_size + (self.square_size + self.margin) * len(sdata.data)
        x = self.sched_pos_x + 0
        content = ""
        for color in sdata.color_data.keys():
            item = sdata.color_data[color]
            content += f"{color}: {item}  "
        black = self.colors.getcolor("black")
        self.drawMessage(painter, x, y, black, content)
        
# this is the gui
class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.width = 850
        self.height = 350
        self.SchedDraw = SchedDraw(20, 20, 20, 20, 10)
        self.SchedData = SchedData()
        self.SchedData.readCSV('name')
        self.show_color = True
        self.InitWindow()

    def InitWindow(self):
        self.setWindowTitle("Chris Sched")
        self.setGeometry(0, 0, self.width, self.height)
        sdraw = self.SchedDraw
        sdata = self.SchedData
        y = sdraw.sched_pos_y +  sdraw.square_size + (sdraw.square_size + sdraw.margin) * len(sdata.data)
        x = sdraw.sched_pos_x
        self.txt = QLineEdit("name", self)
        self.txt.move(x, y)
        x += self.txt.frameGeometry().width()
        self.btn0 = QPushButton("get sched", self)
        self.btn0.clicked.connect(self.loadSched)
        self.btn0.move(x, y)
        x += self.btn0.frameGeometry().width()
        self.btn1 = QPushButton("new sched", self)
        self.btn1.clicked.connect(self.loadSched)
        self.btn1.move(x, y)
        x += self.btn1.frameGeometry().width()
        self.btn2 = QPushButton("del sched", self)
        self.btn2.clicked.connect(self.loadSched)
        self.btn2.move(x, y)
        x += self.btn2.frameGeometry().width()
        self.btn3 = QPushButton("edit sched", self)
        self.btn3.clicked.connect(self.loadSched)
        self.btn3.move(x, y)
        x += self.btn3.frameGeometry().width()
        self.btn4 = QPushButton("show colors", self)
        self.btn4.clicked.connect(self.toggleColors)
        self.btn4.move(x, y)
        x += self.btn4.frameGeometry().width()
        self.btn5 = QPushButton("show scheds", self)
        self.btn5.clicked.connect(self.toggleColors)
        self.btn5.move(x, y)
        x += self.btn5.frameGeometry().width()
        self.btn6 = QPushButton("show instr", self)
        self.btn6.clicked.connect(self.toggleColors)
        self.btn6.move(x, y)

    def loadSched(self):
        name = self.txt.text()
        self.SchedData.readCSV(name)
        self.update()
        self.repaint()
    
    def toggleColors(self):
         self.show_color = not self.show_color
         self.update()
         self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.SchedDraw.drawSched(painter, self.SchedData)
        if self.show_color:
            self.SchedDraw.drawColors(painter, self.SchedData)

# testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
