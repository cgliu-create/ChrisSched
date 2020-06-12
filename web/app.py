from flask import Flask, render_template, request
import os
from data import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


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


# given a name of a recorded week
# deletes all data associated with it
def deleteWeek(theweek):
    weeks = listWeekNames()
    if theweek not in weeks:
        raise Exception('INVALID WEEK')
    db.session.execute('''
    DELETE FROM hours WHERE id IN
        (SELECT hours.id FROM hours WHERE hours.day IN
            (SELECT days.id FROM days WHERE days.week IN
                (SELECT id FROM weeks WHERE weeks.week=(:week))))
     ''', {'week': theweek})
    db.session.execute('''
    DELETE FROM days WHERE id IN
        (SELECT days.id FROM days WHERE days.week IN
            (SELECT id FROM weeks WHERE weeks.week=(:week)))
    ''', {'week': theweek})
    db.session.execute('''
    DELETE FROM weeks WHERE weeks.week=(:week)
    ''', {'week': theweek})


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


# creates the tables
def createModel():
    db.create_all()


# web pages
@app.route("/")
def index():
    weeks = listWeekNames()
    return render_template("index.html", scheds=weeks)


@app.route("/scheds", methods=["POST"])
def scheds():
    # Get form information.
    week = request.form.get('schedule')
    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    daydata = []
    for day in days:
        data = getWeeKDayColors(week, day)
        daydata.append(data)
    days = map(getDayName, days)
    times = []
    for i in range(1, 25):
        times.append(getTwelveHr(i))
    return render_template("sched.html", headline=week, times=times, days=days, daydata=daydata)


# testing
if __name__ == '__main__':
    with app.app_context():
        printAll()
        deleteWeek('test')
        printAll()

# running web app
# if __name__ == '__main__':
#     app.run()
