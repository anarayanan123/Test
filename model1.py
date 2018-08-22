

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_TRACK_URI']='postgres://okvpxcvauaofmd:a57bf0462d83f843211915ad4c7b043a7883d1ef988b31c502860dac75d4406d@ec2-54-163-246-5.compute-1.amazonaws.com:5432/ddplart5et8pfb'

###config
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username