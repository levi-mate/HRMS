from flask import *
from functools import wraps


# Role checking, (S)taff, (C)hef, (M)anager, (A)dmin
def role_required(*roles):
    def role_checker(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get("role") in roles:
                return f(*args, **kwargs)
            elif session.get("role") is not None:
                return redirect(url_for("manage", msg=f"Access to {request.path} denied"))
            else:
                return redirect("/index/")
        return wrapper
    return role_checker

def get_ip():
    ip = request.remote_addr
    if ip == False: ip = "127.0.0.1"
    return ip
