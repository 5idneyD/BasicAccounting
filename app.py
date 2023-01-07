from flask import Flask, render_template, request, redirect, url_for
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Current files path to create absolute path
basedir = os.path.abspath(os.path.dirname(__file__))


# Using sqlite3 db
# Secret key changes for each new session; improves security
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + \
    os.path.join(basedir, "./database/database.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(12).hex()

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
    password = db.Column(db.String(40))
    admin = db.Column(db.Boolean)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html", message="Hello Flask")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        users = db.session.execute("SELECT * FROM Users WHERE username='" + email + "';")
        # each user contains id, company, email & password
        for user in users:
            if user["password"] == password:
                return redirect(f"/{user['company']}/dashboard/{user['username']}")
        # print(users)

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
        new_email = request.form["email"]
        new_password = request.form["password"]

        new_user = Users(company=company, username=new_email,
                         password=new_password, admin=False)
        db.session.add(new_user)
        db.session.commit()


    return render_template("admin.html", company=company)


@app.route("/<company>/dashboard/<username>")
def dashboard(company, username):

    return render_template("dashboard.html", company=company, username=username)

if __name__ == "__main__":
    app.run(debug=True)
