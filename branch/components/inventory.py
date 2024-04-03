from flask import *
from .base import *
from .branch_db import Cursor

inv = Blueprint('inventory', __name__)


class InventoryItem:
    def __init__(self, name, amount, restock_at):
        self.name = name
        self.amount = amount
        self.restock_at = restock_at

    def inventory_update(self):
        return {
            "name" : self.name,
            "amount" : self.amount,
            "restock_at" : self.restock_at
        }

    # Shows entire inventory
    def view_stock():
        with Cursor() as c:
            c.execute("SELECT * FROM inventory_item")
            items = c.fetchall()
            return [InventoryItem(name = row["name"], amount = row["amount"], restock_at = row["restock_at"]) for row in items]

    # Shows details of specific item (identified by name)
    def view_stock_item(name):
        with Cursor() as c:
            c.execute("SELECT * FROM inventory_item WHERE name = ?", (name,))
            item = c.fetchone()
            return item

    # Creates inventory item with specified name, amount and restock level
    def create_stock_item(item):
        with Cursor() as c:
            c.execute("INSERT INTO inventory_item (name, amount, restock_at) VALUES (?, ?, ?)", (item.name, item.amount, item.restock_at))

    # Updates inventory item of specific name with new name, amount and restock level
    def update_stock(name, new_name, amount, restock_at):
        with Cursor() as c:
            c.execute("UPDATE inventory_item SET name = ?, amount = ?, restock_at = ? WHERE name = ?", (new_name, amount, restock_at, name))

    # Deletes inventory item of specific name
    def delete_stock_item(name):
        with Cursor() as c:
            c.execute("DELETE FROM inventory_item WHERE name = ?", (name,))


@inv.route('/m_inventory/', methods = ["POST","GET"])
@role_required("S", "M", "A")
def m_inventory():
    # Shows entire stock
    inventory = InventoryItem.view_stock()
    return render_template('m_inventory.html', inventory = inventory)


@inv.route('/create_inventory/', methods = ["POST","GET"])
@role_required("S", "M", "A")
def create_inventory():
    # If details are provided for new inventory item, creates object from InventoryItem class and stores it in database
    if request.method == 'POST':
        name = request.form.get('name')
        amount = max(0, min(100, int(request.form.get('amount'))))
        restock_at = max(0, min(amount, int(request.form.get('restock_at'))))

        item = InventoryItem(name, amount, restock_at)

        InventoryItem.create_stock_item(item)

        flash(f"Inventory item with name: {name}, amount: {amount}, restock at: {restock_at} successfully created.")
        return redirect("/m_inventory/")


@inv.route('/update_inventory/<string:item_name>/', methods = ["POST","GET"])
@role_required("S", "M", "A")
def update_inventory(item_name):
    # If details are provided for updated inventory item, uses update_stock to update them in database
    if request.method == 'POST':
        new_name = request.form.get('name')
        amount = max(0, min(100, int(request.form.get('amount'))))
        restock_at = max(0, min(amount, int(request.form.get('restock_at'))))

        InventoryItem.update_stock(item_name, new_name, amount, restock_at)
        return redirect('/m_inventory/')

    # By default, fetches details of an item with specific name to populate update fields with
    item = InventoryItem.view_stock_item(item_name)
    return render_template('update_inventory.html', item = item)


@inv.route('/delete_inventory/<string:item_name>/', methods = ["POST","GET"])
@role_required("S", "M", "A")
def delete_inventory(item_name):
    if request.method == 'POST':
        InventoryItem.delete_stock_item(item_name)

        flash(f"Inventory item '{item_name}' has been successfully deleted.")
        return redirect('/m_inventory/')