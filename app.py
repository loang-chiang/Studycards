import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from flask_session import Session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

# configures application
app = Flask(__name__)

# configures session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flask_session_cache"
Session(app)

# configures the SQLite database
# includes USERS (id, username, hash), PACKAGES (user_id, name), FLASHCARDS (id, user_id, package_name, question, answer)
db = SQL("sqlite:///flashcards.db")


@app.after_request
def after_request(response):  # disables caching of the response
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def login_required(f):  # requires user to have logged in to access certain routes
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@login_required
def index():  # shows the page index
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():  # registers new users
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("error.html", message="Must provide username")
        elif not request.form.get("password"):
            return render_template("error.html", message="Must provide password")
        elif not request.form.get("confirmation"):
            return render_template("error.html", message="Must provide password a second time")
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("error.html", message="Passwords do not match")

        names = db.execute(  # queries database to check if username already exists
            "SELECT username FROM users WHERE username = ?",
            request.form.get("username"),)
        if names:
            return render_template("error.html", message="Username already exists")

        db.execute(  # inserts new user into the database
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            request.form.get("username"), generate_password_hash(request.form.get("password")),)

        # gets user back to login page
        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():  # logs users in
    session.clear()  # forgets any user_id

    if request.method == "POST":
        if not request.form.get("username"):  # check if username was submitted
            return render_template("error.html", message="Must provide username")
        elif not request.form.get("password"):  # check if password was submitted
            return render_template("error.html", message="Must provide password")

        # queries database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # checks if username exists and password are correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return render_template("error.html", message="Invalid username and/or password")

        session["user_id"] = rows[0]["id"]  # remembers which user has logged in
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():  # allows the user to log out of their account
    session.clear()
    return redirect("/")


@app.route("/<mode>")
@login_required
def choose_package(mode):  # shows all packages to choose from
    if mode == "study" or mode == "add" or mode == "edit":
        packages = db.execute("SELECT * FROM packages WHERE user_id = ?", session["user_id"])
        return render_template("choose_package.html", action=mode, packages=packages)
    else:
        # handles invalid mode
        abort(404)


@app.route("/study_cards", methods=["GET"])
@login_required
def study_cards():  # outputs the first question
    package_name = request.args.get("package_name")
    flashcards = db.execute("SELECT * FROM flashcards WHERE package_name = ?", package_name)
    length = len(flashcards)
    show_answer = False  # initially sets show_answer to false

    if flashcards:
        return render_template("study_cards.html", flashcards=flashcards, question=flashcards[0]['question'],
                               answer=flashcards[0]['answer'], package_name=package_name, current_question_index=0,
                               length=length, show_answer=show_answer)
    else:
        return render_template("no_cards.html")


@app.route("/next_question", methods=["POST"])
@login_required
def next_question():  # moves onto the next questions
    # gets necessary parameters
    package_name = request.form.get("package_name")
    flashcards = db.execute("SELECT * FROM flashcards WHERE package_name = ?", package_name)
    length = len(flashcards)
    current_question_index = int(request.form.get('current_question_index'))
    show_answer = False  # initially sets show_answer to false

    if current_question_index < len(flashcards) - 1:
        next_question_index = current_question_index + 1
        return render_template("study_cards.html", question=flashcards[next_question_index]['question'],
                               answer=flashcards[next_question_index]['answer'], package_name=package_name,
                               current_question_index=next_question_index, length=length, show_answer=show_answer)
    else:  # if there are no more flashcards left
        return render_template('no_more_cards.html')


@app.route("/show_answer", methods=["POST"])
@login_required
def show_answer():  # shows the answer to the question the user selected
    package_name = request.form.get("package_name")
    flashcards = db.execute("SELECT * FROM flashcards WHERE package_name = ?", package_name)
    length = len(flashcards)
    current_question_index = int(request.form.get('current_question_index'))

    show_answer = True  # shows answer

    # reload the page
    return render_template("study_cards.html", flashcards=flashcards, question=flashcards[current_question_index]['question'],
                           answer=flashcards[current_question_index]['answer'], package_name=package_name,
                           current_question_index=current_question_index, length=length, show_answer=show_answer)


