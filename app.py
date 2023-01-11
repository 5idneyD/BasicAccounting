from flask import Flask, render_template, request, redirect, url_for, session, g
from flask_migrate import Migrate
import flask_login
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)

# Current files path to create absolute path
basedir = os.path.abspath(os.path.dirname(__file__))


# Using sqlite3 db
# Secret key changes for each new session; improves security
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + \
    os.path.join(basedir, "./database/database.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = False
app.config['SECRET_KEY'] = os.urandom(12).hex()
app.secret_key = os.urandom(12).hex()


db = SQLAlchemy(app)


class Companies(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    company = db.Column(db.String(40))
    admin_email = db.Column(db.String(40))
    admin_password = db.Column(db.String(40))


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    company = db.Column(db.String(40))
    username = db.Column(db.String(40))
    email = db.Column(db.String(40))
    password = db.Column(db.String(40))
    admin = db.Column(db.Boolean)

class ChartOfAccounts(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    company = db.Column(db.String(40))
    nominal = db.Column(db.Integer, nullable=False)
    account_name = db.Column(db.String(40))


with app.app_context():
    db.create_all()


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)
    session.modified = True


@app.route("/")
def index():
    return render_template("index.html", message="Hello Flask")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        users = db.session.execute(
            "SELECT * FROM Users WHERE email='" + email + "';")
        # each user contains id, company, email & password
        for user in users:
            print(user)
            if user["password"] == password:
                session[email] = os.urandom(12).hex()
                if user["admin"] == True:
                    # return redirect(f"/admin/{user['company']}")
                    return redirect(url_for("admin", company=user['company']))
                else:
                    return redirect(url_for("dashboard", company=user['company'],
                                            email=email, username=user['username'], session_key=session[email]))

    return render_template("login.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():

    if request.method == "POST":
        company_name = request.form["company"]
        company_email = request.form["email"]
        company_password = request.form["password"]

        new_company = Companies(
            company=company_name, admin_email=company_email, admin_password=company_password)
        db.session.add(new_company)
        new_admin = Users(company=company_name, username=company_email,
                          password=company_password, admin=True)
        db.session.add(new_admin)
        db.session.commit()

        return redirect(f"/admin/{company_name}")
    return render_template("signup.html")


@app.route("/admin/<company>", methods=["POST", "GET"])
def admin(company):

    if request.method == "POST":
        new_name = request.form["name"]
        new_email = request.form["email"]
        new_password = request.form["password"]

        new_user = Users(company=company, username=new_name, email=new_email,
                         password=new_password, admin=False)
        db.session.add(new_user)
        db.session.commit()

    return render_template("admin.html", company=company)


@app.route("/<company>/<email>/<username>/<session_key>/dashboard", methods=["POST", "GET"])
def dashboard(company, email, username, session_key):
    
    try:
        if session[email] == session_key:
            return render_template("dashboard.html", company=company, email=email, username=username, session_sey=session_key)
        else:
            return redirect(url_for("login"))
    except KeyError:
        # Username is not in session
        return redirect(url_for("login"))
    return 0

@app.route("/<company>/<email>/<username>/<session_key>/chartOfAccounts", methods=["POST", "GET"])
def chartOfAccounts(company, email, username, session_key):
    try:
        if session[email] == session_key:
            return render_template("chartOfACcounts.html", company=company, email=email, username=username, session_sey=session_key)
        else:
            return redirect(url_for("login"))
    except KeyError:
        # Username is not in session
        return redirect(url_for("login"))
    return 0

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
