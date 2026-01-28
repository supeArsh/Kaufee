from datetime import datetime, timedelta
import random

# In-memory data storage
menu_items = []
inventory_items = []
staff = []
orders = []

def initialize_data():
    """Initialize sample data for the application"""
    # Clear existing data
    menu_items.clear()
    inventory_items.clear()
    staff.clear()
    orders.clear()

def get_menu_items():
    return menu_items

def add_menu_item(item):
    menu_items.append(item)

def update_menu_item(updated_item):
    for i, item in enumerate(menu_items):
        if item['id'] == updated_item['id']:
            menu_items[i] = updated_item
            break

def delete_menu_item(item_id):
    global menu_items
    menu_items = [item for item in menu_items if item['id'] != item_id]

def get_inventory_items():
    return inventory_items

def add_inventory_item(item):
    inventory_items.append(item)

def update_inventory_item(updated_item):
    for i, item in enumerate(inventory_items):
        if item['id'] == updated_item['id']:
            inventory_items[i] = updated_item
            break

def delete_inventory_item(item_id):
    global inventory_items
    inventory_items = [item for item in inventory_items if item['id'] != item_id]

def get_staff():
    return staff

def add_staff(employee):
    staff.append(employee)

def update_staff(updated_employee):
    for i, employee in enumerate(staff):
        if employee['id'] == updated_employee['id']:
            staff[i] = updated_employee
            break

def delete_staff(employee_id):
    global staff
    staff = [employee for employee in staff if employee['id'] != employee_id]

def get_orders():
    return orders

def add_order(order):
    orders.append(order)

    # Update inventory based on ordered items
    for item_id in order['menu_items']:
        # In a real system, this would decrease inventory levels
        # based on ingredient requirements for each menu item
        pass

def update_order(updated_order):
    for i, order in enumerate(orders):
        if order['id'] == updated_order['id']:
            orders[i] = updated_order
            break

def delete_order(order_id):
    global orders
    orders = [order for order in orders if order['id'] != order_id]