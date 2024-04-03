import sys
from os import path
sys.path.append(path.abspath("."))
sys.path.append(path.abspath("./components/"))

from flask import *
import requests
from datetime import datetime
from passlib.hash import sha256_crypt as sha256

# Import components
from components.branch_db import Cursor, branch_name, get_report_data, branch_address, branch_port
from components.base import *
from components.inventory import inv
from components.hrms_link import hrms_link, hrms_url
from components.employee import acc
from components.reservation import res
from components.menu import menu
from components.order import ord


# Create flask app and load components
app = Flask("HorizonBranch")
app.root_path = path.dirname(__file__) + "/web"

app.register_blueprint(hrms_link)  # id: link
app.register_blueprint(inv)                            # id: inventory
app.register_blueprint(acc)                            # id: account
app.register_blueprint(res)                            # id: reservation
app.register_blueprint(menu)                           # id: menu
app.register_blueprint(ord)                            # id: order


app.secret_key = b"ald"

@app.route("/info/")
def info():
    return jsonify({"name":branch_name, "address":branch_address})


@app.route('/index/')
def index():
    return render_template("index.html")


@app.route('/', methods=["GET"])
@role_required("S", "C", "M", "A")
def manage():
    return render_template("manage.html", branch_name=branch_name, msg=request.args.get("msg"))


@app.route('/logout/')
def logout():
    session.clear()
    return redirect('/index/')


@app.route('/m_kitchen/')
@role_required("S", "C", "M", "A")
def m_kitchen():
    return render_template('m_kitchen.html')


@app.route('/m_discount/')
@role_required("M", "A")
def m_discount():
    return render_template('m_discount.html')


@app.route('/m_payment/')
@role_required("M", "A")
def m_payment():
    return render_template('m_payment.html')


@app.route('/m_report/')
@role_required("M", "A")
def m_report():
    return render_template('m_report.html')


from datetime import date

@app.route('/report.html', methods=["GET","POST"])
@role_required("M", "A")
def create_report():

    datefrom = request.form.get("from")
    datefrom = datetime.strptime(datefrom, "%Y-%m-%d").date()
    dateto = request.form.get("to")
    dateto = datetime.strptime(dateto, "%Y-%m-%d").date()

    if datefrom > dateto:
        return redirect("/m_report/")

    items = request.form.get("items") is not None
    orders = request.form.get("orders") is not None
    reservations = request.form.get("reservations") is not None

    interval = request.form.get("interval","monthly")

    content = get_report_data(datefrom, dateto, interval, items=items, orders=orders, reservations=reservations)
    report = ""

    for _k,v in content.items():
        if _k == "created_at": continue
        report = report + f"""<h2>{v["label"]}</h2>"""
        for k,v in v.items():
            if k == "label": continue

            if type(v) != dict:
                report = report + f"<p>{k}: {v}</p>"

            else:
                labels = ""
                values = ""
                span = 0
                for label, value in v.items():
                    labels = labels + f"<th>{label}</th>"
                    values = values + f"<td>{value}</td>"
                    span = span + 1
                report = report + f"""<table><tr><th colspan="{span}">{k}</th></tr><tr>{labels}</tr><tr>{values}</tr></table>"""
        report = report + "<br><br>"

    return render_template("report.html", branch=branch_name, report=report)


try:
    r = requests.post(hrms_url + "/register_branch", json = {"port": branch_port, "magic_password": "SecretBranchRegistrationPassword"})
    print(r)
except:
    print("Couldn't register to HRMS")

try:
    app.run(debug = True, port = int(branch_port), host="0.0.0.0") # host 0.0.0.0 to allow network connection
except OSError as e:
    print("Port not available")