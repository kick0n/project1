import os
import requests, json

from flask import Flask, session, url_for, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))



@app.route('/')
def index():
    try:
        if session['logged_in'] :
            return redirect(url_for('search', username=session['username']))

    except KeyError:
        return render_template("index.html")

    return render_template("index.html")

@app.route('/signup', methods = ["GET","POST"])
def signup():


    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username != "" and password != "":
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username":username, "password":password})
            db.commit()
            return render_template("success.html", username=username, password=password)
        return render_template("error.html", message = "no blank fields allowed, please try again")


    return render_template("signup.html")

@app.route('/signin', methods = ["GET","POST"])
def signin():

    if request.method == "POST":

        session['username'] = request.form.get("username")
        session['password'] = request.form.get("password")
        session['logged_in'] = False

        if session['username'] != "" and session['password'] != "":
            if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username":session['username'], "password":session['password']}).rowcount == 0:
                return render_template("error.html", message="No such user registered.")

        else:
            return render_template("error.html", message="please try again.")

        #return profile(username)
        session['logged_in'] = True
        return redirect(url_for("search", username=session['username']))


    return render_template("signin.html")


@app.route('/search')
def search():
    return render_template("search.html")

@app.route('/location/<location>')
def location(location):
    return render_template("location.html", location=location)


@app.route('/search-results', methods = ["GET", "POST"])
def searchResults():
    if request.method=="POST":
        session['searchterm'] = request.form.get('searchterm')

        """Lists all matches."""
        session['locations'] = db.execute("SELECT * FROM locations WHERE id < 20").fetchall()
        return render_template("search-results.html", locations=session['locations'], searchterm=session['searchterm'])

    return render_template("search-results.html", searchterm=session['searchterm'])

@app.route('/logout')
def logout():
    [session.pop(key) for key in list(session.keys()) if key != '_flashes']
    return "successfully logged out"

@app.route('/api/<int:zipcode>')
def api(zipcode):
    return render_template("api.html", zipcode=zipcode)

