

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_TRACK_URI']='postgres://hvfoqbqasxxmco:6c30c1c60c445054f9b1afdf9613fddf06331927a4a9c526c63d60910dc93f2c@ec2-54-83-3-101.compute-1.amazonaws.com:5432/dbaeatcsu7fc1p'

###config
db = SQLAlchemy()
db.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username