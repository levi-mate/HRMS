from flask import *
from .base import *
from .branch_db import Cursor
from .menu import *
from .inventory import *
from datetime import datetime

ord = Blueprint('order', __name__)


class Order:
    def __init__(self, name, placed_at, amount_paid, status, id = None, items = None):
        self.name = name
        self.placed_at = placed_at
        self.amount_paid = amount_paid
        self.status = status
        self.id = id
        self.items = items or []

    def view_orders():
        with Cursor() as c:
            c.execute("SELECT * FROM `order` ORDER BY placed_at ASC")
            orders = c.fetchall()

            order_objects = {row['id']: Order(id = row['id'], name = row['name'], placed_at = row['placed_at'], amount_paid = row['amount_paid'], status = row['status'], items = []) for row in orders}

            query = "SELECT oi.order_id, oi.quantity, mi.name as item_name FROM order_item oi JOIN menu_item mi ON oi.item_id = mi.id"
            c.execute(query)
            order_items = c.fetchall()

            for item in order_items:
                if item['order_id'] in order_objects:
                    order_objects[item['order_id']].items.append({'item_name': item['item_name'], 'quantity': item['quantity']})

            return list(order_objects.values())
        
    def delete_order(order_id):
        with Cursor() as c:
            c.execute("DELETE FROM `order` WHERE id = ?", (order_id,))


class OrderItem:
    def __init__(self, quantity, order_id = None, item_id = None):
        self.quantity = quantity
        self.order_id = order_id
        self.item_id = item_id


@ord.route('/m_order/', methods = ["POST","GET"])
@role_required("S", "M", "A")
def m_order():
    categories = [category.to_dict() for category in MenuCategory.view_categories()]

    inventory_stock = {item.name: item.amount for item in InventoryItem.view_stock()}

    items_by_category = {}
    for cat in categories:
        items = [item.to_dict() for item in MenuItem.view_items_by_category(cat['cat_id'])]

        for item in items:
            item['stock'] = inventory_stock.get(item['item_name'], 0)

        available_menu_items = []
        for item in items:
            if item['item_name'] in inventory_stock and inventory_stock[item['item_name']] > 0:
                available_menu_items.append(item)

        items_by_category[cat['cat_id']] = available_menu_items

    orders = Order.view_orders()
    return render_template('m_order.html', categories = categories, items_by_category = items_by_category, orders = orders)


@ord.route('/create_order/', methods = ["POST","GET"])
@role_required("S", "M", "A")
def create_order():
    if request.method == 'POST':
        item_ids = request.form.getlist('itemIds[]')
        quantities = request.form.getlist('quantities[]')

        with Cursor() as c:
            ids_list = ','.join('?' for _ in item_ids)
            query = f"SELECT id, name, price FROM menu_item WHERE id IN ({ids_list})"
            c.execute(query, item_ids)
            items = c.fetchall()

            item_prices = {str(item['id']): item['price'] for item in items}
            amount_paid = sum(float(item_prices[id]) * int(qty) for id, qty in zip(item_ids, quantities))

            order_name = "New Order"
            placed_at = datetime.now().strftime("%Y-%m-%d %H:%M")
            status = "Pending"

            c.execute("INSERT INTO `order` (name, placed_at, amount_paid, status) VALUES (?, ?, ?, ?)", (order_name, placed_at, amount_paid, status))
            order_id = c.lastrowid

            for item_id, quantity in zip(item_ids, quantities):
                c.execute("INSERT INTO order_item (item_id, order_id, quantity) VALUES (?, ?, ?)", (item_id, order_id, quantity))

                c.execute("UPDATE inventory_item SET amount = amount - ? WHERE name = (SELECT name FROM menu_item WHERE id = ?)", (int(quantity), item_id))

        return render_template('finalise_order.html', order_id = order_id, items = items, quantities = quantities)
    

@ord.route('/finalise_order/', methods = ["POST","GET"])
@role_required("S", "M", "A")
def finalise_order():
    if request.method == 'POST':
        name = request.form.get('name')
        order_id = request.form.get('order_id')
        status = "Placed"

        with Cursor() as c:
            c.execute("UPDATE `order` SET name = ?, status = ? WHERE id = ?", (name, status, order_id,))

        return redirect('/m_order/')
    

@ord.route('/order_ready/<string:order_id>/', methods = ["POST","GET"])
@role_required("S", "M", "A")
def order_ready(order_id):
    if request.method == 'POST':
        status = "Ready"

        with Cursor() as c:
            c.execute("UPDATE `order` SET status = ? WHERE id = ?", (status, order_id,))

        return redirect('/m_order/')
    

@ord.route('/order_served/<string:order_id>/', methods = ["POST","GET"])
@role_required("S", "M", "A")
def order_served(order_id):
    if request.method == 'POST':
        status = "Served"

        with Cursor() as c:
            c.execute("UPDATE `order` SET status = ? WHERE id = ?", (status, order_id,))

        return redirect('/m_order/')
    

@ord.route('/cancel_order/<string:order_id>/', methods = ["POST","GET"])
@role_required("S", "M", "A")
def cancel_order(order_id):
    if request.method == 'POST':
        Order.delete_order(order_id)

        return redirect('/m_order/')