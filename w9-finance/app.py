import os
import re
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session['user_id']
    stock_portfolios = []
    current_cash = float(db.execute("SELECT cash FROM users WHERE id = ?;",
                                    user_id)[0]['cash'])
    total_assets = current_cash
    stock_companys = db.execute("SELECT DISTINCT symbol FROM portfolio WHERE user_id = ?;",
                                user_id)

    for company in stock_companys:

        total_shares = db.execute("SELECT sum(shares) AS 'shares' FROM portfolio WHERE user_id = ? AND symbol = ?;",
                                  user_id, company['symbol'])[0]['shares']

        company_portfolio = {
            "symbol": company['symbol'],
            "company": lookup(company['symbol'])['name'],
            "shares": int(total_shares),
            "price": float(lookup(company['symbol'])['price']),
            "total": int(total_shares) * float(lookup(company['symbol'])['price'])
        }

        total_assets += int(total_shares) * float(lookup(company['symbol'])['price'])
        stock_portfolios.append(company_portfolio)

    return render_template("index.html",
                           stock_portfolios=stock_portfolios,
                           current_cash=current_cash,
                           total_assets=total_assets)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":

        # check for if special character exist
        quote = lookup(request.form.get("symbol"))
        non_number = re.compile(r'\D')
        invalid_shares = non_number.findall(request.form.get("shares"))

        if request.form.get("shares") == None or invalid_shares != [] or quote == None or int(request.form.get("shares")) < 1:
            return apology("invalid symbol", 400)

        user_id = session['user_id']
        shares = int(request.form.get("shares"))
        current_price = float(lookup(request.form.get("symbol"))['price'])
        cash = float(db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]['cash'])

        balance = cash - current_price * shares

        if balance < 0:
            return apology("can't afford", 400)

        symbol = lookup(request.form.get("symbol"))['symbol']

        # update users table
        db.execute("UPDATE users SET cash = ? WHERE id = ?;",
                   balance, user_id)

        # insert into portfolio table
        db.execute("INSERT INTO portfolio (user_id, symbol, shares, price, time) VALUES (?, ?, ?, ?, ?);",
                   user_id, symbol, shares, current_price, datetime.today())

        ###### SHOW popup ######
        flash("Bought!")
        return redirect("/")
    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session['user_id']
    records = db.execute("SELECT * FROM portfolio WHERE user_id = ?;", user_id)
    print(records)
    return render_template("history.html", records=records)


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

        # check for if special character exist
        special_char = re.compile(r'[;<> {}()-.]')
        spec_in_name = special_char.findall(request.form.get("username"))
        spec_in_psw = special_char.findall(request.form.get("password"))

        if spec_in_name != [] or spec_in_psw != []:
            return apology("non allowed character", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

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
        quote = lookup(request.form.get("symbol"))
        if quote == None:
            return apology("invalid symbol", 400)
        else:
            return render_template("quote.html", method="POST", quote=quote)
    return render_template("quote.html", method="GET")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # check for if miss value
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return apology("must provide every values", 400)

        # check for if special character exist
        special_char = re.compile(r'[;<> {}()-.]')
        spec_in_name = special_char.findall(request.form.get("username"))
        spec_in_psw = special_char.findall(request.form.get("password"))
        spec_in_com = special_char.findall(request.form.get("confirmation"))

        if spec_in_name != [] or spec_in_psw != [] or spec_in_com != []:
            return apology("non allowed character", 403)

        # check for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 0:
            return apology("username has been used", 400)

        # check for password
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("password are not matched", 400)

        if len(request.form.get("password")) < 6 or len(request.form.get("password")) > 12:
            return apology("6-12 characters in password is required", 403)

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?);",
                   request.form.get("username"),
                   generate_password_hash(request.form.get("password")))
        return redirect("/")

    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session['user_id']
    stock_companys = db.execute("SELECT DISTINCT symbol FROM portfolio WHERE user_id = ?;",
                                user_id)

    if request.method == "POST":

        symbol_req = request.form.get("symbol")
        quote = lookup(symbol_req)

        shares_req = int(request.form.get("shares"))
        non_number = re.compile(r'\D')
        invalid_shares = non_number.findall(request.form.get("shares"))

        if quote == None or invalid_shares != [] or shares_req < 1:
            return apology("invalid Value", 400)

        own_shares = int(db.execute("SELECT sum(shares) AS 'shares' FROM portfolio WHERE user_id = ? AND symbol = ?;",
                                    user_id, symbol_req)[0]['shares'])

        if shares_req > own_shares:
            return apology("Too many shares", 400)

        current_price = float(lookup(symbol_req)['price'])
        total_cash = float(db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]['cash']) + current_price * shares_req

        # update user cash
        db.execute("UPDATE users SET cash = ? WHERE id = ?;",
                   total_cash, user_id)

        # insert portfolio shares
        db.execute("INSERT INTO portfolio (user_id, symbol, shares, price, time) VALUES (?, ?, ?, ?, ?);",
                   user_id, symbol_req, -1 * shares_req, current_price, datetime.today())
        flash("Sold!")
        return redirect("/")

    return render_template("sell.html", stock_companys=stock_companys)


# export API_KEY=pk_141b863072fd4b41b4a3ca8323e22806