from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
import pandas as pd
import random

from main import app, db, login_manager
from models import User, MenuItem, Staff, Order, OrderItem
from forms import LoginForm, OrderForm, MenuItemForm, StaffForm

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get summary data for dashboard
    orders = Order.query.all()
    menu_items = MenuItem.query.all()
    staff = Staff.query.all()

    # Calculate metrics
    total_orders = len(orders)
    total_sales = sum(order.total for order in orders)
    active_staff = Staff.query.filter_by(active=True).count()

    # Get sales data for chart
    daily_sales = get_daily_sales()
    popular_items = get_popular_items()

    return render_template('dashboard.html', 
                          total_orders=total_orders,
                          total_sales=total_sales,
                          active_staff=active_staff,
                          daily_sales=daily_sales,
                          popular_items=popular_items)

@app.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    form = OrderForm()
    menu_items = MenuItem.query.filter_by(available=True).all()
    staff_members = Staff.query.filter_by(active=True).all()

    form.menu_items.choices = [(item.id, f"{item.name} - ${item.price:.2f}") for item in menu_items]
    form.staff_id.choices = [(employee.id, employee.name) for employee in staff_members]

    if form.validate_on_submit():
        # Calculate order total
        selected_items = MenuItem.query.filter(MenuItem.id.in_(form.menu_items.data)).all()
        total = sum(item.price for item in selected_items)

        # Create new order
        new_order = Order(
            customer_name=form.customer_name.data,
            staff_id=form.staff_id.data,
            timestamp=datetime.now(),
            status='Pending',
            total=total
        )

        db.session.add(new_order)
        db.session.flush()  # Get the order ID

        # Add order items
        for item_id in form.menu_items.data:
            order_item = OrderItem(
                order_id=new_order.id,
                menu_item_id=item_id,
                quantity=1  # Default quantity, can be enhanced later
            )
            db.session.add(order_item)

        db.session.commit()
        flash('Order added successfully!', 'success')
        return redirect(url_for('orders'))

    orders_list = Order.query.order_by(Order.timestamp.desc()).all()

    return render_template('orders.html', 
                           orders=orders_list, 
                           menu_items=menu_items, 
                           staff=staff_members, 
                           form=form)

@app.route('/orders/update/<int:id>', methods=['POST'])
@login_required
def update_order_status(id):
    new_status = request.form.get('status')
    if new_status:
        order = Order.query.get_or_404(id)
        order.status = new_status
        db.session.commit()
        flash('Order status updated', 'success')

    return redirect(url_for('orders'))

@app.route('/orders/delete/<int:id>', methods=['POST'])
@login_required
def remove_order(id):
    if current_user.role != 'admin':
        flash('You do not have permission to delete orders', 'danger')
        return redirect(url_for('orders'))

    order = Order.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    flash('Order deleted', 'success')
    return redirect(url_for('orders'))

@app.route('/menu', methods=['GET', 'POST'])
@login_required
def menu():
    form = MenuItemForm()

    if form.validate_on_submit():
        if current_user.role != 'manager':
            flash('You do not have permission to add menu items', 'danger')
            return redirect(url_for('menu'))
        new_item = MenuItem(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data,
            available=form.available.data
        )

        db.session.add(new_item)
        db.session.commit()
        flash('Menu item added successfully!', 'success')
        return redirect(url_for('menu'))

    menu_items = MenuItem.query.all()
    return render_template('menu.html', menu_items=menu_items, form=form)

@app.route('/menu/update/<int:id>', methods=['POST'])
@login_required
def update_menu_item_route(id):
    if current_user.role not in ['admin', 'manager']:
        flash('You do not have permission to update menu items', 'danger')
        return redirect(url_for('menu'))

    try:
        item = MenuItem.query.get_or_404(id)
        item.name = request.form['name']
        item.description = request.form['description']
        item.price = float(request.form['price'])
        item.category = request.form['category']
        item.available = 'available' in request.form
        
        db.session.commit()
        flash('Menu item updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating menu item', 'danger')
        print(f"Error: {str(e)}")
    
    return redirect(url_for('menu'))

