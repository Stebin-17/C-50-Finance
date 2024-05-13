import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session,url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from helpers import apology, login_required, lookup, usd, format_stock_prices

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

#serializers for the tokens in mail sending
app.secret_key = 'django-insecure-m07p(gc-q3xs!0%_q5o$r%l$=ejsu52uuyn$nm_^3o#&9cv1am'
serializer = URLSafeTimedSerializer(app.secret_key)

# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = '74.125.143.108'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '**********@gmail.com'
app.config['MAIL_PASSWORD'] = 'pgu************yak'

mail = Mail(app)


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

    stock_data = db.execute(
        "SELECT symbol, SUM(shares) shares, price, SUM(total_price) total_price FROM \
        stocks WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", session["user_id"])

    user_data = db.execute(
        "SELECT cash FROM users WHERE id = ?", session["user_id"])
    account_data = db.execute(
        "SELECT SUM(total_price) paid FROM stocks WHERE user_id = ?", session["user_id"])
    total_cash = user_data[0]['cash']

    if account_data[0]['paid']:
        total_cash = account_data[0]['paid'] + user_data[0]['cash']

    stock_data = format_stock_prices(stock_data)

    return render_template("index.html",
                           stocks=stock_data,
                           cash=usd(user_data[0]['cash']),
                           total=usd(total_cash))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("must provide symbol")
        if not shares:
            return apology("must provide shares")
        if not shares.isdigit():
            return apology("num of shares not valid")

        shares = int(float(shares))

        if shares <= 0:
            return apology("num of shares not valid")

        stock_data = lookup(symbol)

        if not stock_data:
            return apology("Symbol not found")

        user_data = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"])

        total_price = stock_data['price'] * shares
        cash = user_data[0]["cash"] - total_price

        if user_data[0]["cash"] < total_price:
            return apology("Not enough cash to complete the purchase")

        db.execute(
            "INSERT INTO stocks (user_id, symbol, price, shares, total_price) \
            VALUES (?, ?, ?, ?, ?)",
            session["user_id"],
            stock_data['symbol'],
            stock_data['price'],
            shares, total_price
        )
        db.execute("UPDATE users SET cash = ? WHERE id = ?",
                   cash, session["user_id"])

        flash("Purchase completed successfully!")

        return redirect("/")

    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    stock_data = db.execute(
        "SELECT symbol, shares, price, total_price, date_created \
         FROM stocks WHERE user_id = ?", session["user_id"])

    stock_data = format_stock_prices(stock_data)

    return render_template("history.html", stocks=stock_data)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("must provide username")

        # Ensure password was submitted
        if not password:
            return apology("must provide password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", username
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], password
        ):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
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
    """Get stock quote"""

    if request.method == "POST":
        symbol = request.form.get("symbol")

        if not symbol:
            return apology("must provide a symbol")

        quote_data = lookup(symbol)

        if quote_data:
            return render_template("quoted.html",
                                   price=usd(quote_data['price']),
                                   symbol=quote_data['symbol'])

        return apology("Symbol not found")

    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("must provide username")
        if not password:
            return apology("must provide password")
        if not confirmation:
            return apology("must confirm password")
        if password != confirmation:
            return apology("password and confirmation do not match")
        
        if email =="" or email is None:
            return apology("must provide email")


        existing_users = db.execute(
            "SELECT id FROM users WHERE username = ?", username
        )

        if len(existing_users) >= 1:
            return apology("Username already exists")

        password_hash = generate_password_hash(password)

        db.execute(
            "INSERT INTO users (username, hash ,email) VALUES (?, ? , ?)", username, password_hash,email
        )

        return redirect("/")

    return render_template("register.html")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add cash to account"""

    if request.method == "POST":
        cash = request.form.get("cash")
        if not cash:
            return apology("must provide cash")

        user_data = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"])
        total_cash = int(cash) + user_data[0]['cash']

        db.execute("UPDATE users SET cash = ? WHERE id = ?",
                   total_cash, session["user_id"])

        flash("Cash added successfully!")

        return redirect("/")

    return render_template("add.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("must provide symbol")
        if not shares:
            return apology("must provide shares")
        if int(shares) <= 0:
            return apology("num of shares not valid")

        stock_data = lookup(symbol)

        if not stock_data:
            return apology("Symbol not found")

        user_data = db.execute(
            "SELECT SUM(s.shares) shares, SUM(s.total_price) price, u.cash FROM users u \
            inner join stocks s on s.user_id = u.id WHERE u.id = ? \
            and symbol = ? GROUP BY s.symbol, u.cash",
            session["user_id"],
            symbol)

        if not user_data:
            return apology("Symbol not found")

        shares = int(shares)
        if user_data[0]['shares'] < shares:
            return apology("Not enough shares to complete the sale")

        total_price = stock_data['price'] * shares
        new_cash = total_price + user_data[0]['cash']

        db.execute(
            "INSERT INTO stocks (user_id, symbol, price, shares, total_price) \
            VALUES (?, ?, ?, ?, ?)",
            session["user_id"],
            stock_data['symbol'],
            stock_data['price'],
            shares * -1,
            total_price * -1
        )
        db.execute("UPDATE users SET cash = ? WHERE id = ?",
                   new_cash, session["user_id"])

        flash("Sale completed successfully!")

        return redirect("/")

    user_stocks = db.execute(
        "SELECT DISTINCT symbol FROM stocks s WHERE s.user_id = ?", session["user_id"])

    return render_template("sell.html", stocks=user_stocks)



# Function to send the password reset email
def send_password_reset_email(email, token):
    msg = Message('Password Reset Request', sender='luxshtech258@gmail.com', recipients=[email])
    msg.body = f"To reset your password, visit the following link:\n{url_for('reset_password', token=token, _external=True)}"
    mail.send(msg)

# Route for requesting a password reset
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")

        # Check if the email exists in the database
        user = db.execute("SELECT * FROM users WHERE email = ?", email)
        print(user)

        if user:
            user = user[0]  # Get the first element of the list
            # Generate a unique token
            token = serializer.dumps(user["id"], salt="reset-password")

            print(user)
            print(token)

            # Send the password reset email to the entered email address
            send_password_reset_email(email, token)

            flash("An email has been sent with instructions to reset your password.")
            return redirect(url_for("login"))

        flash("Email not found. Please enter a valid email address.")
    
    return render_template("forgot_password.html")

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        user_id = serializer.loads(token, salt="reset-password", max_age=3600)  # Token expires after 1 hour
    except:
        flash("The reset password link is invalid or has expired.")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not password:
            return apology("must provide password")
        if not confirmation:
            return apology("must confirm password")

        if password != confirmation:
            flash("Password and confirmation do not match.")
        else:
            # Update the user's password in the database
            hashed_password = generate_password_hash(password)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", hashed_password, user_id)
            flash("Your password has been successfully reset. Please log in with your new password.")
            return redirect(url_for("login"))
    
    return render_template("reset_password.html", token=token)

# Handling the route without the token parameter
@app.route("/reset_password/", methods=["GET", "POST"])
def reset_password_without_token():
    flash("Invalid reset password link.")
    return redirect(url_for("forgot_password"))


if __name__ == "__main__":
    app.run(debug=True)

