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
    # given the name of the sched
    # records the data in sched.csv
    def readCSV(self, sched_name):
        # clears current data
        self.data = [list() for i in range(8)]
        self.color_data = {}
        # reads csv
        sched = open(sched_name+'.csv')
        reader = csv.reader(sched)
        line_num = 0
        for line in reader:
            if line_num < 8:
                self.data[line_num] = line
                check = 24 - len(line)
                # fills data if less than 24 hrs provided
                if check > 0:
                    for i in range(check):
                        self.data[line_num].append("white")
                # removed data if more than 24 hrs provided
                if check < 0:
                    for i in range(abs(check)):
                        self.data[line_num].pop(len(self.data[line_num])-1)
            if line_num >= 8:
                color = line[0]
                item = line[1]
                self.color_data[color] = item
            line_num += 1
        sched.close()
    # given the name of the sched
    # returns a list representing a line of the csv
    def readCSVLine(self, sched_name, line_num):
        self.readCSV(sched_name)
        return self.data[line_num]

    # given the name of the sched and a line
    # either creates a sched or opens an existing sched
    # adds the line
    def writeCSVLine(self, sched_name, line, write_over=False):
        if not os.path.exists(sched_name+'.csv'):
            sched = open(sched_name+'.csv', 'x')
            sched.write(line+'\n')
            sched.close()
        elif write_over:
            sched = open(sched_name+'.csv', 'w')
            sched.write(line)
            sched.close()
        else:
            sched = open(sched_name+'.csv', 'a')
            sched.write(line+'\n')
            sched.close()

    # given the name of the sched, the line num in question, and a line
    # copys the content before and after this line num
    # returns stiched together content with the given line
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
        sched.close()
        content = lines_before +  line + '\n' + lines_after
        self.writeCSVLine(sched_name, content, True)

        
