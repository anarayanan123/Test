
###removing SQL lite 
#from cs50 import SQL
import os
import datetime 
from flask_sqlalchemy import SQLAlchemy

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd



# Configure application
app = Flask(__name__)

###############################SSQLAlchemy 
###if you do not have SQL Alchemy you will get this warning 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
###config the DB to the environment DB URL
app.config['SQLALCHEMY_TRACK_URI'] = 'postgres://okvpxcvauaofmd:a57bf0462d83f843211915ad4c7b043a7883d1ef988b31c502860dac75d4406d@ec2-54-163-246-5.compute-1.amazonaws.com:5432/ddplart5et8pfb'
###config
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique = True)
    hash = db.Column(db.String(200))
    cash = db.Column(db.Float, default = 10000.00)



class Portfolio(db.Model):
    pid = db.Column(db.Integer, primary_key = True)
    TransDate = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    User = db.Column(db.String(80))
    Stock = db.Column(db.String(80))
    Price = db.Column(db.Float)
    Num = db.Column(db.Integer)



# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

###############################SSQLAlchemy 
# Configure CS50 Library to use SQLite database
###removing SQL lite 
#db = SQL("sqlite:///finance.db")

@app.route("/", methods = ["GET"])
@login_required
def index():
    user = session.get("user_id")
###############################SSQLAlchemy
    ##rows = db.execute("Select Stock, sum(Num) as Number from portfolio where User = :User group by Stock having sum(Num) > 0", User = session.get("user_id"))
    rows = Portfolio.query(Portfolio.Stock, func.sum(Portfolio.Num).label('Number')).group_by(Portfolio.Stock).filter(Portfolio.User.in_(user))
    stocks = rows
    currentprices = []
    # get current price for each group (ie AAPL) with help from lookup function (which remember, returns a dict)
    for stock in stocks:
        symbol = str(stock["Stock"])
        currentprices.append(usd(round((lookup(symbol)['price']),2)))
    totals = []
    totals1 = []
    # get current price for each group (ie AAPL) with help from lookup function (which remember, returns a dict)
    for stock in stocks:
        symbol = str(stock["Stock"])
        p = round(float(lookup(symbol)['price']),2)
        n = round(float(stock["Number"]),2)
        t = round(p*n,2)
        totals.append(usd(t))
        totals1.append(t)
###############################SSQLAlchemy 
    #get cash
    ##rows = db.execute("Select cash from users where id = :User", User = session.get("user_id"))
    rows = Users.query(Users.cash).filter(Users.id.in_(user)) 
    cash = round(float(rows[0]["cash"]),2)
    gotal = round(sum(totals1)+cash,2)


    return render_template("index.html", stocks = stocks, prices = currentprices, totals = totals, cash = usd(cash), gotal = usd(gotal))




@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        # Ensure buy order
        if not request.form.get("symbol"):
            return apology("must provide valid order info", 400)

        # Ensure buy order
        elif not request.form.get("shares"):
            return apology("must provide valid order info", 400)

        # Ensure stock is balid else display an apology
        elif lookup(request.form.get("symbol")) == None:
            return apology("invalid stock", 400)

        try:
            shares = int(request.form.get("shares"))
        except ValueError:
            return apology("shares must be a positive integer", 400)


        # Check if its negative
        #elif int(request.form.get("shares")) < 1:
        #    return apology("must provide valid order info", 400)


        # Add stock to user's portfolio

        stock = lookup(request.form.get("symbol"))['name']
        num = request.form.get("shares")
        price = (lookup(request.form.get("symbol"))['price'])
        user = session.get("user_id")
        amount = (float(request.form.get("shares")) * float(lookup(request.form.get("symbol"))['price']))

        # check if they have enough cash
        # Query database for username
  
###############################SSQLAlchemy 
    ##rows = db.execute("Select Stock, sum(Num) as Number from portfolio where User = :User group by Stock having sum(Num) > 0", User = session.get("user_id"))   
        rows = Users.query.all().filter(Users.id.in_(user)) 
        #rows = db.execute("SELECT * FROM users WHERE id = :id", id = session.get("user_id"))
        rows = float(rows[0]["cash"])


        # Add trasnaction to portfolio if user has enough cash
        if (float(num) * float(price)) <= rows:
