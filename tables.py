###removing SQL lite 
#from cs50 import SQL
import os
from flask_sqlalchemy import SQLAlchemy 

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

######SSQLAlchemy 
###if you do not have SQL Alchemy you will get this warning 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
###config the DB to the environment DB URL
app.config['SQLALCHEMY_TRACK_URI'] = os.environ['DATABASE_URL'] 
###config
db = SQLAlchemy(app)
class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique = True)
    hash = db.Column(db.String(80))
    cash = db.Column(db.Float, default = 10000.00)
class Portfolio(db.Model):
    pid = db.Column(db.Integer, primary_key = True)
    TransDate = db.Column(db.DateTime)
    User = db.Column(db.String(80))
    Stock = db.Column(db.String(80))
    Price = db.Column(db.Float)
    Num = db.Column(db.Integer)