class SchedEditor:
    def __init__(self, sched_data=SchedData()):
        self.sched_data = sched_data
        self.day_idex = { 'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6, 'sun': 7 }
        self.time_index = {}

    def markTimeIndex(self, sched_name):
        line0 =self.sched_data.readCSVLine(sched_name, 0)
        index = 0
        for mark in line0:
            self.time_index[mark] = index
            index += 1

    def markSchedule(self, sched_name, day, times, color):
        line_num = self.day_idex[day]
        content = self.sched_data.readCSVLine(sched_name, line_num)
        check = 24 - len(content)
        if check > 0:
            for i in range(check):
                content.append('white')
        changes = []
        for mark in times:
            changes.append(self.time_index[mark])
        for spot in changes:
            content.insert(spot, color)
            content.pop(spot + 1)
        line = ""
        index = 0
        for mark in content:
            if index == 0:
                line += mark
            else: 
                line = line + ',' + mark
            index +=1
        self.sched_data.editCSVLine(sched_name, line_num, line)

    def markMeaning(self, sched_name, color, meaning):
        line = color + ',' + meaning
        self.sched_data.writeCSVLine(sched_name, line, False)


# this displays the schedule data based off SchedData
class SchedDraw():
    # all positions of the items are relative
    def __init__(self, xpos, ypos, square_size, font_size, margin):
        self.colors = colors()
        self.sched_pos_x = xpos
        self.sched_pos_y = ypos
        self.square_size = square_size
        self.font_size = font_size
        self.margin = margin

    # draws a square of given position and color with painter
    def drawSquare(self, painter, x, y, color):
        color_code = self.colors.getcolor("black")
        painter.setPen(QPen(QColor(color_code), 1, Qt.SolidLine))
        painter.setBrush(QBrush(QColor(color), Qt.SolidPattern))
        painter.drawRect(x, y, self.square_size, self.square_size)

    # draws a message of given position, color, and text with painter
    def drawMessage(self, painter,  x, y, color, text):
        painter.setPen(QColor(color))
        painter.setFont(QtGui.QFont('Arial', self.font_size))
        painter.drawText(x, y, text)

    # draws all the schedule items
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
    # returns a string containing the color data from some SchedData
    def getColors(self, painter, sdata):
        # returns what the colors mean
        content = ""
        for color in sdata.color_data.keys():
            item = sdata.color_data[color]
            content += f"{color}: {item}  "
        return content
        black = self.colors.getcolor("black")
        
# this is the gui
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.SchedDraw = SchedDraw(20, 20, 20, 20, 10)
        self.SchedData = SchedData()
        self.SchedEditor = SchedEditor(self.SchedData)
        sdraw = self.SchedDraw
        self.width = (sdraw.square_size + sdraw.margin) * 28
        self.height = (sdraw.square_size + sdraw.margin) * 12
        self.setGeometry(0, 0, self.width, self.height)
        self.setWindowTitle("Chris Sched")
        self.SchedData.readCSV('empty')
        self.current_sched = 'empty'
        self.show_color = True
        self.show_scheds = False
        self.show_instr = False
        self.InitWindow()
    # this creates all the interactable gui elements
    def InitWindow(self):
        sdraw = self.SchedDraw
        sdata = self.SchedData
        y = sdraw.sched_pos_y +  sdraw.square_size + (sdraw.square_size + sdraw.margin) * 8
        x = sdraw.sched_pos_x
    # command text input
        self.txt0 = QLineEdit("example", self)
        self.txt0.move(x, y)
        x += self.txt0.frameGeometry().width()
    # button controls
    # get
        self.btn0 = QPushButton("get sched", self)
        self.btn0.clicked.connect(self.loadSched)
        self.btn0.move(x, y)
        x += self.btn0.frameGeometry().width()
    # new
        self.btn1 = QPushButton("new sched", self)
        self.btn1.clicked.connect(self.newSched)
        self.btn1.move(x, y)
        x += self.btn1.frameGeometry().width()
    # delete
        self.btn2 = QPushButton("del sched", self)
        self.btn2.clicked.connect(self.deleteSched)
        self.btn2.move(x, y)
        x += self.btn2.frameGeometry().width()
    # edit
        self.btn3 = QPushButton("edit sched", self)
        self.btn3.clicked.connect(self.editSched)
        self.btn3.move(x, y)
        x += self.btn3.frameGeometry().width()
    # colors
        self.btn4 = QPushButton("show colors", self)
        self.btn4.clicked.connect(self.showColors)
        self.btn4.move(x, y)
        x += self.btn4.frameGeometry().width()
    # scheds
        self.btn5 = QPushButton("show scheds", self)
        self.btn5.clicked.connect(self.showScheds)
        self.btn5.move(x, y)
        x += self.btn5.frameGeometry().width()
    # intructions
        self.btn6 = QPushButton("show instr", self)
        self.btn6.clicked.connect(self.showInstr)
        self.btn6.move(x, y)
        y = sdraw.sched_pos_y + 3 * sdraw.square_size + (sdraw.square_size + sdraw.margin) * 8
        x = sdraw.sched_pos_x + 0
    # data text output
        self.txt1 = QLineEdit("data", self)
        self.txt1.resize((sdraw.square_size + sdraw.margin) * 27, self.txt1.frameGeometry().height()) 
        self.txt1.move(x, y)

    # these are functions called by the button controls
    # changes all the show_things to False
    def dontShow(self):
        self.show_color = self.show_scheds = self.show_instr = False
    # sets show_color to be the only one to be true
    def showColors(self):
        self.dontShow()
        self.SchedData.readCSV( self.current_sched)
        self.show_color = True
        self.repaint()
    # sets show_sched to be the only one to be true
    def showScheds(self):
        self.dontShow()
        self.show_scheds = True
        self.repaint()
    # reads the name from command text input
    # if this name DNE, text output shows an error
    # if this name exists, Sched Data record info of this Sched
    def loadSched(self):
        name = self.txt0.text()
        self.dontShow()
        if not os.path.exists(name+'.csv'):
            self.txt1.setText("invalid sched")
        else:
            self.SchedData.readCSV(name)
            self.current_sched = name
            self.txt1.setText("complete")
        self.repaint()
    # reads the name from command text input
    # if this name DNE, text output shows an error
    # if this name exists, removes the corresponging csv file
    def deleteSched(self):
        name = self.txt0.text()
        self.dontShow()
        if not os.path.exists(name+'.csv'):
           self.txt1.setText("invalid sched")
        else:
            os.remove(name+'.csv')
            self.txt1.setText("complete")
        self.repaint()
    # reads the name from command text input
    # if this name already exists, text output shows an error
    # if this name DNE, creates and empty schedule csv file
    def newSched(self):
        name = self.txt0.text()
        self.dontShow()
        if os.path.exists(name +'.csv'):
            self.txt1.setText("sched name already taken")
        else:
            line0 = ""
            index = 0
            for mark in self.SchedData.data[0]:
                if index == 0:
                    line0 += mark
                else: 
                    line0 = line0 + ',' + mark
                index +=1
            line0 += '\n'
            self.SchedData.writeCSVLine(name, line0)
            for i in range(3):
                self.SchedData.writeCSVLine(name, '\n')
            self.txt1.setText("complete")
        self.repaint()

    # sets show_instr to be the only one to be true
    def showInstr(self):
        self.dontShow()
        self.show_instr = True
        self.repaint()

    # reads the command from text input
    # changes the schedule csv file of the currently opened sched
    def editSched(self):
        command = self.txt0.text()
        self.dontShow()
        if command.count(';') == 2:
            # mon;6am,7am,8am,9am,10am,11am,Noon;black
            name = self.current_sched
            days = command[0:command.index(';')].split(',')
            times = command[command.index(';')+1:command.rindex(';')].split(',')
            color = command[command.rindex(';')+1:]
            self.SchedEditor.markTimeIndex(name)
            for day in days:
                self.SchedEditor.markSchedule(name, day, times, color)
            self.txt1.setText("complete")
        elif command.count('*') == 1 and command.count(':') == 1:
            # *red:meaning
            name = self.current_sched
            color = command[1 :command.index(':')]
            meaning = command[command.index(':')+1:]
            self.SchedEditor.markMeaning(name, color, meaning)
        else:
            self.txt1.setText("invalid command")
        self.repaint()

    # this controls what is displayed
    def paintEvent(self, event):
        painter = QPainter(self)
        self.SchedDraw.drawSched(painter, self.SchedData)
        if self.show_color:

            data = self.SchedDraw.getColors(painter, self.SchedData)
            self.txt1.setText(data)
        if self.show_scheds:
            scheds = []
            for entry in os.listdir(os.getcwd()):
                if entry.find('.csv') > 0 :
                    scheds.append(entry[0:entry.index('.csv')])
            scheds.remove('empty')
            self.txt1.setText(str(scheds))
        if self.show_instr:
            self.txt1.setText("to change colors: mon,tue;6am,7am,8am,9am,10am,11am,Noon;black   to add meaning: *red:meaning")

# testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
# nice