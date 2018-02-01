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

    
@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    
    if request.method == "POST":

        # test old password was submitted
        if not request.form.get("password"):
            return apology("must provide old password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session['user_id'])

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["password"]): 
            return apology("old password invalid")

        # test password 1 was submitted
        elif not request.form.get("new_pw1"):
            return apology("must provide password")

        # test password 2 was submitted
        elif not request.form.get("new_pw2"):
            return apology("must provide password")

        # store the hash of the password and not the actual password that was typed in
        password_unhashed = request.form.get("new_pw1")
        password_hashed = pwd_context.hash(password_unhashed)

         # who is logged in?
        session["user_id"] = rows[0]["id"]

        # updating the password in db
        result = db.execute("UPDATE users SET password=:password WHERE id = :id", password=password_hashed, id=session['user_id'])
        if not result:
            return apology("shoot, somehow it didn't work")

        # redirect user to profile page
        return render_template("profile.html")

    else:
        return render_template("changepassword.html")
    
    
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
        # get user answer choice and store in variable
        result = request.form.get("choice")
        question_id, user_answer = result.split(", ", 1)

        # strip variables from useless characters
        question_id = question_id.strip("(")
        user_answer = user_answer[1:-2]

        # find correct answer in database
        correct_answer = db.execute("SELECT correct_answer FROM questions WHERE id = :question_id", question_id=question_id)
        correct_answer = correct_answer[0]["correct_answer"]

        # user answer correct
        if user_answer == correct_answer:
            # update 'correct' column in db
            db.execute("UPDATE users SET correct = correct + 1 WHERE id = :id", id=session.get("user_id"))
                
            # get new correct and wrong scores from db
            row = db.execute("SELECT correct, wrong FROM users WHERE id = :id", id=session.get("user_id"))
            correct = row[0]["correct"]
            wrong = row[0]["wrong"]

            # calculate score
            score = round((correct * 2 - wrong) * (correct / (correct + wrong)) * 100)
            # update score
            db.execute("UPDATE users SET score = :score WHERE id = :id", score=score, id=session.get("user_id"))

        if user_answer != correct_answer:
            # update 'wrong' column in db
            db.execute("UPDATE users SET wrong = wrong + 1 WHERE id = :id", id=session.get("user_id"))

            # get new correct and wrong scores from db
            row = db.execute("SELECT correct, wrong FROM users WHERE id = :id", id=session.get("user_id"))
            correct = row[0]["correct"]
            wrong = row[0]["wrong"]

            # calculate score
            score = round((correct * 2 - wrong) * (correct / (correct + wrong)) * 100)
            # update score
            db.execute("UPDATE users SET score = :score WHERE id = :id", score=score, id=session.get("user_id"))
            
        return redirect(url_for("question"))

    if request.method == "GET":
        # find id's from first and last question in db
        first_question_id = db.execute("SELECT min(id) FROM questions")
        first_question_id = first_question_id[0]["min(id)"]
        last_question_id = db.execute("SELECT max(id) FROM questions")
        last_question_id = last_question_id[0]["max(id)"]

        # select random question from all question id's
        question_id = randint(first_question_id, last_question_id)
        row = db.execute("SELECT * FROM questions WHERE id = :id", id=question_id)

        # store question/answers in variables
        question = row[0]['question']
        correct_answer = row[0]['correct_answer']
        wrong_answer1 = row[0]['wrong_answer1']
        wrong_answer2 = row[0]['wrong_answer2']
        wrong_answer3 = row[0]['wrong_answer3']

        # randomize answer location
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

        # get score from db
        score = db.execute("SELECT score FROM users WHERE id = :id", id=session.get("user_id"))
        score = score[0]["score"]

        return render_template("question.html", question=question, answer1=answer1, answer2=answer2, answer3=answer3, answer4=answer4, question_id=question_id, score=score)

@app.route("/create", methods = ["GET", "POST"])
def create():
    # user clicks on submit button
    if request.method == "POST":
        # insert user entry into db
        db.execute("INSERT INTO pending_questions (question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3) VALUES (:question, :correct_answer, :wrong_answer1, :wrong_answer2, :wrong_answer3)", question=request.form.get("question"), correct_answer=request.form.get("correct_answer"), wrong_answer1=request.form.get("wrong_answer1"), wrong_answer2=request.form.get("wrong_answer2"), wrong_answer3=request.form.get("wrong_answer3"))
        return redirect(url_for("create"))

    if request.method == "GET":
        return render_template("create.html")

@app.route("/leaderboard", methods = ["GET"])
def leaderboard():
    if request.method == "GET":
        # get scores from db and order them
        scores = db.execute("SELECT username, score FROM users ORDER BY score DESC")
        # get number of correctlty answered questions from db and order them
        questions_correct = db.execute("SELECT username, correct FROM users ORDER BY correct DESC")

        return render_template("leaderboard.html", scores=scores, questions_correct=questions_correct)

@app.route("/profile", methods = ["GET", "POST"])
def profile():
    if request.method == "GET":
        row = db.execute("SELECT * FROM users WHERE id = :id", id=session.get("user_id"))

        # store all profile info in variables
        username = row[0]["username"]
        score = row[0]["score"]
        correct = row[0]["correct"]
        wrong = row[0]["wrong"]
        questions_answered = correct + wrong
        
        if questions_answered == 0:
            pct_correct = '-'
            pct_wrong = '-'
        else:
            pct_correct = round(correct / questions_answered * 100, 2)
            pct_wrong = round(wrong / questions_answered * 100, 2)

        return render_template("profile.html", username=username, score=score, correct=correct, wrong=wrong, questions_answered=questions_answered, pct_correct=pct_correct, pct_wrong=pct_wrong)

  

