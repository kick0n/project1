import os
import requests, json
import jinja2

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

@app.route('/location/<city>/<location>')
def location(location, city):
    session['lat'] = db.execute("SELECT lat FROM locations WHERE zipcode = :location", {"location":location}).fetchone()
    session['longi'] = db.execute("SELECT longi FROM locations WHERE zipcode = :location", {"location":location}).fetchone()
    session['darkskyUrl'] = f"https://api.darksky.net/forecast/a3b2b1d3e4bfa52619ee61c7d29e83b1/{session['lat'][0]},{session['longi'][0]}"
    weather = requests.get(session['darkskyUrl']).json()
    #output = json.dumps(weather["currently"], indent = 2)
    output2 = weather["currently"]
    typeOf = type(output2)
    return render_template("location.html", Url=session['darkskyUrl'], location=location, city=city, typeOf=typeOf, outputs=output2, lat=float(session['lat'][0]), longi=float(session['longi'][0]))


@app.route('/search-results', methods = ["GET", "POST"])
def searchResults():
    if request.method=="POST":
        session['searchterm'] = request.form.get('searchterm').upper()

        """Lists all matches."""
        """should not use raw SQL queries with variable interpolation, but project assignment requires us not to use sqlalchemy methods"""
        session['locations'] = db.execute("SELECT * FROM locations WHERE city LIKE :searchterm OR zipcode LIKE :searchterm", {"searchterm":f"%{session['searchterm']}%"}).fetchall()
        return render_template("search-results.html", locations=session['locations'], searchterm=session['searchterm'])

    #return render_template("search-results.html", searchterm=session['searchterm'])

@app.route('/logout')
def logout():
    [session.pop(key) for key in list(session.keys()) if key != '_flashes']
    return "successfully logged out"

@app.route('/api/<int:zipcode>')
def api(zipcode):
    weather2 = requests.get("https://api.darksky.net/forecast/a3b2b1d3e4bfa52619ee61c7d29e83b1/29.76,-95.38").json()
    return render_template("api.html", zipcode=json.dumps(weather2["currently"], indent = 2))

