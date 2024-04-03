from flask import *
from .base import *
from .branch_db import Cursor, largest_table
from .hrms_link import is_hrms, hrms_url
from datetime import datetime

res = Blueprint('reservation', __name__)


class Reservation:
    def __init__(self, table_id, amount, name, datetime, id = None):
        self.id = id
        self.table_id = table_id
        self.amount = amount
        self.name = name
        self.datetime = datetime

    def view_all_reservations():
        with Cursor() as c:
            c.execute("SELECT * FROM reservation ORDER BY datetime ASC")
            reservations = c.fetchall()
            return [Reservation(id = row["id"], table_id = row["table"], amount = row["amount"], name = row["name"], datetime = str(row["datetime"])) for row in reservations]
        
    def view_reservation(id):
        with Cursor() as c:
            c.execute("Select * FROM reservation WHERE id = ?", (id,))
            reservation = c.fetchall()
            return [Reservation(id = row["id"], table_id = row["table"], amount = row["amount"], name = row["name"], datetime = str(row["datetime"])) for row in reservation]

    def create_reservation(reservation):
        with Cursor() as c:
            c.execute("INSERT INTO reservation (`table`, amount, name, datetime) VALUES (?, ?, ?, ?)", (reservation.table_id, reservation.amount, reservation.name, reservation.datetime))

    def update_reservation(id, table_id, amount, name, datetime):
        with Cursor() as c:
            c.execute("UPDATE reservation SET 'table' = ?, amount = ?, name = ?, datetime = ? WHERE id = ?", (table_id, amount, name, datetime, id,))

    def cancel_reservation(id):
        with Cursor() as c:
            c.execute("DELETE FROM reservation WHERE id = ?", (id,))


class Table:
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity

    def check_capacity(amount):
        with Cursor() as c:
            c.execute("SELECT * FROM `table` WHERE capacity >= ?", (int(amount),))
            tables = c.fetchall()

            if tables is None:
                error = "No available tables for that date"
            else:
                available_tables = []
                for table_id, table_capacity in tables:
                    available_tables.append((table_id, table_capacity))
                return available_tables
            
    def add_duration(original_datetime, hours):
        return datetime(original_datetime.year, original_datetime.month, original_datetime.day, original_datetime.hour + hours, original_datetime.minute)

    def check_availability(amount, reservation_datetime):
        reserve_start = datetime.strptime(reservation_datetime, "%Y-%m-%dT%H:%M")
        reserve_end = Table.add_duration(reserve_start, 2)

        suitable_tables = Table.check_capacity(amount)
        available_tables = []

        with Cursor() as c:
            for table_id, table_capacity in suitable_tables:
                c.execute("SELECT * FROM reservation WHERE `table` = ? AND ((datetime BETWEEN ? AND ?) OR (datetime(reservation.datetime, '+2 hours') BETWEEN ? AND ?))", (table_id, reserve_start, reserve_end, reserve_start, reserve_end))
                if not c.fetchone():
                    available_tables.append((table_id, table_capacity))

        if not available_tables:
            not_available = "No available tables for the selected date and time"
            return not_available
        else:
            return available_tables
        

@res.route('/m_reserve/', methods = ["POST","GET"])
@role_required("S", "M", "A")
def m_reserve():
    reservations = Reservation.view_all_reservations()
    return render_template("m_reserve.html", reservations = reservations)


@res.route('/create_reservation/', methods = ["POST","GET"])
def create_reservation():

    hrms = is_hrms()
    if (role := session.get("role")) not in ["S","M","A"] and not hrms:
        return redirect(url_for("manage", msg=f"Access to {request.path} denied"))

    if request.method == 'POST':
        amount = request.form.get('amount')
        name = request.form.get('name')
        datetime = request.form.get('datetime')

        available_tables = Table.check_availability(amount, datetime)

        if hrms and False:
            callback = "/reserve_at_branch3/"
        else:
            callback = url_for('reservation.confirm_reservation')

        if isinstance(available_tables, str):
            flash(available_tables, 'error')
            return redirect("/m_reserve/")
        else:
            return render_template("create_reserve.html", tables = available_tables, amount = amount, name = name, datetime = datetime, callback = callback, branch = request.form.get("url"))


@res.route('/confirm_reservation/', methods = ["POST","GET"])
def confirm_reservation():

    hrms = is_hrms()
    if (role := session.get("role")) not in ["S","M","A"] and not hrms:
        return redirect(url_for("manage", msg=f"Access to {request.path} denied"))

    if request.method == 'POST':
        table_id = request.form.get('table_id')
        amount = request.form.get('amount')
        name = request.form.get('name')
        datetime = request.form.get('datetime')

        reservation = Reservation(table_id, amount, name, datetime)

        Reservation.create_reservation(reservation)

        return redirect("/m_reserve/")


@res.route('/update_reservation/<string:res_id>/', methods = ["POST","GET"])
@role_required("S", "M", "A")
def update_reservation(res_id):
    if request.method == 'POST':
        id = res_id
        table_id = request.form.get('table_id')
        amount = request.form.get('amount')
        name = request.form.get('name')
        datetime = request.form.get('datetime')

        Reservation.update_reservation(id, table_id, amount, name, datetime)
        return redirect('/m_reserve/')
    
    reservation = Reservation.view_reservation(res_id)
    return render_template('update_reserve.html', reservation = reservation)


@res.route('/cancel_reservation/<string:res_id>/', methods = ["POST","GET"])
@role_required("S", "M", "A")
def cancel_reservation(res_id):
    if request.method == 'POST':
        Reservation.cancel_reservation(res_id)

        return redirect('/m_reserve/')