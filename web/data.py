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


class convert:
    # this is a dictionary for day abbreviations
    day_list = {
        'mon': 'Monday', 'tue': 'Tuesday', 'wed': 'Wednesday', 'thu': 'Thursday', 'fri': 'Friday',
        'sat': 'Saturday', 'sun': 'Sunday'
    }
    # this is a dictionary for 12hr conversion
    hr_list = {
        1: '1 am', 2: '2 am', 3: '3 am', 4: '4 am', 5: '5 am', 6: '6 am',
        7: '7 am', 8: '8 am', 9: '9 am', 10: '10 am', 11: '11 am', 12: '12 pm',
        13: '1 pm', 14: '2 pm', 15: '3 pm', 16: '4 pm', 17: '5 pm', 18: '6 pm',
        19: '7 pm', 20: '8 pm', 21: '9 pm', 22: '10 pm', 23: '11 pm', 24: '12 am'
    }

    def getDayName(self, abbrev):
        return self.day_list.get(abbrev)

    def getDayAbbrev(self, name):
        abbrev_list = list(self.day_list.keys())
        name_list = list(self.day_list.values())
        index = name_list.index(name)
        return abbrev_list[index]

    def get12Hr(self, num):
        return self.hr_list.get(num)

    def get24Hr(self, time):
        list24 = list(self.hr_list.keys())
        list12 = list(self.hr_list.values())
        index = list12.index(time)
        return list24[index]
