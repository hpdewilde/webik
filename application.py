from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from random import randint

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
    return render_template("logout_screen.html")


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
    if request.method == "GET":
        return render_template("play.html")


@app.route("/question", methods = ["GET", "POST"])
def question():
    if request.method == "POST":
        # check if answer was correct

        result = request.form.get("choice")
        question_id, user_answer = result.split(", ", 1)

        question_id = question_id.strip("(")
        user_answer = user_answer[1:-2]

        correct_answer = db.execute("SELECT correct_answer FROM questions WHERE id = :question_id", question_id=question_id)
        correct_answer = correct_answer[0]["correct_answer"]

        score = db.execute("SELECT score FROM users WHERE id = :id", id=session.get("user_id"))
        score = score[0]["score"]

        if user_answer == correct_answer:
            db.execute("UPDATE users SET score = score + 2 WHERE id = :id", id=session.get("user_id"))

        if user_answer != correct_answer and score > 0:
            db.execute("UPDATE users SET score = score - 1 WHERE id = :id", id=session.get("user_id"))

        return redirect(url_for("question"))

    if request.method == "GET":
        first_question_id = db.execute("SELECT min(id) FROM questions")
        first_question_id = first_question_id[0]["min(id)"]
        last_question_id = db.execute("SELECT max(id) FROM questions")
        last_question_id = last_question_id[0]["max(id)"]

        question_id = randint(first_question_id, last_question_id)
        row = db.execute("SELECT * FROM questions WHERE id = :id", id=question_id)

        question = row[0]['question']
        correct_answer = row[0]['correct_answer']
        wrong_answer1 = row[0]['wrong_answer1']
        wrong_answer2 = row[0]['wrong_answer2']
        wrong_answer3 = row[0]['wrong_answer3']

        r = randint(1,4)

        if r == 1:
            answer1 = correct_answer
            answer2 = wrong_answer1
            answer3 = wrong_answer2
            answer4 = wrong_answer3
        elif r == 2:
            answer2 = correct_answer
            answer1 = wrong_answer1
            answer3 = wrong_answer2
            answer4 = wrong_answer3
        elif r == 3:
            answer3 = correct_answer
            answer2 = wrong_answer1
            answer1 = wrong_answer2
            answer4 = wrong_answer3
        else:
            answer4 = correct_answer
            answer2 = wrong_answer1
            answer3 = wrong_answer2
            answer1 = wrong_answer3

        score = db.execute("SELECT score FROM users WHERE id = :id", id=session.get("user_id"))
        score = score[0]["score"]

        return render_template("question.html", question=question, answer1=answer1, answer2=answer2, answer3=answer3, answer4=answer4, question_id=question_id, score=score)


@app.route("/create", methods = ["GET", "POST"])
def create():

    # user clicks one of the buttons
    if request.method == "GET":
        return render_template("create.html")

@app.route("/create_question", methods = ["GET", "POST"])
def create_question():
    # user clicks on submit button
    if request.method == "POST":
        db.execute("INSERT INTO pending_questions (question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3) VALUES (:question, :correct_answer, :wrong_answer1, :wrong_answer2, :wrong_answer3)", question=request.form.get("question"), correct_answer=request.form.get("correct_answer"), wrong_answer1=request.form.get("wrong_answer1"), wrong_answer2=request.form.get("wrong_answer2"), wrong_answer3=request.form.get("wrong_answer3"))
        return redirect(url_for("create_question"))

    if request.method == "GET":
        return render_template("create_question.html")

@app.route("/rate_question", methods = ["GET", "POST"])
def rate_question():
    # user clicks on submit button
    if request.method == "POST":
        """
        Store user entry in database
        """
        return redirect(url_for("rate_question"))

    if request.method == "GET":
        return render_template("rate_question.html")


"""
@app.route(“leaderboards”, methods = ["GET"]
def leaderboards():
    render_template(“leaderboards.html”)
"""

@app.route("/profile", methods = ["GET", "POST"])
def profile():
    if request.method == "GET":
        rows = db.execute("SELECT * FROM users WHERE id = :id", id=session.get("user_id"))
        username = rows[0]['username']
        return render_template("profile.html", username=username)

@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    if request.method == "POST":
        if request.form["new_pw1"] == "" or request.form["new_pw2"] == "":
            return apology("Must provide password twice")
        elif request.form["new_pw1"] != request.form["new_pw2"]:
            return apology("Passwords do not match")
        else:
            new_pw = request.form["new_pw1"]

        db.execute("UPDATE users SET password = :password WHERE id = :id", password=pwd_context.hash(new_pw), id=session.get("user_id"))

        return redirect(url_for("profile"))

    else:
        return render_template("changepassword.html")

