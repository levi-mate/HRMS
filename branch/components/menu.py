from flask import *
from .base import *
from .branch_db import Cursor

menu = Blueprint('menu', __name__)


class MenuCategory:
    def __init__(self, cat_name, cat_id = None):
        self.cat_name = cat_name
        self.cat_id = cat_id

    def to_dict(self):
        return {
            'cat_id': self.cat_id,
            'cat_name': self.cat_name
        }

    def view_menu_category(cat_id):
        with Cursor() as c:
            c.execute("SELECT * FROM menu_category WHERE id = ?", (cat_id,))
            category = c.fetchone()
            return category

    def view_categories():
        with Cursor() as c:
            c.execute("SELECT id, name FROM menu_category")
            category_list = c.fetchall()
            return [MenuCategory(cat_name = row['name'], cat_id = row['id']) for row in category_list]
        
    def create_category(category):
        with Cursor() as c:
            c.execute("INSERT INTO menu_category (name) VALUES (?)", (category.cat_name,))

    def update_category(name, cat_id):
        with Cursor() as c:
            c.execute("UPDATE menu_category SET name = ? WHERE id = ?", (name, cat_id,))

    def delete_category(cat_id):
        with Cursor() as c:
            c.execute("DELETE FROM menu_item WHERE category_id = ?", (cat_id,))

            c.execute("DELETE FROM menu_category WHERE id = ?", (cat_id,))


class MenuItem:
    def __init__(self, price, item_name, desc, all_gens, category = None, item_id = None):
        self.price = price
        self.item_name = item_name
        self.desc = desc
        self.all_gens = all_gens
        self.category = category
        self.item_id = item_id

    def to_dict(self):
        return {
            'item_id': self.item_id,
            'price': self.price,
            'item_name': self.item_name,
            'desc': self.desc,
            'all_gens': self.all_gens
        }

    def view_menu_item(item_id):
        with Cursor() as c:
            c.execute("SELECT * FROM menu_item WHERE id = ?", (item_id,))
            item = c.fetchone()
            return item

    def view_items_by_category(cat_id):
        with Cursor() as c:
            c.execute("SELECT id, price, name, description, allergens FROM menu_item WHERE category_id = ?", (cat_id,))
            item_list = c.fetchall()
            return [MenuItem(price = row['price'], item_name = row['name'], desc = row['description'], all_gens = row['allergens'], item_id = row['id']) for row in item_list]

    def create_item(item):
        with Cursor() as c:
            c.execute("INSERT INTO menu_item (category_id, price, name, description, allergens) VALUES (?, ?, ?, ?, ?)", (item.category, item.price, item.item_name, item.desc, item.all_gens,))

    def update_item(price, name, desc, all_gens, item_id):
        with Cursor() as c:
            c.execute("UPDATE menu_item SET price = ?, name = ?, description = ?, allergens = ? WHERE id = ?", (price, name, desc, all_gens, item_id,))

    def delete_item(item_id):
        with Cursor() as c:
            c.execute("DELETE FROM menu_item WHERE id = ?", (item_id,))


@menu.route('/m_menu/', methods = ["POST","GET"])
@role_required("C", "M", "A")
def m_menu():
    categories = [category.to_dict() for category in MenuCategory.view_categories()]
    items_by_category = {
        cat['cat_id']: [item.to_dict() for item in MenuItem.view_items_by_category(cat['cat_id'])]
        for cat in categories
    }
    return render_template('m_menu.html', categories = categories, items_by_category = items_by_category)


@menu.route('/create_menu_category/', methods = ["POST","GET"])
@role_required("C", "M", "A")
def create_menu_category():
    if request.method == 'POST':
        name = request.form.get('name')

        category = MenuCategory(name)
        MenuCategory.create_category(category)

        return redirect('/m_menu/')
    

@menu.route('/create_menu_item/', methods = ["POST","GET"])
@role_required("C", "M", "A")
def create_menu_item():
    if request.method == 'POST':
        category = request.form.get('category')
        price = request.form.get('price')
        name = request.form.get('name')
        desc = request.form.get('desc')
        all_gens = request.form.get('all_gens')

        item = MenuItem(price, name, desc, all_gens, category)
        MenuItem.create_item(item)

        return redirect('/m_menu/')
    

@menu.route('/update_menu_category/<string:cat_id>/', methods = ["POST","GET"])
@role_required("C", "M", "A")
def update_menu_category(cat_id):
    if request.method == 'POST':
        name = request.form.get('name')

        MenuCategory.update_category(name, cat_id)
        return redirect('/m_menu/')
    
    category = MenuCategory.view_menu_category(cat_id)
    return render_template('update_menu_category.html', category = category)


@menu.route('/update_menu_item/<string:item_id>/', methods = ["POST","GET"])
@role_required("C", "M", "A")
def update_menu_item(item_id):
    if request.method == 'POST':
        price = request.form.get('price')
        name = request.form.get('name')
        desc = request.form.get('desc')
        all_gens = request.form.get('all_gens')

        MenuItem.update_item(price, name, desc, all_gens, item_id)
        return redirect('/m_menu/')
    
    item = MenuItem.view_menu_item(item_id)
    return render_template('update_menu_item.html', item = item)


@menu.route('/delete_menu_category/<string:cat_id>/', methods = ["POST","GET"])
@role_required("C", "M", "A")
def delete_menu_category(cat_id):
    if request.method == 'POST':
        MenuCategory.delete_category(cat_id)

        return redirect('/m_menu/')
    

@menu.route('/delete_menu_item/<string:item_id>/', methods = ["POST","GET"])
@role_required("C", "M", "A")
def delete_menu_item(item_id):
    if request.method == 'POST':
        MenuItem.delete_item(item_id)

        return redirect('/m_menu/')