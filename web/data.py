from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Week(db.Model):
    __tablename__ = "weeks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)


class Day(db.Model):
    __tablename__ = "days"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, db.ForeignKey("weeks.id"), nullable=False)


class Color(db.Model):
    __tablename__ = "colors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, db.ForeignKey("days.id"), nullable=False)
