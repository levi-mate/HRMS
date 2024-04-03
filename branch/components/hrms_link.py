from flask import *
from .base import role_required, get_ip
import requests


hrms_ip = "127.0.0.1"
hrms_url = "http://" + hrms_ip + ":5069"
hrms_link = Blueprint('link', __name__)
hrms_key = "I'M TH3 R34L HRM$. Obey Me."

def is_hrms():
    print("[               [")
    print(get_ip() == hrms_ip)
    print(request.form.get("key") != hrms_key)
    print("]               ]")
    return ((request.form.get("key") != hrms_key)
        and (get_ip() == hrms_ip) )


# The first endpoint will display the form to select branch and input reservation info
@hrms_link.route("/reserve_at_branch/")
@role_required("M","A")
def view_reservation_station():
    branches = requests.get(hrms_url+"/branches/").json()
    return render_template("branch_reserve.html", branches=branches)


# The second endpoint will forward the form to HRMS and display what it gets back
@hrms_link.route("/reserve_at_branch2/", methods=["POST"])
@role_required("M","A")
def submit_reservation_station():
    r = requests.post(hrms_url+"/reserve1/", data=request.form)
    return r.text


# The third endpoint will send the full reservation form back to HRMS and completes the reservation
@hrms_link.route("/reserve_at_branch3/", methods=["POST"])
@role_required("M","A")
def create_reservation_station():
    r = requests.post(hrms_url+"/reserve2/", data=request.form)
    return redirect("/")


# request data for the report functions
@hrms_link.route("/report/", methods=["POST"])
def report_info():
    if request.form.get("key") != b_key:
        return abort(403)
