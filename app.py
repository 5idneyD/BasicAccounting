# testing webhooks
from flask import Flask, render_template, request, redirect, send_from_directory, url_for, session, Response, abort
from flask_migrate import Migrate
from passlib.hash import pbkdf2_sha256
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import datetime as dt
from functools import wraps
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import random
import string
from dotenv import load_dotenv
from bin.generateInvoice import loadInvoiceTemplate
from pyinvoice.models import Item
from flask_cors import CORS
import git
import pandas as pd
import openpyxl
import sys
import traceback
import json
# PythonAnywhere and windows10 reference parent directories differently
# If trying to load the windows 10 way doesn't find a .env file (i.e. returns False), use the PythonAnywhere route
if load_dotenv("./.env") == False:
    load_dotenv("../.env")
else:
    load_dotenv("./.env")

# Initialise app and add CORS config
app = Flask(__name__, static_folder="dist", template_folder="src/templates")
CORS(app)

# Current files path to create absolute path
basedir = os.path.abspath(os.path.dirname(__file__))


# Using sqlite3 db in Dev mode, MySQL in Production mode
# The correct URI is stored in the .env file
# Secret key changes for each new session; improves security
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_POOL_RECYCLE"] = 280
app.config["SQLALCHEMY_POOL_SIZE"] = 20
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["SESSION_PERMANENT"] = False
app.config["SECRET_KEY"] = os.urandom(12).hex()
app.secret_key = os.urandom(12).hex()


db = SQLAlchemy(app)
# Allows us to migrate the db
# Needed when adding new columns to any table during development
# See db_migrate.txt in Notes/ for tips on how to migrate
# Doesn't work for MySQL, need to append manually via terminal
migrate = Migrate(app, db)