@app.route("/add_cards", methods=["GET", "POST"])
@login_required
def add_cards():  # lets the user add flashcards to a package
    if request.method == "POST":
        package_name = request.form.get("package_name")
        question = request.form.get("question")
        answer = request.form.get("answer")

        if not answer or not question:
            return render_template("error.html", message="Can't leave any textfields blank!")

        # adds the new cards to the database using the question and answer from add_cards
        db.execute("INSERT INTO flashcards (user_id, package_name, question, answer) VALUES (?, ?, ?, ?)",
                   session["user_id"], package_name, question, answer)
        return render_template('add_cards.html', package_name=package_name)  # reloads the same page

    else:
        package_name = request.args.get("package_name")
        return render_template('add_cards.html', package_name=package_name)


@app.route("/add_package", methods=["POST"])
@login_required
def add_package():  # adds a new package to the packages table
    # checks if there's a package with that name already
    same_name_packages = db.execute("SELECT * FROM packages WHERE user_id = ? AND name = ?",
                                    session["user_id"], request.form.get("new_package_name"))
    if same_name_packages:
        return render_template("error.html", message="A package with that name already exists!")
    # if the user didn't write a name for the new package
    elif not request.form.get("new_package_name"):
        return render_template("error.html", message="Please provide a name for your package")

    # adds new package to database
    db.execute("INSERT INTO packages (user_id, name) VALUES (?, ?)",
               session["user_id"], request.form.get("new_package_name"))
    package_name = request.form.get("new_package_name")

    # goes back to package selector page
    packages = db.execute("SELECT * FROM packages WHERE user_id = ?", session["user_id"])
    return redirect(url_for('choose_package', mode='add'))  # calls choose_package with the add mode


@app.route("/edit_cards", methods=["GET"])
@login_required
def edit_cards():  # lets the user choose what card they want to edit
    package_name = request.args.get("package_name")
    flashcards = db.execute("SELECT * FROM flashcards WHERE user_id = ? AND package_name = ?",
                            session["user_id"], package_name)
    return render_template("edit_cards.html", flashcards=flashcards, package_name=package_name)


@app.route("/edit_card", methods=["GET", "POST"])
@login_required
def edit_card():  # lets the user edit the question and answer of a card
    if request.method == "POST":
        # gets necessary parameters
        flashcard_id = request.form.get("flashcard_id")
        package_name = request.form.get("package_name")
        question = request.form.get("question")
        answer = request.form.get("answer")

        if not answer or not question:
            return render_template("error.html", message="Can't leave any textfields blank!")

        db.execute("UPDATE flashcards SET question = ?, answer = ? WHERE user_id = ? AND id = ? AND package_name = ?",
                   question, answer, session["user_id"], flashcard_id, package_name)

        # redirects the user to the edit cards page
        flashcards = db.execute("SELECT * FROM flashcards WHERE user_id = ? AND package_name = ?",
                                session["user_id"], package_name)
        return render_template("edit_cards.html", flashcards=flashcards, package_name=package_name)

    else:
        # gets necessary parameters
        flashcard_id = request.args.get("flashcard_id")
        package_name = request.args.get("package_name")

        flashcard = db.execute("SELECT * FROM flashcards WHERE user_id = ? AND id = ? AND package_name = ?",
                               session["user_id"], flashcard_id, package_name)

        return render_template("edit_card.html", flashcard=flashcard[0], package_name=package_name)


@app.route("/delete_package", methods=["POST"])
@login_required
def delete_package():
    # selects the flashcards belonging to the current package
    package_name = request.form.get("package_name")

    flashcards = db.execute("SELECT * FROM flashcards WHERE user_id = ? AND package_name = ?",
                            session["user_id"], package_name)

    for flashcard in flashcards:  # deletes each flashcard inside the package
        db.execute("DELETE FROM flashcards WHERE user_id = ? AND id = ? AND package_name = ?",
                   session["user_id"], flashcard["id"], package_name)

    # deletes the package itself
    db.execute("DELETE FROM packages WHERE user_id = ? AND name = ?",
               session["user_id"], package_name)

    return redirect("/")  # takes user back to homepage


@app.route("/delete_card", methods=["POST"])
@login_required
def delete_card():  # lets the user delete a card's information
    # gets necessary parameters
    flashcard_id = request.form.get("flashcard_id")
    package_name = request.form.get("package_name")

    # deletes flashcard from database
    db.execute("DELETE FROM flashcards WHERE user_id = ? AND id = ? AND package_name = ?",
               session["user_id"], flashcard_id, package_name)

    # reloads the edit cards page
    flashcards = db.execute("SELECT * FROM flashcards WHERE user_id = ? AND package_name = ?",
                            session["user_id"], package_name)
    return render_template("edit_cards.html", flashcards=flashcards)