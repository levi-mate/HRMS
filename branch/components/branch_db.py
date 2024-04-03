import sqlite3
from datetime import date, timedelta
from os import path
import json


web_path = path.abspath(path.join(path.dirname(__file__), '..', 'web'))
db_path = path.join(web_path, 'horizon.db')

# Check if 'horizon.db' exists in the 'web' folder before starting up
existing = path.isfile(db_path)
db = sqlite3.connect(db_path, check_same_thread=False)
db.row_factory = sqlite3.Row

# If 'horizon.db' didn't exist, run the SQL in the db init file
if not existing:
    db_init_path = path.join(path.dirname(__file__), '..', 'db_init.sql')
    with open(db_init_path, "r") as f:
        c = db.cursor()
        s = f.read()
        c.executescript(s)
        db.commit()
        c.close()

# Convenience class to use inside a "with as" statement
class Cursor():

    def __enter__(self):
        self.c = db.cursor()
        return self.c

    def __exit__(self, *args):
        db.commit()
        self.c.close()


if not path.isfile("branch_info.json"):
    with open("branch_info.json","w") as f:
        f.write("""{"address":"Placeholder Street, BS69","name":"I literally dont know","port":5070}""")

with open("branch_info.json","r") as f:
    data = json.load(f)
    branch_name = data["name"]
    branch_address = data["address"]
    branch_port = data["port"]

# find the largest table
with Cursor() as c:
    c.execute("SELECT capacity FROM `table`")
    largest_table = 0
    for table in c.fetchall():
        largest_table = max(largest_table, table["capacity"])


"""
Branch report parameters:
Timeframe <2x date>
Contents <set>: orders, revenue, reservations
Interval: daily, weekly, monthly

Returns a big giant dictionary with what you asked for
"""
def get_report_data(_from, to, interval, items=False, orders=False, reservations=False):
    data = {} #{ "creation_date" : str(date.today()) }
    ranges = __iteratable(_from, to, interval)

    for rng in ranges:
        rs = rng["from"]
        re = rng["to"]
        sect = { "label": rng["label"]}

        if items:
            __items(sect, rs, re)
        if orders:
            __orders(sect, rs, re)
        if reservations:
            __reservations(sect, rs, re)

        data[rs] = (sect)

    return data


ONEDAY = timedelta(days=1)

# function that returns an dictionary with 2 dates for SQL and a humanised label
def __iteratable(c, to, interval):
    ranges = []

    if interval == "daily":
        delta = timedelta(days=1)
        while c < to:
            nxt = c+delta
            ranges.append({"from": str(c), "to": str(nxt),
                           "label": c.strftime("%d/%m/%Y") })
            c = nxt


    elif interval == "weekly":
        delta = timedelta(days=7)
        while c < to:
            nxt = c+delta
            ranges.append({"from": str(c), "to": str(nxt),
                           "label": f"{c.strftime('%d/%m/%Y')} to {(nxt-ONEDAY).strftime('%d/%m/%Y')}" })
            c = nxt


    elif interval == "monthly":
        while c < to:
            # use replace to keep the day the same for each month
            nxt = c.replace(month=c.month+1)
            ranges.append({"from": str(c), "to": str(nxt),
                           "label": f"{c.strftime('%d/%m/%Y')} to {(nxt-ONEDAY).strftime('%d/%m/%Y')}" })
            c = nxt

    return ranges


## Helper functions that insert data directly into dictionary
# function that sums how much each menu item was ordered
def __items(o, _from, to):
    tally = {}

    with Cursor() as c:
        pass


# function that sums order payments in a range and gets an average
def __orders(o, _from, to):
    _sum = 0
    n = 0
    with Cursor() as c:
        c.execute("SELECT amount_paid FROM `order` WHERE placed_at > ? AND placed_at < ?", (_from, to,))
        r = c.fetchall()
    for order in r:
        _sum = _sum + order["amount_paid"]
        n = n + 1
    o["Total orders"] = n
    o["Average order price"] = _sum/(n==0 and 1 or n)
    o["Revenue"] = _sum


# function that sums the amounts of reservations and tallies them based on how many people were reserved for
def __reservations(o, _from, to):
    # tally will show group sizes between 1 and the largest reservable size in the branch
    # remember that the index = groupsize-1
    tally = {i:0 for i in range(1, largest_table+1)}
    _sum = 0
    with Cursor() as c:
        c.execute("SELECT amount FROM reservation WHERE datetime > ? AND datetime < ?", (_from, to,))
        for rsv in c.fetchall():
            _sum = _sum + 1
            amt = rsv["amount"]
            tally[amt-1] = tally[amt] + 1

    o["Total reservations"] = _sum
    o["Reservation size frequencies"] = tally