# All database classes
class Companies(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    company = db.Column(db.String(40))
    admin_email = db.Column(db.String(40))
    admin_password = db.Column(db.String(40))
    accounting_year = db.Column(db.String(4))
    accounting_period = db.Column(db.String(4))
    vat_number = db.Column(db.String(40), default="")
    invoice_email = db.Column(db.String(40), default="")


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    company = db.Column(db.String(40))
    username = db.Column(db.String(40))
    email = db.Column(db.String(40))
    password = db.Column(db.String(256))
    admin = db.Column(db.String(1))
    designTheme = db.Column(db.String(35))

    # Result of printing the class
    # e.g.
    # for i in users:
    #        print(i)
    def __repr__(self):
        return f"<id={self.id}, username={self.username}>, admin={self.admin}"


class ChartOfAccounts(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    company = db.Column(db.String(40))
    nominal = db.Column(db.Integer, nullable=False)
    account_name = db.Column(db.String(40))
    balance = db.Column(db.Float, default=0.00)


class Customers(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    company = db.Column(db.String(40))
    customer_name = db.Column(db.String(40))
    customer_code = db.Column(db.String(6))
    customer_email = db.Column(db.String(40))
    customer_address = db.Column(db.String(100))
    customer_credit_limit = db.Column(db.Float)
    customer_payment_terms = db.Column(db.Integer)


class Suppliers(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    company = db.Column(db.String(40))
    supplier_name = db.Column(db.String(40))
    supplier_code = db.Column(db.String(6))
    supplier_email = db.Column(db.String(40))
    supplier_address = db.Column(db.String(100))


class NominalTransactions(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    company = db.Column(db.String(40))
    transaction_type = db.Column(db.String(40))
    client_code = db.Column(db.String(40))
    transaction_number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(40))
    # description = db.Column(db.String(40))
    nominal_code = db.Column(db.Integer)
    description = db.Column(db.String(40))
    debit = db.Column(db.Float)
    credit = db.Column(db.Float)
    net_value = db.Column(db.Float)
    vat_value = db.Column(db.Float, default=0.00)
    total_value = db.Column(db.Float)
    posted_by = db.Column(db.String(40))
    posted_on = db.Column(db.String(40))
    accounting_year = db.Column(db.String(4), default=0)
    accounting_period = db.Column(db.String(4), default=0)
    reference = db.Column(db.String(70))
    to_post = db.Column(db.Integer, default=0)
    is_paid = db.Column(db.String(8), default="False")


class Budgets(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    company = db.Column(db.String(40))
    year = db.Column(db.Integer)
    period = db.Column(db.Integer)
    nominal_code = db.Column(db.Integer)
    value = db.Column(db.Float, default=0.00)


class PasswordReset(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(40))
    code = db.Column(db.String(6))

class ToDoList(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user = db.Column(db.String(64))
    company = db.Column(db.String(64))
    task = db.Column(db.String(256))

class SalesHubProducts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(64))
    product_name = db.Column(db.String(128))
    product_description = db.Column(db.String(128))
    product_net_price = db.Column(db.Float)
    product_vat_price = db.Column(db.Float)
    product_image = db.Column(db.String(128))
    link = db.Column(db.String(32))

class LogIns(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    user = db.Column(db.String(128))
    ip_address = db.Column(db.String(128))
    
# Create database tables if they don't already exist
with app.app_context():
    db.create_all()


# Generic error page when error
# Most common error is url doesn't exist
# Or if database connection fails
# usually caused by re-starting database on PythonAnywhere and not giving time
@app.errorhandler(Exception)
def not_found(e):
    # return render_template("error.html", error=e)
    pass

# refresh session on each request
# If 30 mins between requests, logout of session


@app.before_request
def before_request():

    # Reset password for example account on web
    try:
        user = Users.query.filter_by(
            company="Example Ltd", email="example@basicaccounting.co.uk").first()
        user.password = pbkdf2_sha256.hash("p123")
        db.session.commit()
    # Unless example account doesn't exist (i.e. in dev mode, not production)
    except:

        pass

    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    session.modified = True

    # print(dt.datetime.now().strftime("%d-%b-%Y %I:%M %p"),
    #       request.base_url, "\t", request.remote_addr)

    # Do not respond to requests with wp- (it's a bot looking for wordpress sites)
    if "wp-" in request.path or ".php" in request.path:
        print("Bot intruder")
        return redirect(url_for("index"))
    # Do not allow route access to any url with .env in it
    if ".env" in request.path:
        print("Trying to access .env")
        return redirect(url_for("index"))

    # if request.remote_addr == "":
    #     abort(403)


# Wrapper for login required
# Loads user's personal theme
# If error/user doesn't exist in db, load login page
def login_required(f):
    @wraps(f)
    def wrap(company, email, username, session_key):
        try:
            if os.getenv("DEV") == "True" or session[email] == session_key:
                user = Users.query.filter(
                    Users.company == company, Users.email == email).first()
                design = user.designTheme
                return f(company, email, username, session_key,theme=design)
            else:
                return redirect(url_for("login"))
        except KeyError as exception:
            # etype, value, tb = sys.exc_info()
            # print(traceback.print_exception(etype, value, tb))
            # print("error", exception)
            return redirect(url_for("login"))

    return wrap


# Tghis is a route that listens to github webhooks, and refreshed the pythonanywhere files
# by pulling the master everytime the github repo is updated (i.e. has a new commit)
@app.route("/update_server", methods=["GET", "POST"])
def update_server():
    if request.method == 'POST':
        try:
            repo = git.Repo("/home/SLD/BasicAccounting")
            repo.remotes.origin.pull()
            print("Have pulled git origin")
            return "Git origin pulled", 200
        except Exception as e:
            print(f"Error in process of updating: {e}")
            return "Error in process of updating"
    else:
        print("Error: Wrong event type")
        return 'Wrong event type', 400


# This returns whichever static file the browser is trying to reach
# They are both saved in the static directory
# Only there for SEO reasons
@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

# Homepage, indexed
@app.route("/")
def index():
    return render_template("home.html")


# Login Page
# Uses hashed password then adds user to session
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        users = Users.query.filter(Users.email == email).all()

        if len(users) == 0:
            return render_template("login.html", message="This email address cannot be found")

        for user in users:
            # Use library's built in function to compare hashed password in db with user input
            if pbkdf2_sha256.verify(password, user.password):
                # Add user to current session
                session[email] = os.urandom(12).hex()
                login_details = LogIns(user=email, date=dt.datetime.now(), ip_address=str(request.remote_addr))
                db.session.add(login_details)
                db.session.commit()
                # redirect to dashboard
                return redirect(
                    url_for(
                        "dashboard",
                        company=user.company,
                        email=email,
                        username=user.username,
                        session_key=session[email],
                    )
                )
            else:
                return render_template("login.html", message="This email address and password do not match")

    return render_template("login.html", message="")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        email = request.form["email"]

        # If the email address is already taken in the db, refuse
        # Else, send email to address given to verify
        # Login details are in .env
        # The verification code is saved in db
        # If the email address has already been sent a verification email, overwrite with new code in db and re-send
        if Users.query.filter(Users.email == email).first() is None:
            print("does not exist")
            verification_code = "".join(
                [str(random.randint(1, 9)) for number in range(6)])
            new_code = PasswordReset(email=email, code=verification_code)
            current = PasswordReset.query.filter(Users.email == email).first()
            if current is None:
                db.session.add(new_code)
            else:
                current.code = verification_code

            db.session.commit()

            mail_server = os.getenv("MAIL_SERVER")
            mail_port = os.getenv("MAIL_PORT")
            mail = smtplib.SMTP_SSL(mail_server, mail_port)
            sender = os.getenv("EMAIL_SENDER")
            password = os.getenv("EMAIL_PASSWORD")
            mail.login(sender, password)
            recipient = email
            subject = "No Variance Verification Code"
            msg_text = f"""
            Hello,\nThank you for being interested in signing up to No Variance!\n
            You are being sent this email to verify that it was you who is signing up to No Variance and ensure nobody is using your
            email address that you don't know about.\n
            The code required to sign-up is : {verification_code}.\n\n
            If you have not requested this, please discard this email.
            \n\nKind regards,
            \nNo Variance
            """.strip()
            msg = f"From: {sender}\r\nTo: {recipient}\r\nsubject: {subject}\r\n{msg_text}\r\n"
            mail.sendmail(sender, recipient, msg)
            mail.quit()

            return redirect(url_for("verifyAccount", email=email))
        else:
            print("exists")
            return render_template("signup.html", message="This email address already exists, please Login")

    return render_template("signup.html")


# Sent through to this page after being emailed a verification code
# Data is collected and saved in db is the verification code matches
# else, is rejected
@app.route("/verifyAccount", methods=["POST", "GET"])
def verifyAccount():
    if request.method == "POST":
        company_name = request.form["company"]
        company_email = request.form["email"]
        company_password = request.form["password"]
        password = pbkdf2_sha256.hash(company_password)
        accounting_year = request.form["accounting_year"]
        accounting_period = request.form["accounting_period"]
        verification_code = request.form["verification_code"]
        # find the code the user was emailed
        required_code = PasswordReset.query.filter(
            PasswordReset.email == company_email).first()
        if verification_code == required_code.code:
            new_company = Companies(
                company=company_name,
                admin_email=company_email,
                admin_password=password,
                accounting_year=accounting_year,
                accounting_period=accounting_period,
            )
            db.session.add(new_company)
            new_admin = Users(
                company=company_name, email=company_email, username=company_email, password=password, admin="3"
            )
            db.session.add(new_admin)
            # remove verification code from db so company account cannot be re-created
            db.session.delete(required_code)

            # Add default nominal accounts
            default_bank_account = ChartOfAccounts(
                company=company_name,
                nominal=60000,
                account_name="Bank Account",
                balance=0.00
            )
            default_cash_account = ChartOfAccounts(
                company=company_name,
                nominal=60010,
                account_name="Outstanding Cash",
                balance=0.00
            )
            default_vat_account = ChartOfAccounts(
                company=company_name,
                nominal=60005,
                account_name="VAT Balance",
                balance=0.00
            )

            db.session.add(default_bank_account)
            db.session.add(default_vat_account)
            db.session.add(default_cash_account)

            db.session.commit()
            session[company_email] = os.urandom(12).hex()
            return redirect(
                url_for(
                    "admin",
                    company=company_name,
                    email=company_email,
                    username="Admin",
                    session_key=session[company_email],
                )
            )
        else:
            return render_template("verifyAccount.html")

    return render_template("verifyAccount.html")


# If password is forgotten, you go to this page and request a verification code
# Then get sent to resetPassword page
@app.route("/forgotPassword", methods=["POST", "GET"])
def forgotPassword():
    if request.method == "POST":
        email = request.form["email"]
        code = "".join([str(random.randint(1, 9)) for number in range(6)])

        mail_server = os.getenv("MAIL_SERVER")
        mail_port = os.getenv("MAIL_PORT")
        mail = smtplib.SMTP_SSL(mail_server, mail_port)
        sender = os.getenv("EMAIL_SENDER")
        password = os.getenv("EMAIL_PASSWORD")
        mail.login(sender, password)
        recipient = email
        subject = "Password Reset Code"
        msg_text = f"Hello,\nYou are being sent this email to reset your password at No Variance.\n The code required to set a new password for your email address is : {code}.\n\nIf you have not requested this, please discard this email.\n\nKind regards,\nNo Variance"
        msg = f"From: {sender}\r\nTo: {recipient}\r\nsubject: {subject}\r\n{msg_text}\r\n"
        mail.sendmail(sender, recipient, msg)
        mail.quit()

        new_code = PasswordReset(email=email, code=code)
        db.session.add(new_code)
        db.session.commit()
        return redirect(url_for("resetPassword"))

    return render_template("forgotPassword.html")


# Come here after requesting verification code to reset password
@app.route("/resetPassword", methods=["POST", "GET"])
def resetPassword():
    message = "An email has been sent to the address you entered.\nPlease enter the code receieved in this email and a new password.\nIf you cannot see any emails, please check your spam folder and ensure the address entered is correct."

    if request.method == "POST":
        email = request.form["email"]
        code = request.form["code"]
        password = request.form["password"]
        criteria = PasswordReset.query.filter(
            PasswordReset.email == email).first()

        if code == criteria.code:
            user = Users.query.filter(Users.email == email).first()
            user.password = pbkdf2_sha256.hash(password)
            db.session.delete(criteria)
            db.session.commit()
            return redirect(url_for("login"))

    return render_template("resetPassword.html", message=message)


# Admin page
# Different users have different permissions
# First user who creates the account is given full permission
# Level 1, 2, 3 (Basic, basic Admin, Advanced Admin)
@app.route("/<company>/<email>/<username>/<session_key>/admin", methods=["POST", "GET"])
@login_required
def admin(company, email, username, session_key, theme):
    company_data = Companies.query.filter(Companies.company == company).first()
    current_users = Users.query.filter(Users.company == company).all()
    accounting_year = company_data.accounting_year
    accounting_period = company_data.accounting_period
    permission_level = Users.query.filter_by(
        company=company, email=email).first().admin

    message = ""

    if request.method == "POST" and email != "example@basicaccounting.co.uk":
        if "addUserForm" in request.form:
            new_name = request.form["name"]
            new_email = request.form["email"]

            # Generating random inintial password
            # User will change password when logged in
            new_password = "".join(random.choice(
                string.ascii_lowercase+string.digits) for i in range(10))
            password = pbkdf2_sha256.hash(new_password)

            # By default givin admin level 1
            # This is the lowest
            admin_permission = "1"
            admin_permission = request.form["adminLevel"]

            # Sending an email to the new address used
            # Assigning a random password at the start
            # instead of the admin user giving one
            # This is for security reasons
            mail_server = os.getenv("MAIL_SERVER")
            mail_port = os.getenv("MAIL_PORT")
            mail = smtplib.SMTP_SSL(mail_server, mail_port)
            sender = os.getenv("EMAIL_SENDER")
            password = os.getenv("EMAIL_PASSWORD")
            mail.login(sender, password)
            recipient = new_email
            subject = "No Variance - New User"
            msg_text = f"""
            Hello,
            You are being sent this email as this email address has recently been added to {company}'s No Variance account.
            
            To confirm your account, you will need to log in with the following details:
            email address: {recipient}
            password: {new_password}
            
            Please note this password is encrypted, and nobody knows this password other than yourself.
            Once you have logged in, please go to the Change password page (found under the 'Other' tab) and re-set your password.
            
            Please do not share your password. We will never ask for your password.
            
            Kind regards,
            
            No Variance Accounting Software
            
            """
            msg = f"From: {sender}\r\nTo: {recipient}\r\nsubject: {subject}\r\n{msg_text}\r\n"
            mail.sendmail(sender, recipient, msg)
            mail.quit()
            new_user = Users(
                company=company, username=new_name, email=new_email, password=password, admin=admin_permission
            )
            db.session.add(new_user)
            db.session.commit()

        elif "addNominalForm" in request.form:
            nominal = request.form["nominal"]
            account_name = request.form["accountName"]

            # If the number of rows that match this account is higher than 0, do not proceed
            # i.e. If the nominal account already exists for this company
            if (
                len(
                    ChartOfAccounts.query.filter(
                        ChartOfAccounts.company == company, ChartOfAccounts.nominal == nominal
                    ).all()
                )
                == 0
            ):
                new_nominal = ChartOfAccounts(
                    company=company, nominal=nominal, account_name=account_name)
                db.session.add(new_nominal)
                db.session.commit()
            else:
                message = "This Nominal Account already exists, please use a different Nominal Code"
        elif "removeUserForm" in request.form:
            user_email = request.form["email"]
            user = Users.query.filter_by(
                email=user_email, company=company).first()
            db.session.delete(user)
            db.session.commit()
        
        elif "editUserForm" in request.form:
            editUserEmail = request.form['email']
            newPermission = request.form['adminLevel']
            editUser = Users.query.filter(Users.company==company, Users.email==editUserEmail).first()
            
            # Update the users admin level
            try:
                editUser.admin = newPermission
                db.session.commit()
                # If error (i.e. the user does not exist), return message
            except AttributeError:
                message = "This user does not exist"

        elif "closePeriodForm" in request.form:

            current_period = request.form["period"]
            current_year = request.form["year"]
            print("current period", current_period)
            print("current year", current_year)
            if current_period == "12":
                new_period = "1"
                new_year = str(int(current_year) + 1)
                company_data.accounting_period = new_period
                company_data.accounting_year = new_year
            else:
                new_period = str(int(current_period) + 1)
                company_data.accounting_period = new_period

            db.session.commit()
            company_data = Companies.query.filter_by(company=company).first()
            accounting_year = company_data.accounting_year
            accounting_period = company_data.accounting_period
            return render_template(
                "admin.html",
                company=company,
                email=email,
                admin=permission_level,
                accounting_year=accounting_year,
                accounting_period=accounting_period,
                design=theme,
            )

        elif "invoiceDetailsForm" in request.form:
            vat_number = request.form["vat_number"]
            email_to_include = request.form["email"]
            company_data.vat_number = vat_number
            company_data.invoice_email = email_to_include
            db.session.commit()
        else:
            pass

    return render_template(
        "admin.html",
        company=company,
        email=email,
        admin=permission_level,
        accounting_year=accounting_year,
        accounting_period=accounting_period,
        design=theme,
        message=message
    )


# Default page when loggin in/creating account
# Holds a graph that shows current year net profit graph using js library
@app.route("/<company>/<email>/<username>/<session_key>/dashboard", methods=["POST", "GET"])
@login_required
def dashboard(company, email, username, session_key, theme):
    year = Companies.query.filter_by(company=company).first().accounting_year
    accounts = (
        db.session.query(ChartOfAccounts)
        .filter(ChartOfAccounts.company == company)
        .filter(ChartOfAccounts.nominal < 60000)
    )
    
    tasks = ToDoList.query.filter(ToDoList.company==company, ToDoList.user==username).all()

    data = {}
    for i in range(1, 13):
        monthly_balance = 0
        ytd_balance = 0
        for account in accounts:
            transactions = (
                db.session.query(NominalTransactions)
                .filter(NominalTransactions.company == company)
                .filter(NominalTransactions.nominal_code == account.nominal)
                .filter(NominalTransactions.accounting_year == year)
                .filter(NominalTransactions.to_post not in [1, "1"])
            )

            for transaction in transactions:
                if int(transaction.accounting_period) == i:
                    if transaction.transaction_type == "journal" and account.nominal < 20000:
                        monthly_balance -= transaction.net_value
                    elif account.nominal > 20000:
                        monthly_balance -= transaction.net_value
                    else:
                        monthly_balance += transaction.net_value
                else:
                    pass

        data[i] = monthly_balance


    # The only post request is adding or removing from to do list
    if request.method == "POST":
        
        # Read the json object being posted
        action = request.json
        
        # If there is a plus at the start, it means add the action
        if action[0] == "+":
            action = action[1:]
            newAction = ToDoList(user=username, company=company, task=action)
            db.session.add(newAction)
        # If theres a minus at the start, it means remove
        else:
            action = action[1:]
            currentAction = ToDoList.query.filter(ToDoList.company==company, ToDoList.user==username, ToDoList.task==action).first()
            db.session.delete(currentAction)
             
        db.session.commit()
        

    return render_template(
        "dashboard.html",
        company=company,
        email=email,
        username=username,
        session_key=session_key,
        design=theme,
        total_values=data,
        tasks=tasks
    )

# Shows user all of their nominal accounts in a sorted order
# They can create new accounts on the admin page
# Once an account is created, it cannot be deleted


@app.route("/<company>/<email>/<username>/<session_key>/chartOfAccounts", methods=["POST", "GET"])
@login_required
def chartOfAccounts(company, email, username, session_key, theme):
    accounts = ChartOfAccounts.query.filter_by(
        company=company).order_by(ChartOfAccounts.nominal).all()
    return render_template(
        "chartOfAccounts.html",
        company=company,
        email=email,
        username=username,
        session_sey=session_key,
        accounts=accounts,
        design=theme,
    )


# Function that calculates the outstanding balance for each customer
# Outstanding balance means unpaid invoices (a.k.a Aged Debt)
# The query ignores journals
# Can specifiy just 1 client to save time if needed
def customerBalances(company, client="%%"):
    customers = Customers.query.filter(
        Customers.company == company, Customers.customer_code.ilike(client)).all()
    balances = {}
    total_sales = {}
    for i in customers:
        balances[i.customer_code] = 0.00
        total_sales[i.customer_code] = [0.00, 0.00, 0.00]

    transactions = NominalTransactions.query.filter(
        NominalTransactions.company == company,
        NominalTransactions.client_code.ilike(client),
        NominalTransactions.transaction_type != "Journal",
        NominalTransactions.transaction_type != "payment",
        NominalTransactions.client_code.in_(set(balances.keys())),
    ).all()

    for i in transactions:
        if i.is_paid == "False":
            balances[i.client_code] += float(i.total_value)
            total_sales[i.client_code][1] += float(i.total_value)
        else:
            total_sales[i.client_code][0] += float(i.total_value)
        total_sales[i.client_code][2] += float(i.total_value)

    print(total_sales)

    return customers, balances, total_sales


# List of each company's customers
# Query the database using our customerBalace function
# All customers needed so no client code argument needed
@app.route("/<company>/<email>/<username>/<session_key>/Customers", methods=["POST", "GET"])
@login_required
def customers(company, email, username, session_key, theme):
    customers, balances, total_sales = customerBalances(company)

    # Sort and only render only top 3 customers
    total_sales = sorted(total_sales.items(),
                         key=lambda x: x[1], reverse=True)[:3]

    return render_template(
        "customers.html",
        company=company,
        email=email,
        username=username,
        session_key=session_key,
        customers=customers,
        design=theme,
        balances=balances,
        total_sales=total_sales
    )


# Page to add new customers
# Customer must be added before an invoice can be posted for them
# User fills in form and posts
@app.route("/<company>/<email>/<username>/<session_key>/addCustomer", methods=["POST", "GET"])
@login_required
def addCustomer(company, email, username, session_key, theme):
    if request.method == "POST":
        customer_name = request.form["customer_name"]
        customer_code = request.form["customer_code"]
        customer_email = request.form["customer_email"]
        customer_address = request.form["customer_address"]
        customer_credit_limit = request.form["customer_credit_limit"]
        customer_payment_terms = request.form["customer_payment_terms"]
        customer = Customers(
            company=company,
            customer_name=customer_name,
            customer_code=customer_code,
            customer_email=customer_email,
            customer_address=customer_address,
            customer_credit_limit=customer_credit_limit,
            customer_payment_terms=customer_payment_terms,
        )
        db.session.add(customer)
        db.session.commit()

    return render_template(
        "addCustomer.html", company=company, email=email, username=username, session_key=session_key, design=theme
    )

# Page to edit existing customers
# Customer must be added before an invoice can be posted for them
# User fills in form and posts
@app.route("/<company>/<email>/<username>/<session_key>/editCustomer", methods=["POST", "GET"])
@login_required
def editCustomer(company, email, username, session_key, theme):
    
    if request.method == "POST":
        name = request.form["name"]
        code = request.form["code"]
        new_email = request.form["email"]
        address = request.form["address"]
        credit = request.form["credit"]
        days = request.form["days"]
    
        client = Customers.query.filter(Customers.company==company,
                                        Customers.customer_code==code).first()
        client.customer_name = name
        client.customer_address = address
        client.customer_email = new_email
        client.customer_payment_terms = days
        client.customer_credit_limit = credit
        db.session.commit()
    
    clients = Customers.query.filter(Customers.company==company).all()
    data = {}
    for client in clients:
        data[client.customer_code] = [client.customer_name, client.customer_email, client.customer_address,
                                   client.customer_credit_limit, client.customer_payment_terms]
    
    
    return render_template(
        "editCustomer.html", company=company, email=email, username=username, session_key=session_key, design=theme, client_codes=clients, clients=data
    )
    

def supplierBalances(company, client="%%"):
    suppliers = Suppliers.query.filter(
        Suppliers.company == company, Suppliers.supplier_code.ilike(client)).all()
    balances = {}
    total_sales = {}
    for i in suppliers:
        balances[i.supplier_code] = 0.00
        total_sales[i.supplier_code] = [0.00, 0.00, 0.00]

    transactions = NominalTransactions.query.filter(
        NominalTransactions.company == company,
        NominalTransactions.client_code.ilike(client),
        NominalTransactions.transaction_type != "Journal",
        NominalTransactions.transaction_type != "payment",
        NominalTransactions.client_code.in_(set(balances.keys())),
    ).all()

    for i in transactions:
        if i.is_paid == "False":
            balances[i.client_code] += float(i.total_value)
            total_sales[i.client_code][1] += float(i.total_value)
        else:
            total_sales[i.client_code][0] += float(i.total_value)
        total_sales[i.client_code][2] += float(i.total_value)

    return suppliers, balances, total_sales


# List of each company's suppliers
# Might create personal function to access and query the list more easily
# e.g. Only select <x> supplier if requested
@app.route("/<company>/<email>/<username>/<session_key>/Suppliers", methods=["POST", "GET"])
@login_required
def suppliers(company, email, username, session_key, theme):

    suppliers, balances, total_sales = supplierBalances(company)

    # Sort and only render top 3 suppliers
    total_sales = sorted(total_sales.items(),
                         key=lambda x: x[1], reverse=True)[:3]

    return render_template(
        "suppliers.html",
        company=company,
        email=email,
        username=username,
        session_key=session_key,
        suppliers=suppliers,
        total_sales=total_sales,
        design=theme
    )


# Page to add new suppliers
# Suppliers must be added before an invoice can be posted for them
# User fills in form and posts
@app.route("/<company>/<email>/<username>/<session_key>/addSupplier", methods=["POST", "GET"])
@login_required
def addSupplier(company, email, username, session_key, theme):
    if request.method == "POST":
        supplier_name = request.form["supplier_name"]
        supplier_code = request.form["supplier_code"]
        supplier_email = request.form["supplier_email"]
        supplier_address = request.form["supplier_address"]

        supplier = Suppliers(
            company=company, supplier_name=supplier_name, supplier_code=supplier_code,
            supplier_email=supplier_email, supplier_address=supplier_address)
        db.session.add(supplier)
        db.session.commit()

    return render_template(
        "addSupplier.html", company=company, email=email, username=username, session_key=session_key, design=theme
    )

# Page to edit existing customers
# Customer must be added before an invoice can be posted for them
# User fills in form and posts
@app.route("/<company>/<email>/<username>/<session_key>/editSupplier", methods=["POST", "GET"])
@login_required
def editSupplier(company, email, username, session_key, theme):
    
    if request.method == "POST":
        name = request.form["name"]
        code = request.form["code"]
        new_email = request.form["email"]
        address = request.form["address"]
    
        client = Suppliers.query.filter(Suppliers.company==company,
                                        Suppliers.supplier_code==code).first()
        client.supplier_name = name
        client.supplier_address = address
        client.supplier_email = new_email
        db.session.commit()
    
    clients = Suppliers.query.filter(Suppliers.company==company).all()
    data = {}
    for client in clients:
        content = [client.supplier_name, client.supplier_email, client.supplier_address]
        data[client.supplier_code] = [str(i) if i== None else i for i in content]
    
            
    
    return render_template(
        "editSupplier.html", company=company, email=email, username=username, session_key=session_key, design=theme, client_codes=clients, clients=data
    )
    

# Inline comments as very detailed
@app.route("/<company>/<email>/<username>/<session_key>/addSalesInvoice", methods=["POST", "GET"])
@login_required
def addSalesInvoice(company, email, username, session_key, theme):
    # Query data to set up form
    # such as customer codes and accounting year/period, VAT number
    customers = Customers.query.filter_by(company=company).all()
    company_data = Companies.query.filter_by(company=company).first()
    accounting_year = company_data.accounting_year
    accounting_period = company_data.accounting_period
    vat_number = company_data.vat_number
    invoice_email = company_data.invoice_email
    accounts = ChartOfAccounts.query.filter(ChartOfAccounts.company==company,
                                                    ChartOfAccounts.nominal < 20000).all()
    revenue_accounts = []
    for i in accounts:
        revenue_accounts.append([i.account_name, i.nominal])

    if request.method == "POST":

        # Query all pre-existing sales_invoices for this company
        # Append the reference to references list
        # If the reference list is empty, append 0
        # The invoice number will be the last reference + 1
        invoices = NominalTransactions.query.filter_by(
            company=company, transaction_type="sales_invoice").all()
        references = []
        for invoice in invoices:
            references.append(int(str(invoice.reference).replace(company, "")))
        if len(references) == 0:
            references.append(0)

        invoice_number = references[-1] + 1

        # Read header form input
        # See what customer this invoice is for and gather that customer's data from db
        invoice_date = request.form["invoice_date"]
        customer_code = request.form["customer_code"]
        customer = Customers.query.filter_by(
            company=company, customer_code=customer_code).first()
        customer_name = customer.customer_name
        customer_email = customer.customer_email
        # Find the number of rows on the invoice so we use the correct for loop range
        number_of_rows = request.form["number_of_rows"]
        # Create pdf for invoice using template from generateInvoice.py
        # This pdf will be emailed to the customer email address if requested in form
        invoiceTemplate = loadInvoiceTemplate(
            invoice_number, invoice_date, company, vat_number, customer_name, customer_email, 30
        )

        # Query the customer's credit limit set in admin
        # Will compare to new balance later to ensure customer credit does not exceed limit
        credit_limit = customer.customer_credit_limit

        # Loop through the form, reading each row in the invoice
        # Data (nominal code, values, description, date) will be different for each row
        for i in range(1, int(number_of_rows) + 1):
            row = str(i)
            nominal_code = request.form[row + "_nominal_code"]
            description = request.form[row + "_description"]
            net_value = request.form[row + "_net_value"]
            vat = request.form[row + "_vat"]
            total_value = request.form[row + "_total_value"]
            reference = company + str(invoice_number)

            # If no VAT value set in the form, use 0.00 to avoid concat errors
            if vat == "":
                vat = 0.00

            # Combine all data for this row and add to db, not committing yet
            new_nominal_transaction = NominalTransactions(
                company=company,
                transaction_type="sales_invoice",
                client_code=customer_code,
                transaction_number=invoice_number,
                date=invoice_date,
                nominal_code=nominal_code,
                description=description,
                net_value=net_value,
                vat_value=vat,
                total_value=total_value,
                posted_on=dt.datetime.today().strftime("%Y-%m-%d"),
                posted_by=username,
                reference=reference,
                accounting_year=accounting_year,
                accounting_period=accounting_period,
            )

            db.session.add(new_nominal_transaction)

            # Update the nominal accounts balance in db (for trial balance data)
            account = ChartOfAccounts.query.filter_by(
                company=company, nominal=nominal_code).first()
            account.balance = account.balance - float(net_value)

            # Now add the vat balance to the VAT nominal code
            vat_account = ChartOfAccounts.query.filter_by(
                company=company, nominal=60005).first()
            vat_account.balance = float(vat_account.balance) - float(vat)

            # Now add the total balance to the outstanding cash account
            cash_account = ChartOfAccounts.query.filter(
                ChartOfAccounts.company == company, ChartOfAccounts.nominal == 60010).first()
            cash_account.balance = float(
                cash_account.balance) + float(total_value)

            # Add invoice row to pdf file
            invoiceTemplate.add_item(Item(row, description, 1, total_value))

        # If this invoice pushes the customer balance above the credit limit, abort
        _, new_balance, total_sales = customerBalances(
            company, client=customer_code)
        new_balance = new_balance[customer_code]
        if float(new_balance) > float(credit_limit):
            return render_template(
                "addSalesInvoice.html",
                company=company,
                email=email,
                username=username,
                session_key=session_key,
                customers=customers,
                references=references,
                design=theme,
                message="Post not completed, above customer's credit limit",
            )
        else:
            pass

        # Add further details to the pdf invoice and save
        # Create email using smtplib, credentials saved in .env
        # Add sender, recipient, attachment and message to email, cc in current user
        # Send email
        # Only do this if email setting in the form was set to yes (which is default)
        invoiceTemplate.set_bottom_tip(
            f"Email: {invoice_email}<br/>Please don't hesitate to contact us with any questions <br/> This invoice was generated automatically by No Variance"
        )
        invoiceTemplate.finish()
        if request.form["emailSetting"] == "yes" and email != "example@basicaccounting.com":
            sender = os.getenv("EMAIL_SENDER")
            password = os.getenv("EMAIL_PASSWORD")

            message = MIMEMultipart("mixed")
            message["Subject"] = f"{company} Invoice {invoice_number}"
            message["From"] = sender
            if email == "example@basicaccounting.co.uk":
                message["To"] = email
            else:
                message["To"] = customer_email
                message["CC"] = email
            msg_text = f"""
            Hello,\nAttached is an invoice from {company} to {customer_name}.\n
            This email has been auto-generated by No Variance.\n
            If you believe there are errors or have any questions, please contact the email address provided on the invoice.\n
            Kind regards,\n
            No Variance
            """.strip()
            part1 = MIMEText(msg_text, "plain")
            message.attach(part1)
            with open(f"invoice {invoice_number}.pdf", "rb") as opened:
                openedfile = opened.read()
            attachedfile = MIMEApplication(openedfile, _subtype="pdf")
            attachedfile.add_header(
                "content-disposition", "attachment", filename=f"invoice {invoice_number}.pdf")
            message.attach(attachedfile)

            mail_server = os.getenv("MAIL_SERVER")
            mail_port = os.getenv("MAIL_PORT")
            mail = smtplib.SMTP_SSL(mail_server, mail_port)
            mail.login(sender, password)
            mail.sendmail(sender, sender, message.as_string())
            mail.quit()

        # Commit the invoice to db
        db.session.commit()

        # Add this invoice number to the referneces instead of re-querying the entire db to save time
        references.append(reference)

        return render_template(
            "addSalesInvoice.html",
            company=company,
            email=email,
            username=username,
            session_key=session_key,
            customers=customers,
            design=theme,
            message="",
            revenue_accounts=revenue_accounts
        )
    return render_template(
        "addSalesInvoice.html",
        company=company,
        email=email,
        username=username,
        session_key=session_key,
        customers=customers,
        design=theme,
        message="",
        revenue_accounts=revenue_accounts
    )


@app.route("/<company>/<email>/<username>/<session_key>/addPurchaseInvoice", methods=["POST", "GET"])
@login_required
def addPurchaseInvoice(company, email, username, session_key, theme):
    # Query general supplier data to fill out potential options in form
    # e.g. Possible suppliers for the user to use
    suppliers = Suppliers.query.filter_by(company=company).all()
    company_data = Companies.query.filter_by(company=company).first()
    accounting_year = company_data.accounting_year
    accounting_period = company_data.accounting_period

    accounts = ChartOfAccounts.query.filter(ChartOfAccounts.company==company,
                                                    ChartOfAccounts.nominal >= 20000).order_by(ChartOfAccounts.nominal).all()
    cost_accounts = []
    for i in accounts:
        cost_accounts.append([i.account_name, i.nominal])


    if request.method == "POST":
        # Collect header table data from form
        invoice_number = request.form["invoice_number"]
        invoice_date = request.form["invoice_date"]
        supplier_code = request.form["supplier_code"]
        number_of_rows = request.form["number_of_rows"]

        # loop through rows in invoice
        for i in range(1, int(number_of_rows) + 1):
            row = str(i)
            nominal_code = request.form[row + "_nominal_code"]
            description = request.form[row + "_description"]
            net_value = request.form[row + "_net_value"]
            vat = request.form[row + "_vat"]
            total_value = request.form[row + "_total_value"]

            new_nominal_transaction = NominalTransactions(
                company=company,
                transaction_type="purchase_invoice",
                client_code=supplier_code,
                transaction_number=invoice_number,
                date=invoice_date,
                nominal_code=nominal_code,
                description=description,
                net_value=net_value,
                vat_value=vat,
                total_value=total_value,
                posted_on=dt.datetime.today().strftime("%Y-%m-%d"),
                posted_by=username,
                reference="",
                accounting_year=accounting_year,
                accounting_period=accounting_period,
            )

            db.session.add(new_nominal_transaction)
            account = ChartOfAccounts.query.filter_by(
                company=company, nominal=int(nominal_code)).first()
            account.balance = float(account.balance) + float(net_value)

            # Now add the vat balance to the vat account
            vat_account = ChartOfAccounts.query.filter_by(
                company=company, nominal=60005).first()
            vat_account.balance = vat_account.balance + float(vat)

            # Now add the total balance to the outstanding cash account
            cash_account = ChartOfAccounts.query.filter(
                ChartOfAccounts.company == company, ChartOfAccounts.nominal == 60010).first()
            cash_account.balance = float(
                cash_account.balance) - float(total_value)

        db.session.commit()

    return render_template(
        "addPurchaseInvoice.html",
        company=company,
        email=email,
        username=username,
        session_key=session_key,
        suppliers=suppliers,
        design=theme,
        cost_accounts=cost_accounts
    )


@app.route("/<company>/<email>/<username>/<session_key>/viewSalesInvoices", methods=["POST", "GET"])
@login_required
def viewSalesInvoices(company, email, username, session_key, theme):
    invoices = NominalTransactions.query.filter_by(
        company=company, transaction_type="sales_invoice").all()
    customers = []
    for invoice in invoices:
        customers.append(invoice.client_code)
    customers = set(customers)

    if request.method == "POST":
        customer_code = request.form["customer_code"]
        invoice_number = request.form["invoice_number"]
        selected_period = request.form["selected_period"]
        selected_year = request.form["selected_year"]
        if customer_code != "*":
            invoices = [
                invoice for invoice in invoices if invoice.client_code == customer_code]
        if invoice_number != "":
            invoices = [invoice for invoice in invoices if invoice.transaction_number == int(
                invoice_number)]
        if selected_period != "*":
            invoices = [
                invoice for invoice in invoices if invoice.accounting_period == selected_period]
        if selected_year != "*":
            invoices = [
                invoice for invoice in invoices if invoice.accounting_year == selected_year]

        return render_template(
            "viewSalesInvoices.html", company=company, invoices=invoices, customers=customers, design=theme
        )

    return render_template(
        "viewSalesInvoices.html", company=company, invoices=invoices, customers=customers, design=theme
    )


@app.route("/<company>/<email>/<username>/<session_key>/viewPurchaseInvoices", methods=["POST", "GET"])
@login_required
def viewPurchaseInvoices(company, email, username, session_key, theme):
    invoices = NominalTransactions.query.filter_by(
        company=company, transaction_type="purchase_invoice").all()

    suppliers = []
    for invoice in invoices:
        suppliers.append(invoice.client_code)

    suppliers = set(suppliers)

    if request.method == "POST":
        supplier_code = request.form["supplier_code"]
        invoice_number = request.form["invoice_number"]
        selected_period = request.form["selected_period"]
        selected_year = request.form["selected_year"]
        if supplier_code != "*":
            invoices = [
                invoice for invoice in invoices if invoice.client_code == supplier_code]
        if invoice_number != "":
            invoices = [invoice for invoice in invoices if invoice.transaction_number == int(
                invoice_number)]
        if selected_period != "*":
            invoices = [
                invoice for invoice in invoices if invoice.accounting_period == selected_period]
        if selected_year != "*":
            invoices = [
                invoice for invoice in invoices if invoice.accounting_year == selected_year]

        return render_template(
            "viewPurchaseInvoices.html", company=company, invoices=invoices, suppliers=suppliers, design=theme
        )

    return render_template(
        "viewPurchaseInvoices.html", company=company, invoices=invoices, suppliers=suppliers, design=theme
    )


@app.route("/<company>/<email>/<username>/<session_key>/journal", methods=["POST", "GET"])
@login_required
def journal(company, email, username, session_key, theme):

    if request.method == "POST":
        journal_date = str(request.form["journalDate"])
        journal_description = request.form["journalDescription"]
        to_reverse = request.form["to_reverse"]
        debitTotal = request.form["debitTotal"]
        creditTotal = request.form["creditTotal"]
        number_of_rows = request.form["number_of_rows"]
        company_data = Companies.query.filter_by(company=company).first()
        accounting_year = company_data.accounting_year
        accounting_period = company_data.accounting_period

        # Calcul;ate the next jounral number by loopingthrough all journals, and adding 1 to the last
        journals = NominalTransactions.query.filter_by(
            company=company, transaction_type="journal").all()
        references = []
        for journal in journals:
            references.append(int(journal.reference.split("_")[-1]))
            next_journal_number = max(references) + 1
        if len(references) == 0:
            next_journal_number = 1

        journal_number = str(next_journal_number)
        journal_reference = "journal_" + journal_number

        for i in range(1, int(number_of_rows) + 1):
            nominal_code = request.form[str(i) + "_nominal_code"]
            description = request.form[str(i) + "_description"]
            debit = request.form[str(i) + "_debit"]
            credit = request.form[str(i) + "_credit"]

            if debit == "":
                debit = 0.00
            else:
                debit = float(debit)

            if credit == "":
                credit = 0.00
            else:
                credit = float(credit)

            if debit == 0.00 and credit == 0.00:
                pass
            else:
                new_nominal_transaction = NominalTransactions(
                    company=company,
                    transaction_type="journal",
                    client_code="Journal",
                    transaction_number=journal_number,
                    date=journal_date,
                    nominal_code=nominal_code,
                    description=description,
                    debit=debit,
                    credit=credit,
                    net_value=debit - credit,
                    vat_value=0,
                    total_value=debit - credit,
                    posted_on=dt.datetime.today().strftime("%Y-%m-%d"),
                    posted_by=username,
                    reference=journal_reference,
                    accounting_year=accounting_year,
                    accounting_period=accounting_period,
                    to_post=0,
                )

                db.session.add(new_nominal_transaction)

                account = ChartOfAccounts.query.filter_by(
                    company=company, nominal=nominal_code).first()
                account.balance += debit
                account.balance -= credit

                if to_reverse == "yes":
                    debit, credit = credit, debit
                    batched_transaction = NominalTransactions(
                        company=company,
                        transaction_type="journal",
                        client_code="Journal",
                        transaction_number=journal_number,
                        date=journal_date,
                        nominal_code=nominal_code,
                        description=description,
                        debit=debit,
                        credit=credit,
                        net_value=debit - credit,
                        vat_value=0,
                        total_value=debit - credit,
                        posted_on=dt.datetime.today().strftime("%Y-%m-%d"),
                        posted_by=username,
                        reference=journal_reference,
                        to_post=1,
                    )
                    db.session.add(batched_transaction)

        db.session.commit()

        return render_template("journal.html", company=company, design=theme)

    return render_template("journal.html", company=company, design=theme)


@app.route("/<company>/<email>/<username>/<session_key>/changePassword", methods=["POST", "GET"])
@login_required
def changePassword(company, email, username, session_key, theme):
    if request.method == "POST":
        if email == "example@basicaccounting.co.uk":
            pass
        else:
            user_email = request.form["user_email"]
            old_password = request.form["old_password"]
            new_password = request.form["new_password"]
            new_password2 = request.form["new_password2"]
            if new_password != new_password2:
                return render_template(
                    "changePassword.html",
                    company=company,
                    email=email,
                    message="These passwords do not match. Please try again with matching passwords",
                    design=theme,
                )
            else:
                user = Users.query.filter_by(
                    company=company, email=user_email).first()
                if pbkdf2_sha256.verify(old_password, user.password):
                    user.password = pbkdf2_sha256.hash(new_password)
                    db.session.commit()
                else:
                    return render_template(
                        "changePassword.html",
                        company=company,
                        email=email,
                        message="This password does not match the email. No passwords have been changed",
                        design=theme,
                    )

            return render_template(
                "changePassword.html", company=company, email=email, message="Your password has been changed", design=theme
            )
    return render_template("changePassword.html", company=company, email=email, message="", design=theme)


@app.route("/<company>/<email>/<username>/<session_key>/trialBalance", methods=["POST", "GET"])
@login_required
def trialBalance(company, email, username, session_key, theme):

    accounts = ChartOfAccounts.query.filter_by(
        company=company).order_by(ChartOfAccounts.nominal).all()
    return render_template("trialBalance.html", company=company, accounts=accounts, design=theme)


@app.route("/<company>/<email>/<username>/<session_key>/balanceSheet", methods=["POST", "GET"])
@login_required
def balanceSheet(company, email, username, session_key, theme):
    company_data = db.session.query(Companies).filter(
        Companies.company == company).first()
    current_year = company_data.accounting_year
    current_period = company_data.accounting_period


    if request.method == "POST":
        current_period = request.form['selected_period']
        current_year = request.form['selected_year']


    accounts = (
        db.session.query(ChartOfAccounts)
        .filter(ChartOfAccounts.company == company)
        .filter(ChartOfAccounts.nominal >= 60000)
    ).order_by(ChartOfAccounts.nominal).all()

    data = {}

    for account in accounts:
        monthly_balance = 0
        ytd_balance = 0
        transactions = (
            db.session.query(NominalTransactions)
            .filter(NominalTransactions.company == company)
            .filter(NominalTransactions.nominal_code == account.nominal)
            .filter(NominalTransactions.accounting_year <= current_year)
            .filter(NominalTransactions.accounting_period <= current_period)
        )

        for transaction in transactions:
            if transaction.accounting_period == current_period:
                monthly_balance += transaction.net_value
            else:
                pass
            ytd_balance += transaction.net_value

        data[account.nominal] = [monthly_balance, ytd_balance,
                                 account.nominal, account.account_name]
    return render_template("balanceSheet.html", company=company, data=data, design=theme)


@app.route("/<company>/<email>/<username>/<session_key>/profitAndLoss", methods=["POST", "GET"])
@login_required
def profitAndLoss(company, email, username, session_key, theme):
    company_data = db.session.query(Companies).filter(
        Companies.company == company).first()
    current_year = company_data.accounting_year
    current_period = company_data.accounting_period

    if request.method == "POST":
        current_year = request.form["selected_year"]
        current_period = request.form["selected_period"]

    accounts = (
        db.session.query(ChartOfAccounts)
        .filter(ChartOfAccounts.company == company)
        .filter(ChartOfAccounts.nominal < 60000)
    ).order_by(ChartOfAccounts.nominal)

    data = {}

    for account in accounts:
        monthly_balance = 0
        ytd_balance = 0
        
        transactions = NominalTransactions.query.filter(
            NominalTransactions.company == company,
            NominalTransactions.nominal_code == account.nominal,
            NominalTransactions.accounting_year == current_year,
            NominalTransactions.to_post not in [1, "1"]
        ).all()

        for transaction in transactions:
            # Filtering here as using the filter in the query didnt work
            # I think becuase using <= with strings but not sure
            if int(transaction.accounting_period) <= int(current_period):

                if transaction.accounting_period == current_period:
                    if transaction.transaction_type == "journal" and account.nominal < 20000:
                        monthly_balance -= transaction.net_value
                    else:
                        monthly_balance += transaction.net_value
            
    
                if transaction.transaction_type == "journal" and account.nominal < 20000:
                    ytd_balance -= transaction.net_value
                else:
                    ytd_balance += transaction.net_value
            budget = Budgets.query.filter_by(
                company=company, nominal_code=account.nominal, year=current_year
            ).all()

            ytd_budget = 0
            if budget:

                for val in budget:
                    if int(val.period) == int(current_period):
                        budget_value = val.value
                    if int(val.period) <= int(current_period):
                        ytd_budget += val.value
            else:
                budget_value = 0

            data[account.account_name] = [monthly_balance,
                                        ytd_balance, account.nominal,
                                        budget_value, ytd_budget]

    return render_template(
        "profitAndLoss.html",
        company=company,
        data=data,
        accounting_year=current_year,
        accounting_period=current_period,
        design=theme,
    )


@app.route("/<company>/<email>/<username>/<session_key>/nominalTransactions", methods=["POST", "GET"])
@login_required
def nominalTransactions(company, email, username, session_key, theme):
    transactions = NominalTransactions.query.filter_by(company=company)

    if request.method == "POST":
        transaction_type = request.form["type"]
        client_code = request.form["client_code"]
        nominal_code = request.form["nominal_code"]
        selected_year = request.form["year"]
        selected_period = request.form["period"]

        if transaction_type != "all":
            transactions = [
                transaction for transaction in transactions if transaction.transaction_type == transaction_type
            ]
        if selected_year != "all":
            transactions = [
                transaction for transaction in transactions if transaction.accounting_year == selected_year]
        if selected_period != "all":
            transactions = [
                transaction for transaction in transactions if transaction.accounting_period == selected_period
            ]
        if client_code != "":
            transactions = [
                transaction for transaction in transactions if transaction.client_code == client_code]

        if nominal_code != "":

            transactions = [
                transaction for transaction in transactions if transaction.nominal_code == int(nominal_code)]

        return render_template("nominalTransactions.html", company=company, transactions=transactions, design=theme)
    return render_template("nominalTransactions.html", company=company, transactions=transactions, design=theme)


@app.route("/<company>/<email>/<username>/<session_key>/batchedJournals", methods=["POST", "GET"])
@login_required
def batchedJournals(company, email, username, session_key, theme):
    journals = NominalTransactions.query.filter_by(
        company=company, transaction_type="journal", to_post=1).all()

    if request.method == "POST":
        company_data = db.session.query(Companies).filter(
            Companies.company == company).first()
        current_year = company_data.accounting_year
        current_period = company_data.accounting_period

        for journal in journals:
            journal.to_post = 0
            journal.date = dt.datetime.today().strftime("%Y-%m-%d")
            journal.posted_on = dt.datetime.today().strftime("%Y-%m-%d")
            journal.posted_by = username
            journal.accounting_period = current_period
            journal.accounting_year = current_year
        db.session.commit()

        journals = NominalTransactions.query.filter_by(
            company=company, transaction_type="journal", to_post=1).all()

        return render_template("batchedJournals.html", company=company, journals=journals, design=theme)

    return render_template("batchedJournals.html", company=company, journals=journals, design=theme)


@app.route("/<company>/<email>/<username>/<session_key>/changeTheme", methods=["POST", "GET"])
@login_required
def changeTheme(company, email, username, session_key, theme):
    user = Users.query.filter_by(company=company, email=email).first()
    print(user.designTheme)
    theme = user.designTheme

    if request.method == "POST":
        primary = request.form["primary"]
        second = request.form["second"]
        third = request.form["third"]
        text = request.form["text"]
        combined = ",".join([primary, second, third, text])
        user.designTheme = combined
        db.session.commit()

        theme = user.designTheme
        print(theme)
        return render_template("changeTheme.html", company=company, design=combined)

    return render_template("changeTheme.html", company=company, design=theme)


@app.route("/<company>/<email>/<username>/<session_key>/budget", methods=["POST", "GET"])
@login_required
def budget(company, email, username, sesion_key, theme):
    accounts = ChartOfAccounts.query.filter_by(company=company).all()
    uploadedData = {}
    if request.method == "POST":
        if request.files:
            file = request.files["file"]
            uploadedData = pd.read_excel(file, index_col=0)

            d = {}
            for i in uploadedData.index:
                d[i] = uploadedData.loc[i, :].values.flatten().tolist()
            uploadedData = d
            return render_template("budget.html", company=company, accounts=accounts, design=theme, data=uploadedData)
        else:
            year = request.form["year"]
            for cell, value in request.form.items():
                if cell == "year":
                    pass
                else:
                    nominal = cell[:5]
                    period = cell[6:]
                    value = value if value != "" else 0.00
                    if (
                        Budgets.query.filter_by(
                            company=company, year=year, period=period, nominal_code=nominal).first()
                        is not None
                    ):
                        Budgets.query.filter_by(
                            company=company, year=year, period=period, nominal_code=nominal
                        ).first().value = value
                    else:
                        data = Budgets(company=company, year=year,
                                    nominal_code=nominal, period=period, value=value)
                        db.session.add(data)

            db.session.commit()

    return render_template("budget.html", company=company, accounts=accounts, design=theme, data=uploadedData)


@app.route("/<company>/<email>/<username>/<session_key>/help", methods=["POST", "GET"])
@login_required
def help(company, email, username, session_key, theme):
    return render_template("helpPage.html", company=company, design=theme)


@app.route("/<company>/<email>/<username>/<session_key>/bankRec", methods=["POST", "GET"])
@login_required
def bankRec(company, email, username, session_key, theme):
    data = NominalTransactions.query.filter(
        NominalTransactions.company == company,
        NominalTransactions.is_paid == "False",
        NominalTransactions.transaction_type != "journal",
    ).all()
    
    # convert data to dict
    d = {}
    row=0
    for i in data:
        d[row] = [i.id, i.transaction_type, i.client_code, i.transaction_number, i.description, i.total_value]
        row += 1
    company_data = Companies.query.filter_by(company=company).first()
    accounting_year = company_data.accounting_year
    accounting_period = company_data.accounting_period

    if request.method == "POST":

        number_of_rows = int(request.form["rows"])

        bank_account = ChartOfAccounts.query.filter(
            ChartOfAccounts.company == company, ChartOfAccounts.nominal == 60000).first()
        cash_account = ChartOfAccounts.query.filter(
            ChartOfAccounts.company == company, ChartOfAccounts.nominal == 60010).first()

        for i in range(1, number_of_rows + 1):
            print(i)
            try:
                print(request.form)
                transaction_type = request.form[f"row_{str(i)}_type"]
                client_code = request.form[f"row_{str(i)}_client"]
                transaction_number = request.form[f"row_{str(i)}_invoiceNo"]
                total_value = request.form[f"row_{str(i)}_value"]

                print(transaction_type)
                print("-")
                print(client_code)
                print(transaction_number)
                print(total_value)
                print("--")

                actual_invoice = NominalTransactions.query.filter_by(
                    company=company,
                    client_code=client_code,
                    transaction_type=transaction_type,
                    transaction_number=int(transaction_number),
                ).all()

                print(actual_invoice)
                
                for invoice in actual_invoice:
                    invoice.is_paid = "True"

                new_nominal_transaction = NominalTransactions(
                    company=company,
                    transaction_type="payment",
                    client_code=client_code,
                    transaction_number=transaction_number,
                    date=dt.datetime.today().strftime("%Y-%m-%d"),
                    nominal_code=60000,
                    net_value=total_value,
                    vat_value=0,
                    total_value=total_value,
                    posted_on=dt.datetime.today().strftime("%Y-%m-%d"),
                    posted_by=username,
                    reference="",
                    accounting_year=accounting_year,
                    accounting_period=accounting_period,
                    is_paid="True",
                )

                db.session.add(new_nominal_transaction)

                # Reduce balance of outstanding cash (The Cash GL)
                # and increase balance of bank account
                # Treat sales & purchase invoices in opposite ways
                if "sales" in transaction_type:
                    bank_account.balance = bank_account.balance + \
                        float(total_value)
                    cash_account.balance = cash_account.balance - \
                        float(total_value)
                else:
                    bank_account.balance = bank_account.balance - \
                        float(total_value)
                    cash_account.balance = cash_account.balance + \
                        float(total_value)
                db.session.commit()
            # Row not included in bank rec
            except Exception as e:
                print(e)

        db.session.commit()
        data = NominalTransactions.query.filter(
            NominalTransactions.company == company,
            NominalTransactions.is_paid == "False",
            NominalTransactions.transaction_type != "journal",
        ).all()
        
        # convert data to dict
        d = {}
        row=0
        for i in data:
            d[row] = [i.id, i.transaction_type, i.client_code, i.transaction_number, i.description, i.total_value]
            row += 1
        return render_template("bankRec.html", company=company, design=theme, data=d)

    return render_template("bankRec.html", company=company, design=theme, data=d)


@app.route("/<company>/<email>/<username>/<session_key>/agedDebt", methods=["POST", "GET"])
@login_required
def agedDebt(company, email, username, session_key, theme):
    # Loop through sales_invoices that have not been paid
    # This is determined by is_paid being False
    # is_paid becomes True when a bank rec is completed and the invoice as marked off

    transactions = NominalTransactions.query.filter(
        NominalTransactions.company == company,
        NominalTransactions.is_paid == "False",
        NominalTransactions.transaction_type == "sales_invoice",
    ).all()
    clients = set([client.client_code for client in transactions])

    data = {}
    for client in clients:
        data[client] = [0, 0, 0, 0, 0]

    # Used to calculate age of unpaid invoices
    today = dt.datetime.today()
    for i in transactions:
        # Split data up into 0-30, 31-60, 61-90, 91-120, 121+
        days_aged = (today - dt.datetime.strptime(i.date, "%Y-%m-%d")).days
        if days_aged < 31:
            age = "0-30"
            data[i.client_code][0] += i.net_value
        elif days_aged < 61:
            age = "31-60"
            data[i.client_code][1] += i.net_value
        elif days_aged < 91:
            age = "61-90"
            data[i.client_code][2] += i.net_value
        elif days_aged < 121:
            age = "90-120"
            data[i.client_code][3] += i.net_value
        else:
            age = "121+"
            data[i.client_code][4] += i.net_value

    return render_template("agedDebt.html", company=company, design=theme, data=data)


# When logging out, the user is redirected to the index page
# This is via the logout page where the session for this user is deleted
@app.route("/<company>/<email>/<username>/<session_key>/logout", methods=["POST", "GET"])
@login_required
def logout(company, email, username, session_key, theme):
    del session[email]
    return redirect(url_for("index"))


# Cash flow statement
@app.route("/<company>/<email>/<username>/<session_key>/cashFlow")
@login_required
def cashFlow(company, email, username, sesion_key, theme):
    # Find this company's current accounting year to use later
    company_data = Companies.query.filter(Companies.company == company).first()
    accounting_year = company_data.accounting_year

    # Find the company's current bank account balance
    # We will minus this year's transactions from their current bank balance
    # This will be to calculate this years cash flow as well as their opening balance
    # Calculate the closing balance by adding all bsheet accounts balances together
    closingBalanceAccounts = ChartOfAccounts.query.filter(ChartOfAccounts.company == company,
                                                          ChartOfAccounts.nominal >= 60000).all()
    closingBalance = 0
    for transaction in closingBalanceAccounts:
        closingBalance += transaction.balance

    # Collect all nominal transactions of this company that have hit the P&L this year
    # Including journals
    currentYearTransactions = NominalTransactions.query.filter(NominalTransactions.company == company,
                                                               NominalTransactions.accounting_year == accounting_year,
                                                               NominalTransactions.nominal_code < 60000
                                                               ).all()

    # Cash Flow statements are made up of 3 sections:
    # Operating Activities
    # Investing Activities
    # Financing Activities

    openingBalance = closingBalance
    operating_activities = 0
    investing_activities = 0
    financing_activities = 0
    # Start with current balance, loop through this years tarnsactions and minus them from the closing balance
    for transaction in currentYearTransactions:

        # Investing activities go into 4**** nominal codes
        # e.g. Purchase of property, sale of securities, re-purchase of securities
        # Put this in to investing activies
        if 50000 > transaction.nominal_code >= 40000:
            investing_activities -= transaction.net_value
            openingBalance += transaction.net_value

        # Financing activities go into 5**** nominal codes
        # e.g. tax, interest, depreciation, amortisation
        # Put this in to financing activies
        elif 60000 > transaction.nominal_code >= 50000:
            financing_activities -= transaction.net_value
            openingBalance += transaction.net_value

        # If the transaction is revenue, add it to operating activies, minus it from closing balance
        elif transaction.nominal_code < 20000:
            operating_activities += transaction.net_value
            openingBalance = openingBalance - transaction.net_value

        # If the transaction is a cost (but not financing), minus it from operating activies, add it to closing balance
        elif transaction.nominal_code < 40000:
            operating_activities -= transaction.net_value
            openingBalance = openingBalance + transaction.net_value

    return render_template("cashFlow.html", company=company, design=theme, openingBalance=openingBalance, closingBalance=closingBalance,
                           operating_activities=operating_activities, financing_activities=financing_activities, investing_activities=investing_activities,
                           accounting_year=accounting_year)

@app.route("/<company>/<email>/<username>/<session_key>/salesHub")
@login_required
def salesHub(company, email, username, session_key, theme):
    sales_products = SalesHubProducts.query.filter(SalesHubProducts.company==company).all()
    
    return render_template("salesHubDashboard.html", company=company, design=theme, sales_products=sales_products)

@app.route("/<company>/<email>/<username>/<session_key>/salesHubAddProduct", methods=["POST", "GET"])
@login_required
def salesHubAddProduct(company, email, username, session_key, theme):
    
    if request.method == "POST":
        print(request.form)
        product_name = request.form['name']
        product_description = request.form['description']
        product_net_price = request.form['netPrice']
        product_vat_price = request.form['vatPrice']
        product_image = request.form['image']
        
        newProduct = SalesHubProducts(company=company, product_name=product_name,
                                      product_description=product_description, product_net_price=product_net_price,
                                      product_vat_price=product_vat_price, product_image=product_image)
        db.session.add(newProduct)
        db.session.commit()
    
    return render_template("salesHubaddProduct.html", company=company, design=theme)

# This login leads to the sales hub for clients
@app.route("/salesHubLogin", methods=['POST', 'GET'])
def salesHubLogin():
    return render_template("salesHubLogin.html")

# This is the sales hub that clients visit to place orders
@app.route("/salesHub/<link>", methods=['POST', 'GET'])
def salesHubClientSide(link):
    products = SalesHubProducts.query.filter().all()
    
    return render_template("salesHubClientSide.html", products=products)


debug = os.getenv("DEBUG")
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=debug)
