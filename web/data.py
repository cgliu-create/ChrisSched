import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# table for weeks
class Week(db.Model):
    __tablename__ = 'weeks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    week = db.Column(db.String, nullable=False)

    # lists seven days for a new week and lists white for each day
    def createWeek(self):
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        hours = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        for day in days:
            new_day = Day(week=self.id, day=day)
            db.session.add(new_day)
            db.session.commit()
            for hour in hours:
                new_hour = Hour(day=new_day.id, hour=hour, color='white')
                db.session.add(new_hour)
                db.session.commit()


# table for days of weeks
class Day(db.Model):
    __tablename__ = 'days'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    week = db.Column(db.Integer, db.ForeignKey('weeks.id'), nullable=False)
    day = db.Column(db.String, nullable=False)


# table for hours and corresponding colors of days
class Hour(db.Model):
    __tablename__ = 'hours'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    day = db.Column(db.Integer, db.ForeignKey('days.id'), nullable=False)
    hour = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String, nullable=False)


# prints out everything stored in the tables
def printAll():
    print('WEEK DATA')
    for num, week in db.session.execute('SELECT * FROM weeks').fetchall():
        print(f'id {num}:week {week}')
    print('DAY DATA')
    for num, week, day in db.session.execute('SELECT * FROM days').fetchall():
        print(f'id {num}:week {week}:day {day}')
    print('HOUR DATA')
    for num, day, hour, color in db.session.execute('SELECT * FROM hours').fetchall():
        print(f'id {num}:day {day}:hour {hour}:color {color}')


# returns the names or recorded weeks
def listWeekNames():
    names = []
    for item in db.session.execute('SELECT * FROM weeks').fetchall():
        names.append(item.week)
    return names


# given a name that is not taken
# creates a new default week
def createNewWeek(theweek):
    weeks = listWeekNames()
    if theweek not in weeks:
        raise Exception('NAME TAKEN')
    new_week = Week(week=theweek)
    db.session.add(new_week)
    db.session.commit()
    new_week.createWeek()


# given the name of a recorded week and day
# returns the colors of the hours of that week day
def getWeeKDayColors(theweek, theday):
    weeks = listWeekNames()
    if theweek not in weeks:
        raise Exception('INVALID WEEK')
    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    if theday not in days:
        raise Exception('INVALID DAY')
    data = db.session.execute('''
    SELECT hours.hour, hours.color
    FROM weeks 
    JOIN days ON days.week = weeks.id
    JOIN hours ON hours.day = days.id
    WHERE weeks.week=(:week) AND days.day=(:day)
    ''', {'week': theweek, 'day': theday}).fetchall()
    return sorted(data)


# given the target week, day, and desired color
# changes the color of the day of the week to the desired color
def changeHourColor(theweek, theday, thehour, thecolor):
    weeks = listWeekNames()
    if theweek not in weeks:
        raise Exception('INVALID WEEK')
    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    if theday not in days:
        raise Exception('INVALID DAY')
    if thehour < 1 or thehour > 24:
        raise Exception('INVALID TIME')
    data = db.session.execute('''
    SELECT hours.color
    FROM weeks
    JOIN days ON days.week = weeks.id
    JOIN hours ON hours.day = days.id
    WHERE weeks.week=(:week) 
    AND days.day=(:day) 
    AND hours.hour=(:hour)
    ''', {'week': theweek, 'day': theday, 'hour': thehour}).fetchone()
    if data.color != thecolor:
        info = db.session.execute('''
        SELECT days.id FROM weeks JOIN days ON days.week = weeks.id
        WHERE weeks.week=(:week) AND days.day=(:day)''', {'week': theweek, 'day': theday}).fetchone()
        db.session.execute('UPDATE hours SET color=(:color) WHERE day=(:day) AND hour=(:hour)',
                           {'color': thecolor, 'day': info.id, 'hour': thehour})
        db.session.commit()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# creates the tables
def createModel():
    db.create_all()


# testing
if __name__ == '__main__':
    with app.app_context():
        # createModel()
        # test = Week(week='test')
        # db.session.add(test)
        # db.session.commit()
        # test.createWeek()
        # createNewWeek('example')
        # createNewWeek('test')
        # changeHourColor('test', 'mon', 1, 'blue')
        printAll()
        # print(getWeeKDayColors('test', 'mon'))
        # print(listWeekNames())


# this is a dictionary of color codes
def getColorCode(name):
    color_list = {
        'white': '#ffffff',
        'black': '#000000',
        'red': '#ff0000',
        'orange': '#ffb600',
        'yellow': '#fff700',
        'green': '#09ff00',
        'blue': '#0059ff',
        'purple': '#9d00ff',
        'pink': '#ff00e1',
        'darkred': '#a10000',
        'darkorange': '#bd8700',
        'darkyellow': '#c9c300',
        'darkgreen': '#07c900',
        'darkblue': '#003fb5',
        'darkpurple': '#7300ba',
        'darkpink': '#bd00a6'
    }
    return color_list.get(name)


# this is a dictionary for day abbreviations
def getDayName(abbrev):
    day_list = {
        'mon': 'Monday', 'tue': 'Tuesday', 'wed': 'Wednesday', 'thu': 'Thursday', 'fri': 'Friday',
        'sat': 'Saturday', 'sun': 'Sunday'
    }
    return day_list.get(abbrev)


# this is a dictionary for 12hr conversion
def getTwelveHr(num):
    hr_list = {
        1: '1 am', 2: '2 am', 3: '3 am', 4: '4 am', 5: '5 am', 6: '6 am',
        7: '7 am', 8: '8 am', 9: '9 am', 10: '10 am', 11: '11 am', 12: '12 pm',
        13: '1 pm', 14: '2 pm', 15: '3 pm', 16: '4 pm', 17: '5 pm', 18: '6 pm',
        19: '7 pm', 20: '8 pm', 21: '9 pm', 22: '10 pm', 23: '11 pm', 24: '12 am'
    }
    return hr_list.get(num)
