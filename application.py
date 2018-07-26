import os
import requests, json

from flask import Flask, session, url_for, render_template, request
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
    return render_template("index.html")

@app.route('/signin', methods = ["GET","POST"])
def signin():

    if request.method == "POST":

        myusername = request.form.get("myusername")
        mypassword = request.form.get("mypassword")

        return render_template("success.html", username=myusername, password=mypassword)

    return render_template("signin.html")

@app.route('/signup', methods = ["GET","POST"])
def signup():


    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")


        return render_template("success.html", username=username, password=password)

    return render_template("signup.html")



@app.route('/user/<username>')
def profile(username):
    return '{}\'s profile'.format(username)


@app.route('/error')
def error():
    return "This is an error page."

@app.route('/success')
def success(username, email, password):
    return render_template("success.html", username=username, email=email, password=password)