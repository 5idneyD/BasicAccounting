from flask import Flask, render_template, request, redirect, url_for, session, g
from flask_migrate import Migrate
# from passlib.hash import pbkdf2_sha256 as sha256
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import datetime as dt


app = Flask(__name__)

# Current files path to create absolute path
basedir = os.path.abspath(os.path.dirname(__file__))


# Using sqlite3 db
# Secret key changes for each new session; improves security
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + \
    os.path.join(basedir, "./database/database.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SESSION_PERMANENT'] = False
app.config['SECRET_KEY'] = os.urandom(12).hex()
app.secret_key = os.urandom(12).hex()


db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Companies(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    company = db.Column(db.String(40))
    admin_email = db.Column(db.String(40))
    admin_password = db.Column(db.String(40))
    accounting_year = db.Column(db.String(4))
    accounting_period = db.Column(db.String(4))


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    company = db.Column(db.String(40))
    username = db.Column(db.String(40))
    email = db.Column(db.String(40))
    password = db.Column(db.String(40))
    admin = db.Column(db.String(1))

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


class Suppliers(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    company = db.Column(db.String(40))
    supplier_name = db.Column(db.String(40))
    supplier_code = db.Column(db.String(6))


class SalesInvoices(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    company = db.Column(db.String(40))
    customer_code = db.Column(db.String(40))
    invoice_number = db.Column(db.Integer, nullable=False)
    invoice_date = db.Column(db.String(40))
    nominal_code = db.Column(db.Integer)
    description = db.Column(db.String(40), nullable=False)
    net_value = db.Column(db.Float)
    vat_value = db.Column(db.Float)
    total_value = db.Column(db.Float)
    date_posted = db.Column(db.String(40))
    user_posted = db.Column(db.String(40))
    reference = db.Column(db.String(50))
    accounting_year = db.Column(db.String(4))
    accounting_period = db.Column(db.String(4))


class PurchaseInvoices(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    company = db.Column(db.String(40))
    supplier_code = db.Column(db.String(40))
    invoice_number = db.Column(db.Integer, nullable=False)
    invoice_date = db.Column(db.String(40))
    nominal_code = db.Column(db.Integer)
    description = db.Column(db.String(40), nullable=False)
    net_value = db.Column(db.Float)
    vat_value = db.Column(db.Float)
    total_value = db.Column(db.Float)
    date_posted = db.Column(db.String(40))
    user_posted = db.Column(db.String(40))
    accounting_year = db.Column(db.String(4))
    accounting_period = db.Column(db.String(4))


class Journals(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    company = db.Column(db.String(40))
    journal_number = db.Column(db.Integer)
    journal_date = db.Column(db.String(40))
    journal_description = db.Column(db.String(40))
    nominal_code = db.Column(db.Integer)
    description = db.Column(db.String(40), nullable=False)
    debit = db.Column(db.Float)
    credit = db.Column(db.Float)
    posted_by = db.Column(db.String(40))
    posted_on = db.Column(db.String(40))
    accounting_year = db.Column(db.String(4))
    accounting_period = db.Column(db.String(4))


class NominalTransactions(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    company = db.Column(db.String(40))
    transaction_type = db.Column(db.String(40))
    client_code = db.Column(db.String(40))
    transaction_number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(40))
    description = db.Column(db.String(40))
    nominal_code = db.Column(db.Integer)
    description = db.Column(db.String(40), nullable=False)
    debit = db.Column(db.Float)
    credit = db.Column(db.Float)
    net_value = db.Column(db.Float)
    vat_value = db.Column(db.Float)
    total_value = db.Column(db.Float)
    posted_by = db.Column(db.String(40))
    posted_on = db.Column(db.String(40))
    accounting_year = db.Column(db.String(4))
    accounting_period = db.Column(db.String(4))
    reference = db.Column(db.String(50))


with app.app_context():
    db.create_all()


@app.errorhandler(Exception)
def not_found(e):
    return render_template("error.html", error=e)


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=20)
    session.modified = True


@app.route("/")
def index():
    return render_template("index.html", message="Hello Flask")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        users = Users.query.filter_by(email=email).all()

        # each user contains id, company, email & password
        for user in users:
            if user.password == password:
                session[email] = os.urandom(12).hex()
                return redirect(url_for("dashboard", company=user.company,
                                        email=email, username=user.username, session_key=session[email]))

    return render_template("login.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():

    if request.method == "POST":
        company_name = request.form["company"]
        company_email = request.form["email"]
        company_password = request.form["password"]
        accounting_year = request.form["accounting_year"]
        accounting_period = request.form["accounting_period"]

        new_company = Companies(
            company=company_name, admin_email=company_email, admin_password=company_password, accounting_year=accounting_year, accounting_period=accounting_period)
        db.session.add(new_company)
        new_admin = Users(company=company_name, email=company_email, username=company_email,
                          password=company_password, admin="3")
        db.session.add(new_admin)
        db.session.commit()

        session[company_email] = os.urandom(12).hex()
        return redirect(url_for("admin", company=company_name, email=company_email, username="Admin", session_key=session[company_email]))
    return render_template("signup.html")


@app.route("/<company>/<email>/<username>/<session_key>/admin", methods=["POST", "GET"])
def admin(company, email, username, session_key):

    company_data = Companies.query.filter_by(company=company).first()
    accounting_year = company_data.accounting_year
    accounting_period = company_data.accounting_period
    permission_level = Users.query.filter_by(
        company=company, email=email).first().admin

    try:
        if session[email] == session_key:
            if request.method == "POST":
                if "addUserForm" in request.form:
                    new_name = request.form["name"]
                    new_email = request.form["email"]
                    new_password = request.form["password"]
                    admin_permission = "1"
                    admin_permission = request.form['adminLevel']
                    print(admin_permission)
                    new_user = Users(company=company, username=new_name, email=new_email,
                                     password=new_password, admin=admin_permission)
                    db.session.add(new_user)
                    db.session.commit()

                elif "addNominalForm" in request.form:
                    print("nominal account")
                    nominal = request.form["nominal"]
                    account_name = request.form["accountName"]
                    new_nominal = ChartOfAccounts(
                        company=company, nominal=nominal, account_name=account_name)
                    db.session.add(new_nominal)
                    db.session.commit()

                elif "removeUserForm" in request.form:
                    user_email = request.form['email']
                    user = Users.query.filter_by(
                        email=user_email, company=company).first()
                    db.session.delete(user)
                    db.session.commit()

                elif "closePeriodForm" in request.form:
                    current_period = request.form["period"]
                    current_year = request.form["year"]
                    if current_period == "12":
                        new_period = "1"
                        new_year = str(int(current_year) + 1)
                        company_data.accounting_period = new_period
                        company_data.accounting_year = new_year
                    else:
                        new_period = str(int(current_period) + 1)
                        company_data.accounting_period = new_period

                    db.session.commit()
                    company_data = Companies.query.filter_by(
                        company=company).first()
                    accounting_year = company_data.accounting_year
                    accounting_period = company_data.accounting_period
                    return render_template("admin.html", company=company, email=email, admin=permission_level, accounting_year=accounting_year, accounting_period=accounting_period)
                else:
                    pass

            return render_template("admin.html", company=company, email=email, admin=permission_level, accounting_year=accounting_year, accounting_period=accounting_period)

    except KeyError:
        return redirect(url_for("login"))

    return render_template("admin.html", company=company, email=email, admin=permission_level, accounting_year=accounting_year, accounting_period=accounting_period)


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

            accounts = ChartOfAccounts.query.filter_by(company=company).all()

            return render_template("chartOfACcounts.html", company=company, email=email, username=username, session_sey=session_key, accounts=accounts)
        else:
            return redirect(url_for("login"))
    except KeyError:
        # Username is not in session
        return redirect(url_for("login"))
    return 0


@app.route("/<company>/<email>/<username>/<session_key>/Customers", methods=["POST", "GET"])
def customers(company, email, username, session_key):

    try:
        if session[email] == session_key:
            customers = Customers.query.filter_by(company=company).all()
            return render_template("customers.html", company=company, email=email, username=username, session_key=session_key, customers=customers)
        else:
            return redirect(url_for("login"))
    except KeyError:
        return redirect(url_for("login"))
    return 0


@app.route("/<company>/<email>/<username>/<session_key>/addCustomer", methods=["POST", "GET"])
def addCustomer(company, email, username, session_key):

    try:
        if session[email] == session_key:

            if request.method == "POST":
                customer_name = request.form['customer_name']
                customer_code = request.form['customer_code']
                customer = Customers(
                    company=company, customer_name=customer_name, customer_code=customer_code)
                db.session.add(customer)
                db.session.commit()

            return render_template("addCustomer.html", company=company, email=email, username=username, session_key=session_key)
        else:
            return redirect(url_for("login"))
    except KeyError:
        return redirect(url_for("login"))


@app.route("/<company>/<email>/<username>/<session_key>/Suppliers", methods=["POST", "GET"])
def suppliers(company, email, username, session_key):

    try:
        if session[email] == session_key:

            suppliers = Suppliers.query.filter_by(company=company).all()
            return render_template("suppliers.html", company=company, email=email, username=username, session_key=session_key, suppliers=suppliers)
        else:
            return redirect(url_for("login"))
    except KeyError:
        return redirect(url_for("login"))


@app.route("/<company>/<email>/<username>/<session_key>/addSupplier", methods=["POST", "GET"])
def addSupplier(company, email, username, session_key):

    try:
        if session[email] == session_key:

            if request.method == "POST":
                supplier_name = request.form['supplier_name']
                supplier_code = request.form['supplier_code']
                supplier = Suppliers(
                    company=company, supplier_name=supplier_name, supplier_code=supplier_code)
                db.session.add(supplier)
                db.session.commit()

            return render_template("addSupplier.html", company=company, email=email, username=username, session_key=session_key)
        else:
            return redirect(url_for("login"))
    except KeyError:
        return redirect(url_for("login"))


@app.route("/<company>/<email>/<username>/<session_key>/addSalesInvoice", methods=["POST", "GET"])
def addSalesInvoice(company, email, username, session_key):

    try:
        if session[email] == session_key:
            customers = Customers.query.filter_by(company=company).all()
            invoices = SalesInvoices.query.filter_by(company=company).all()
            company_data = Companies.query.filter_by(company=company).first()
            accounting_year = company_data.accounting_year
            accounting_period = company_data.accounting_period
            references = []
            for invoice in invoices:
                references.append(str(invoice.reference))

            if request.method == "POST":
                invoice_number = request.form['invoice_number']
                invoice_date = request.form['invoice_date']
                customer_code = request.form['customer_code']
                number_of_rows = request.form['number_of_rows']

                for i in range(1, int(number_of_rows)+1):
                    row = str(i)
                    nominal_code = request.form[row+"_nominal_code"]
                    description = request.form[row+"_description"]
                    net_value = request.form[row+"_net_value"]
                    vat = request.form[row+"_vat"]
                    total_value = request.form[row+"_total_value"]
                    reference = company+str(invoice_number)

                    new_invoice = SalesInvoices(company=company, customer_code=customer_code,
                                                invoice_number=invoice_number, invoice_date=invoice_date,
                                                nominal_code=nominal_code, description=description,
                                                net_value=net_value, vat_value=vat, total_value=total_value,
                                                date_posted=dt.datetime.today().strftime("%Y-%m-%d"),
                                                user_posted=username, reference=reference,
                                                accounting_year=accounting_year, accounting_period=accounting_period)

                    new_nominal_transaction = NominalTransactions(company=company, transaction_type="sales_invoice",
                                                                  client_code=customer_code,
                                                                  transaction_number=invoice_number, date=invoice_date,
                                                                  nominal_code=nominal_code, description=description,
                                                                  net_value=net_value, vat_value=vat, total_value=total_value,
                                                                  posted_on=dt.datetime.today().strftime("%Y-%m-%d"),
                                                                  posted_by=username, reference=reference,
                                                                  accounting_year=accounting_year, accounting_period=accounting_period)

                    db.session.add(new_invoice)
                    db.session.add(new_nominal_transaction)
                    account = ChartOfAccounts.query.filter_by(
                        company=company, nominal=nominal_code).first()
                    account.balance = account.balance-float(net_value)
                db.session.commit()

                return render_template("addSalesInvoice.html", company=company, email=email, username=username, session_key=session_key, customers=customers, references=references)
            return render_template("addSalesInvoice.html", company=company, email=email, username=username, session_key=session_key, customers=customers, references=references)
        else:
            return redirect(url_for("login"))
    except KeyError:
        return redirect(url_for("login"))


@app.route("/<company>/<email>/<username>/<session_key>/addPurchaseInvoice", methods=["POST", "GET"])
def addPurchaseInvoice(company, email, username, session_key):

    try:
        if session[email] == session_key:
            suppliers = Suppliers.query.filter_by(company=company).all()
            company_data = Companies.query.filter_by(company=company).first()
            accounting_year = company_data.accounting_year
            accounting_period = company_data.accounting_period

            if request.method == "POST":
                invoice_number = request.form['invoice_number']
                invoice_date = request.form['invoice_date']
                supplier_code = request.form['supplier_code']
                number_of_rows = request.form['number_of_rows']

                for i in range(1, int(number_of_rows)+1):
                    row = str(i)
                    nominal_code = request.form[row+"_nominal_code"]
                    description = request.form[row+"_description"]
                    net_value = request.form[row+"_net_value"]
                    vat = request.form[row+"_vat"]
                    total_value = request.form[row+"_total_value"]

                    new_invoice = PurchaseInvoices(company=company, supplier_code=supplier_code,
                                                   invoice_number=invoice_number, invoice_date=invoice_date,
                                                   nominal_code=nominal_code, description=description,
                                                   net_value=net_value, vat_value=vat, total_value=total_value,
                                                   date_posted=dt.datetime.today().strftime("%Y-%m-%d"), user_posted=username,
                                                   accounting_year=accounting_year, accounting_period=accounting_period)
                    
                    new_nominal_transaction = NominalTransactions(company=company, transaction_type="purchase_invoice",
                                                                  client_code=supplier_code,
                                                                  transaction_number=invoice_number, date=invoice_date,
                                                                  nominal_code=nominal_code, description=description,
                                                                  net_value=net_value, vat_value=vat, total_value=total_value,
                                                                  posted_on=dt.datetime.today().strftime("%Y-%m-%d"),
                                                                  posted_by=username, reference="",
                                                                  accounting_year=accounting_year, accounting_period=accounting_period)
                   
                    db.session.add(new_invoice)
                    db.session.add(new_nominal_transaction)
                    account = ChartOfAccounts.query.filter_by(
                        company=company, nominal=nominal_code).first()
                    account.balance = account.balance+float(net_value)
                db.session.commit()

            return render_template("addPurchaseInvoice.html", company=company, email=email, username=username, session_key=session_key, suppliers=suppliers)
        else:
            return redirect(url_for("login"))
    except KeyError:
        return redirect(url_for("login"))


@app.route("/<company>/<email>/<username>/<session_key>/viewSalesInvoices", methods=["POST", "GET"])
def viewSalesInvoices(company, email, username, session_key):
    try:
        if session[email] == session_key:
            invoices = SalesInvoices.query.filter_by(company=company).all()

            return render_template("viewSalesInvoices.html", company=company, invoices=invoices)
        else:
            return redirect(url_for("login"))
    except KeyError:
        return redirect(url_for("login"))


@app.route("/<company>/<email>/<username>/<session_key>/viewPurchaseInvoices", methods=["POST", "GET"])
def viewPurchaseInvoices(company, email, username, session_key):
    try:
        if session[email] == session_key:
            invoices = PurchaseInvoices.query.filter_by(company=company).all()

            return render_template("viewPurchaseInvoices.html", company=company, invoices=invoices)
        else:
            return redirect(url_for("login"))
    except KeyError:
        return redirect(url_for("login"))


@app.route("/<company>/<email>/<username>/<session_key>/journal", methods=["POST", "GET"])
def journal(company, email, username, session_key):
    try:
        if session[email] == session_key:
            if request.method == "POST":
                journal_date = str(request.form['journalDate'])
                journal_description = request.form["journalDescription"]
                debitTotal = request.form["debitTotal"]
                creditTotal = request.form["creditTotal"]
                number_of_rows = request.form["number_of_rows"]
                print(int(number_of_rows) + 1)

                for i in range(1, int(number_of_rows)+1):
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

                    print(i, debit, credit)
                    if debit == 0.00 and credit == 0.00:
                        pass
                    else:
                        new_journal = Journals(company=company, journal_date=journal_date,
                                               journal_description=journal_description,
                                               nominal_code=nominal_code, description=description,
                                               debit=debit, credit=credit, posted_by=username)
                        
                        
                        new_nominal_transaction = NominalTransactions(company=company, transaction_type="journal",
                                                                  client_code="Journal",
                                                                  transaction_number=invoice_number, date=invoice_date,
                                                                  nominal_code=nominal_code, description=description,
                                                                  net_value=net_value, vat_value=vat, total_value=total_value,
                                                                  posted_on=dt.datetime.today().strftime("%Y-%m-%d"),
                                                                  posted_by=username, reference="",
                                                                  accounting_year=accounting_year, accounting_period=accounting_period)
                                         
                        
                        
                        db.session.add(new_journal)

                        account = ChartOfAccounts.query.filter_by(
                            company=company, nominal=nominal_code).first()
                        account.balance += debit
                        account.balance -= credit

                db.session.commit()

                return render_template("journal.html", company=company)

            return render_template("journal.html", company=company)
        else:
            return redirect(url_for("login"))
    except KeyError:
        return redirect(url_for("login"))


@app.route("/<company>/<email>/<username>/<session_key>/changePassword", methods=["POST", "GET"])
def changePassword(company, email, username, session_key):

    try:
        if session[email] == session_key:
            if request.method == "POST":
                user_email = request.form["user_email"]
                old_password = request.form["old_password"]
                new_password = request.form["new_password"]
                new_password2 = request.form["new_password2"]
                if new_password != new_password2:
                    return render_template("changePassword.html", company=company, email=email, message="These passwords do not match. Please try again with matching passwords")
                else:
                    user = Users.query.filter_by(
                        company=company, email=user_email).first()
                    if user.password == old_password:
                        user.password = new_password
                        db.session.commit()
                    else:
                        return render_template("changePassword.html", company=company, email=email, message="This password does not match the email. No passwords have been changed")

                return render_template("changePassword.html", company=company, email=email, message="Your password has been changed")
            return render_template("changePassword.html", company=company, email=email, message="")
        else:
            return redirect(url_for("login"))
    except KeyError:
        return redirect(url_for("login"))


@app.route("/<company>/<email>/<username>/<session_key>/trialBalance", methods=["POST", "GET"])
def trialBalance(company, email, username, session_key):
    try:
        if session[email] == session_key:
            accounts = ChartOfAccounts.query.filter_by(company=company).all()

            return render_template("trialBalance.html", company=company, accounts=accounts)
    except KeyError:
        return redirect(url_for("login"))


@app.route("/<company>/<email>/<username>/<session_key>/balanceSheet", methods=["POST", "GET"])
def balanceSheet(company, email, username, session_key):

    try:
        if session[email] == session_key:
            data = ChartOfAccounts.query.filter_by(company=company).all()
            totalAssets = 0
            totalLiabilities = 0
            for account in data:
                if account.nominal < 60000:
                    pass
                elif account.nominal < 70000:
                    totalAssets += account.balance
                else:
                    totalLiabilities -= account.balance
            return render_template("balanceSheet.html", company=company, data=data, totalAssets=totalAssets, totalLiabilities=totalLiabilities)
        else:
            return redirect(url_for("login"))
    except KeyError:
        return redirect(url_for("login"))


@app.route("/<company>/<email>/<username>/<session_key>/profitAndLoss", methods=["POST", "GET"])
def profitAndLoss(company, email, username, session_key):
    try:
        if 1 == 1:

            company_data = db.session.query(Companies).filter(
                Companies.company == company).first()
            current_year = company_data.accounting_year
            current_period = company_data.accounting_period

            accounts = db.session.query(ChartOfAccounts).filter(ChartOfAccounts.company == company).filter(
                ChartOfAccounts.nominal < 60000)

            data = {}

            for account in accounts:
                monthly_balance = 0
                ytd_balance = 0
                transactions = db.session.query(NominalTransactions).filter(NominalTransactions.company == company).filter(NominalTransactions.nominal_code==account.nominal).filter(NominalTransactions.accounting_year==current_year)

                for transaction in transactions:
                    if transaction.accounting_period == current_period:
                        monthly_balance += transaction.total_value
                    else:
                        pass
                    ytd_balance += transaction.total_value

                print(account.account_name, monthly_balance, ytd_balance)


                data[account.account_name] = [
                    monthly_balance, ytd_balance, account.nominal]

            return render_template("profitAndLoss.html", company=company, data=data)
        else:
            return redirect(url_for("login"))
    except KeyError:
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