@app.route('/menu/delete/<int:id>', methods=['POST'])
@login_required
def delete_menu_item_route(id):
    if current_user.role != 'manager':
        flash('You do not have permission to delete menu items', 'danger')
        return redirect(url_for('menu'))

    try:
        item = MenuItem.query.get_or_404(id)
        # First delete related order items
        OrderItem.query.filter_by(menu_item_id=id).delete()
        db.session.delete(item)
        db.session.commit()
        flash('Menu item deleted', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting menu item. It may be referenced in orders.', 'danger')
    
    return redirect(url_for('menu'))



@app.route('/staff', methods=['GET', 'POST'])
@login_required
def staff():
    if current_user.role not in ['admin', 'manager']:
        flash('You do not have permission to access staff management', 'danger')
        return redirect(url_for('dashboard'))

    form = StaffForm()

    if form.validate_on_submit():
        # Generate staff ID if not provided (will use the model's __init__ method)
        new_staff = Staff(
            name=form.name.data,
            position=form.position.data,
            contact=form.contact.data,
            staff_id=form.staff_id.data if form.staff_id.data else str(random.randint(100, 999)),
            active=form.active.data
        )

        db.session.add(new_staff)
        db.session.commit()
        flash('Staff member added successfully!', 'success')
        return redirect(url_for('staff'))

    staff_list = Staff.query.all()
    return render_template('staff.html', staff=staff_list, form=form)

@app.route('/staff/update/<int:id>', methods=['POST'])
@login_required
def update_staff_route(id):
    if current_user.role != 'admin':
        flash('You do not have permission to update staff information', 'danger')
        return redirect(url_for('staff'))

    staff_member = Staff.query.get_or_404(id)
    staff_member.name = request.form.get('name', staff_member.name)
    staff_member.position = request.form.get('position', staff_member.position)
    staff_member.contact = request.form.get('contact', staff_member.contact)
    staff_member.staff_id = request.form.get('staff_id', staff_member.staff_id)
    staff_member.active = 'active' in request.form

    db.session.commit()
    flash('Staff information updated', 'success')

    return redirect(url_for('staff'))

@app.route('/staff/delete/<int:id>', methods=['POST'])
@login_required
def delete_staff_route(id):
    if current_user.role != 'manager':
        flash('You do not have permission to delete staff records', 'danger')
        return redirect(url_for('staff'))

    staff_member = Staff.query.get_or_404(id)
    db.session.delete(staff_member)
    db.session.commit()
    flash('Staff record deleted', 'success')
    return redirect(url_for('staff'))


# Helper functions for dashboard chart data (previously in reports section)
def get_daily_sales():
    """Generate daily sales data for dashboard"""
    try:
        orders = Order.query.all()
        if not orders:
            # Return sample data for demonstration with INR values
            return {
                'dates': ['2025-04-10', '2025-04-11', '2025-04-12', '2025-04-13', '2025-04-14'],
                'sales': [8500.00, 9200.50, 7600.75, 12500.25, 11000.00]
            }

        # Group orders by date and calculate total sales
        sales_by_date = {}
        for order in orders:
            date_str = order.timestamp.strftime('%Y-%m-%d')
            if date_str in sales_by_date:
                sales_by_date[date_str] += order.total
            else:
                sales_by_date[date_str] = order.total

        # Sort by date
        sorted_dates = sorted(sales_by_date.keys())
        sorted_sales = [float(sales_by_date[date]) for date in sorted_dates]

        return {
            'dates': sorted_dates,
            'sales': sorted_sales
        }
    except Exception as e:
        # If any error occurs, return sample data with INR values
        print(f"Error in get_daily_sales: {e}")
        return {
            'dates': ['2025-04-10', '2025-04-11', '2025-04-12', '2025-04-13', '2025-04-14'],
            'sales': [8500.00, 9200.50, 7600.75, 12500.25, 11000.00]
        }

def get_popular_items():
    """Generate popular items data for dashboard"""
    try:
        # Check if we have any order items
        if not OrderItem.query.first():
            # Return sample data for demonstration
            return {
                'items': ['Espresso', 'Cappuccino', 'Latte', 'Mocha', 'Americano'],
                'counts': [42, 38, 30, 25, 20]
            }

        # Query to get the most popular menu items
        popular_items_query = db.session.query(
            MenuItem.name, 
            db.func.count(OrderItem.id).label('count')
        ).join(
            OrderItem, MenuItem.id == OrderItem.menu_item_id
        ).group_by(
            MenuItem.name
        ).order_by(
            db.desc('count')
        ).limit(5).all()

        items = [item[0] for item in popular_items_query]
        counts = [int(item[1]) for item in popular_items_query]

        return {
            'items': items,
            'counts': counts
        }
    except Exception as e:
        # If any error occurs, return sample data
        print(f"Error in get_popular_items: {e}")
        return {
            'items': ['Espresso', 'Cappuccino', 'Latte', 'Mocha', 'Americano'],
            'counts': [42, 38, 30, 25, 20]
        }