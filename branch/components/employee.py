from .branch_db import Cursor
from passlib.hash import sha256_crypt as sha256
from flask import *
from .base import *

acc = Blueprint('account', __name__)


class Employee:
    def __init__(self, id, forename, surname, password, role):
        self.id = id
        self.forename = forename
        self.surname = surname
        self.password = password
        self.role = role

    def view_employees():
        with Cursor() as c:
            c.execute("SELECT * FROM employee")
            employees = c.fetchall()
            return [Employee(id = row["id"], forename = row["forename"], surname = row["surname"], password = row["security_hash"], role = row["role"]) for row in employees]
        
    def view_employee(employee_id):
        with Cursor() as c:
            c.execute("SELECT * FROM employee WHERE id = ?", (employee_id,))
            employees = c.fetchall()
            return [Employee(id = row["id"], forename = row["forename"], surname = row["surname"], password = row["security_hash"], role = row["role"]) for row in employees]


@acc.route('/login/', methods=["POST","GET"])
def login():
    if request.method == "GET":
        return render_template("index.html")

    elif request.method == "POST":
        print(*request.form)
        forename = request.form.get("forename","").lower()
        surname = request.form.get("surname","").lower()
        password = request.form.get("password")

        with Cursor() as c:
            c.execute("SELECT * FROM employee WHERE forename = ? AND surname = ?", (forename, surname,))
            r = c.fetchone()
            if r is None or not sha256.verify(password, r["security_hash"]):
                flash("Invalid credentials. Please try again.")
                return render_template("index.html") # login failed

            session["id"] = r["id"]
            session["role"] = r["role"]
            session["name"] = forename
            return redirect("/")


@acc.route('/m_account/')
@role_required("A")
def m_account():
    employees = Employee.view_employees()
    return render_template("m_account.html", employees = employees)


@acc.route('/admin/update_role/<string:employee_id>/', methods = ["POST","GET"])
@role_required("A")
def change_employee_role(employee_id):
    #user_role = session.get("role")
    #fn = request.form.get("forename")
    #sn = request.form.get("surname")
    #new_role = request.form.get("role")

    # The user has to be an admin, they can't set another employee to be an admin, and they can't "demote" other admins
    # (this should be done by the sysadmins who have access to the database)
    #if user_role != "A" or new_role not in ["A","C","S","M"]:
        #return abort(403)

    # Get role of wanted employee
    #with Cursor() as c:
        #c.execute("SELECT role FROM employee WHERE forename = ? AND surname = ?", (fn, sn,) )
        #target_role = c.fetchone().get("role")

    #if target_role is None:
        #return abort(404)
    #elif target_role == "A":
        #return abort(403)

    # Finally set the employee's new role
    #with Cursor() as c:
        #c.execute("UPDATE employee SET role = ? WHERE forename = ? AND surname = ?", (new_role, fn, sn,) )
    #return True, 200

    if request.method == 'POST':
        new_role = request.form.get("role")

        with Cursor() as c:
            c.execute("SELECT role FROM employee WHERE id = ?", (employee_id,))
            target_role = c.fetchone()["role"]

            if target_role is None:
                return redirect("/m_account/")
            elif target_role == "A":
                return redirect("/m_account/")
            
            with Cursor() as c:
                c.execute("UPDATE employee SET role = ? WHERE id = ?", (new_role, employee_id,))

            return redirect("/m_account/")
        
    employee = Employee.view_employee(employee_id)
    return render_template('update_role.html', employees = employee)


@acc.route('/admin/update_password/<string:employee_id>/', methods = ["POST","GET"])
@role_required("A")
def change_employee_password(employee_id):
    #user_role = session.get("role")
    #fn = request.form.get("forename")
    #sn = request.form.get("surname")
    #new_password = request.form.get("password")
    #hashed = sha256.hash(new_password)

    # The user has to be an admin, and they can't change other admins' passwords
    # (this should be done by the sysadmins who have access to the database)
    #if user_role != "A":
        #return abort(403)

    # Get role of wanted employee
    #with Cursor() as c:
        #c.execute("SELECT role FROM employee WHERE forename = ? AND surname = ?", (fn, sn,) )
        #target_role = c.fetchone().get("role")

    #if target_role is None:
        #return abort(404)
    #elif target_role == "A":
        #return abort(403)

    # Finally set the employee's new password
    #with Cursor() as c:
        #c.execute("UPDATE employee SET security_hash = ? WHERE forename = ? AND surname = ?", (hashed, fn, sn,) )
    #return redirect("/m_account/")

    if request.method == 'POST':
        new_password = request.form.get("password")
        hashed = sha256.hash(new_password)

        with Cursor() as c:
            c.execute("SELECT role FROM employee WHERE id = ?", (employee_id,))
            target_role = c.fetchone()["role"]

            if target_role is None:
                return redirect("/m_account/")
            elif target_role == "A":
                return redirect("/m_account/")
            
            with Cursor() as c:
                c.execute("UPDATE employee SET security_hash = ? WHERE id = ?", (hashed, employee_id,))

            return redirect("/m_account/")
        
    employee = Employee.view_employee(employee_id)
    return render_template('update_password.html', employees = employee)


@acc.route('/admin/create_employee/', methods = ["POST"])
@role_required("A")
def create_employee():
    user_role = session.get("role")
    fn = request.form.get("forename","").lower()
    sn = request.form.get("surname","").lower()
    role = request.form.get("role")
    password = request.form.get("password")
    hashed = sha256.hash(password)

    # The user has to be an admin, and they can't create new admins
    # (this should be done by the sysadmins who have access to the database)
    if user_role != "A" or role not in ["A","C","S","M"]:
        return abort(403)

    # Create new employee
    with Cursor() as c:
        c.execute("INSERT INTO employee(forename, surname, role, security_hash) values(?, ?, ?, ?)", (fn, sn, role, hashed,) )
    return redirect("/m_account/")


@acc.route('/admin/delete_employee/<string:employee_id>/', methods = ["POST"])
@role_required("A")
def delete_employee(employee_id):
    #user_role = session.get("role")
    #fn = request.form.get("forename")
    #sn = request.form.get("surname")

    # The user has to be an admin, and they can't delete other admins
    # (this should be done by the sysadmins who have access to the database)
    #if user_role != "A":
        #return abort(403)

    #with Cursor() as c:
        #c.execute("SELECT role FROM employee WHERE forename = ? AND surname = ?", (fn, sn,) )
        #target_role = c.fetchone().get("role")

    #if target_role is None:
        #return abort(404)
    #elif target_role == "A":
        #return abort(403)

    # Delete the employee
    #with Cursor() as c:
        #c.execute("DELETE FROM employee WHERE forename = ? AND surname = ?", (fn, sn,) )
    #return redirect("/m_account/")

    if request.method == 'POST':
        with Cursor() as c:
            c.execute("SELECT role FROM employee WHERE id = ?", (employee_id,))
            target_role = c.fetchone()["role"]

            if target_role is None:
                return redirect("/m_account/")
            elif target_role == "A":
                return redirect("/m_account/")
        
        with Cursor() as c:
            c.execute("DELETE FROM employee WHERE id = ?", (employee_id,))

        return redirect("/m_account/")
