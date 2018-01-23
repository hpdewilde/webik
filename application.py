from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///trivia.db")

@app.route("/")
@login_required
def index():
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # test username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # test password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # test username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["password"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return render_template("play.html")

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    if request.method == "POST":

        # test username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # test password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

         # test password is the same
        elif request.form.get("password") != request.form.get("confirmpassword"):
            return apology("password doesn't match")

        # insert user into database with a hash value
        result = db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", username = request.form.get("username"), password = pwd_context.hash(request.form.get("password")))

        if not result:
            return apology("The Username was empty or the Username already exists")

        session["user_id"] = result

        # redirect user to home page
        return redirect(url_for("login"))

    else:
        return render_template("register.html")


@app.route("/play", methods = ["GET", "POST"])
def play():
    return render_template("play.html")


"""
@app.route("/question", methods = ["GET", "POST"])
def question():
    # user is on question page and selects an answer
    if request.method == "POST":
        # renders question.html again with new question
        # function located in helpers.py
        generate_question()

    if request.method == "GET":
        return render_template("question.html")

@app.route(“/create”, methods = ["GET", "POST"]
def create():
    # user clicks one of the buttons
    if request.method == "POST":
        # use HTML buttons with the ‘name’ and ‘value’ attributes
        if request.form[“choice”] == “create”:
            return render_template(“create_question.html”)
        elif request.form[“choice”] == “rate”:
            return render_template(“rate_question.html”)
    if request.method == "GET":
        return render_template(“create.html”)

@app.route(“/create_question”, methods = ["GET", "POST"]
def create_question():
    # user clicks on submit button
    if request.method == "POST":
        “””
        Store user entry in database
        “””
        return redirect(url_for(“create_question”))

    if request.method == "GET":
        return render_template(“create.html”)

@app.route(“leaderboards”, methods = ["GET"]
def leaderboards():
    render_template(“leaderboards.html”)

@app.route(“profile”, methods = ["GET", "POST"]
def profile():
    if request.method == "POST"
        # user wants to change profile information
        return render_template(“settings.html”)
    if request.method == "GET":
        return render_template(“profile.html”)
"""