from flask import *
import requests
from os import path
import sqlite3


# Check if ms.db exists before starting up
existing = path.isfile("ms.db")
db = sqlite3.connect("ms.db", check_same_thread=False)

# If ms.db didn't exist, run the SQL in the db init file
if not existing:
    with open("hrms_init.sql", "r") as f:
        c = db.cursor()
        s = f.read()
        c.executescript(s)
        db.commit()
        c.close()


# actual HRMS flask app below
app = Flask(__name__)
app.secret_key = b"ulldozah"

# secret password. keep it secret.
hrms_key = "I'M TH3 R34L HRM$. Obey Me."

def deregister_branch(url):
    c = db.cursor()


def verify():
    ip = request.remote_addr
    if ip == False: ip = "127.0.0.1"
    c = db.cursor()
    c.execute("SELECT ip FROM branch WHERE ip=?",(ip,))
    b = c.fetchone()
    c.close()
    return b[0] == ip


@app.route("/reserve1/", methods=["POST"])
def reserve():
    if not verify():
        return abort(401)

    if (url := request.form.get("url")) is None:
        return abort(406)

    ## REQUEST TO THE BRANCH
    ## RETURN WHAT THE BRANCH RETURNSSSS
    amount = request.form.get('amount')
    name = request.form.get('name')
    datetime = request.form.get('datetime')

    r = requests.post(url+"/create_reservation/", data={"amount": amount, "name": name, "datetime": datetime, "url": url, "key": hrms_key})
    return r.text


@app.route("/reserve2/", methods=["POST"])
def confirm_reserve():
    if not verify():
        return abort(401)

    if (url := request.form.get("url")) is None:
        return abort(406)

    table_id = request.form.get('table_id')
    amount = request.form.get('amount')
    name = request.form.get('name')
    datetime = request.form.get('datetime')
    r = requests.post(url+"/confirm_reservation/", data={"table_id": table_id, "amount": amount, "name": name, "datetime": datetime, "key": hrms_key})
    return r.text


@app.route("/branches/")
def branches():
    data = []
    c = db.cursor()
    c.execute("SELECT url FROM branch")
    bs = c.fetchall()
    c.close()
    for b in bs:
        url = b[0]
        try:
            r = requests.get(url + "/info/").json()
            data.append({ "name": r["name"], "address": r["address"], "url": url })
        except Exception as e:
            print("Branch at",url,"is unreachable")
            deregister_branch(url)

    return jsonify(data)


# use this to register a branch's ip+port to the hrms backend database
# branches should try to register as soon as they are ran
@app.route("/register_branch/", methods=["POST"])
def register_branch():
    if request.json.get("magic_password") != "SecretBranchRegistrationPassword":
        return abort(403)
    if (port := request.json.get("port")) is None:
        return abort(406)

    ip = request.remote_addr
    if ip == False: ip = "127.0.0.1"
    ap = "http://" + ip + ":" + str(port)

    c = db.cursor()
    try:
        c.execute("INSERT INTO branch(url, ip) VALUES (?,?)", (ap,ip,))
        db.commit()
        print("NEW BRANCH REGISTERED AT", ap)
    except sqlite3.IntegrityError:
        print("Branch at", ap, "just initialised")
    c.close()

    return "Hi", 200


try:
    app.run(debug = True, port = 5069, host="0.0.0.0") # host 0.0.0.0 to allow network connection
except OSError as e:
    print("Port not available")