###############################SSQLAlchemy 
            #result = db.execute("INSERT INTO portfolio (User, Stock, Price, Num) VALUES(:User, :Stock, :Price, :Num)", User = session.get("user_id"), Stock = stock, Price = usd(price), Num = num)
            tx_user = Portfolio(session.get("user_id"))
            tx_stock = Portfolio(stock)
            tx_price = Portfolio(usd(price))
            tx_num = Portfolio(num)
            db.session.add(tx_user, tx_stock, tx_price, tx_num)
            result = db.session.commit()
            if not result:
               return apology("TX did not record", 400)
#         Update cash



            result = db.execute("UPDATE users set cash = cash - :amount where id = :User ", User = session.get("user_id"), amount = amount)
          


            if not result:
               return apology("Cash did not update", 400)

         # Redirect user to home page
            return redirect("/")
        else:

            return apology("Not enough Cash", 403)
    else:
        return render_template("buy.html")



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    user = session.get("user_id")
###############################SSQLAlchemy 
    rows = db.execute("Select TransDate as Date, Stock, Price, case when Num < 0 then 'Sell' else 'Buy' end as Type, Num as Quantity from portfolio where User = :User order by Date asc", User = session.get("user_id"))


    return render_template("hist.html", rows = rows)





@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
  ###############################SSQLAlchemy 



        ##rows = db.execute("SELECT * FROM users WHERE username = :username",
                          #username=request.form.get("username"))

        rows = Users.query.filter(Users.username.in_(request.form.get("username"))).all()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":

        # Ensure username quote
        if not request.form.get("symbol"):
            return apology("must provide quote", 400)

        # Ensure stock is balid else display an apology
        elif lookup(request.form.get("symbol")) == None:
            return apology("invalid stock", 400)

        # display symbol
        quote = lookup(request.form.get("symbol"))['name']
        quote1 = usd(lookup(request.form.get("symbol"))['price'])
        quote2 = lookup(request.form.get("symbol"))['symbol']

        return render_template("quote1.html", name1 = quote, name2 = quote2, name3 = quote1)

    else:
        return render_template("quote.html")




@app.route("/register", methods=["GET", "POST"])
def register():

    """Forget any user id"""
    session.clear()

    """Register user"""

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Make sure password and confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password does not match", 400)


        # add username and pw to the DB

        hash = generate_password_hash(request.form.get("password"))
        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username=request.form.get("username"), hash=hash)

        if not result:
           return apology("username already exists", 400)

        # Log user in
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))


        session["user_id"] = rows[0]["id"]


        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")




@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""


    if request.method == "POST":
        symbol = request.form.get("symbol")
        rows = db.execute("Select Stock, sum(Num) as Number from portfolio where User = :User and Stock = :symbol group by Stock", User = session.get("user_id"), symbol = symbol)
        num = rows[0]["Number"]
        num1 = int(request.form.get("number"))
        # render apology if the user fails to select a stock
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)

        # Ensure number of shares
        elif not request.form.get("number"):
            return apology("must provide number", 403)

        # Ensure if users owns the number of stocks
        elif num1 > num:
            return apology("not enough stock", 403)

        #log sale as a negative quant of shares at the current slide


        stock = symbol

        price = float(lookup(stock)['price'])


        num = -num1
        result = db.execute("INSERT INTO portfolio (User, Stock, Price, Num) VALUES(:User, :Stock, :Price, :Num)", User = session.get("user_id"), Stock = stock, Price = price, Num = num)


        #update the user cash
        amount = round(num*price,2)
        result = db.execute("UPDATE users set cash = cash - :amount where id = :User ", User = session.get("user_id"), amount = amount)


#        if not result:
#           return apology("username already exists", 403)

        # Log user in
        # Query database for username
#        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))


 #       session["user_id"] = rows[0]["id"]


        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        rows = db.execute("Select Stock, sum(Num) as Number from portfolio where User = :User group by Stock", User = session.get("user_id"))
        stockss = rows
        stocksss = []
        for stock in stockss:
            symbol = str(stock["Stock"])
            stocksss.append(symbol)

        return render_template("sell.html", x = stocksss)




    # get current price for each group (ie AAPL) with help from lookup function (which remember, returns a dict)




def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

