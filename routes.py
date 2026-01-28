from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from functools import wraps
import random

from models import db, User, MenuItem, Staff, Order, OrderItem, AuditLog
from forms import LoginForm, OrderForm, MenuItemForm, StaffForm, UserForm

def register_routes(app, login_manager):
    """Register all routes for the application"""
    
    # -------- DECORATORS --------
    def require_role(*roles):
        """Decorator to require specific roles"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_user.is_authenticated or current_user.role not in roles:
                    flash(f"Access denied. Required role: {', '.join(roles)}", "danger")
                    return redirect(url_for('dashboard'))
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def log_action(action, description=""):
        """Log user action to audit log"""
        if current_user.is_authenticated:
            log = AuditLog(user_id=current_user.id, action=action, description=description)
            db.session.add(log)
            db.session.commit()
    
    # -------- Helper Functions --------
    def get_daily_sales():
        return {
            "dates": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "sales": [8500, 9200, 7600, 12500, 11000]
        }

    def get_popular_items():
        return {
            "items": ["Espresso", "Latte", "Mocha"],
            "counts": [42, 30, 25]
        }
    
    # ---------------- LOGIN LOADER ----------------
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # -------- AUTH ROUTES --------
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))
            flash("Invalid username or password", "danger")
        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Logged out successfully", "success")
        return redirect(url_for("login"))

    # -------- DASHBOARD --------
    @app.route("/dashboard")
    @login_required
    def dashboard():
        orders = Order.query.all()
        total_orders = len(orders)
        total_sales = sum(order.total for order in orders)
        active_staff = Staff.query.filter_by(active=True).count()

        daily_sales = get_daily_sales()
        popular_items = get_popular_items()

        return render_template(
            "dashboard.html",
            total_orders=total_orders,
            total_sales=total_sales,
            active_staff=active_staff,
            daily_sales=daily_sales,
            popular_items=popular_items
        )

    # -------- ORDERS --------
    @app.route("/orders", methods=["GET", "POST"])
    @login_required
    def orders():
        form = OrderForm()
        menu_items = MenuItem.query.filter_by(available=True).all()
        staff_members = Staff.query.filter_by(active=True).all()

        form.menu_items.choices = [(i.id, f"{i.name} - ₹{i.price}") for i in menu_items]
        form.staff_id.choices = [(s.id, s.name) for s in staff_members]

        if form.validate_on_submit():
            selected_items = MenuItem.query.filter(MenuItem.id.in_(form.menu_items.data)).all()
            total = sum(i.price for i in selected_items)

            order = Order(
                customer_name=form.customer_name.data,
                staff_id=form.staff_id.data,
                timestamp=datetime.now(),
                status="Pending",
                total=total
            )

            db.session.add(order)
            db.session.flush()

            for item in selected_items:
                db.session.add(OrderItem(order_id=order.id, menu_item_id=item.id, quantity=1))

            db.session.commit()
            flash("Order added successfully", "success")
            return redirect(url_for("orders"))

        orders_list = Order.query.order_by(Order.timestamp.desc()).all()
        return render_template("orders.html", orders=orders_list, form=form)

    @app.route("/order/update_status/<int:id>", methods=["POST"])
    @login_required
    @require_role("admin", "manager")
    def update_order_status(id):
        order = Order.query.get_or_404(id)
        new_status = request.form.get("status")
        old_status = order.status
        
        if new_status in ["Pending", "In Progress", "Completed", "Cancelled"]:
            order.status = new_status
            db.session.commit()
            log_action("UPDATE_ORDER_STATUS", f"Order #{order.id}: {old_status} → {new_status}")
            flash(f"Order status updated to {new_status}", "success")
        
        return redirect(url_for("orders"))

    @app.route("/order/remove/<int:id>", methods=["POST"])
    @login_required
    @require_role("admin", "manager")
    def remove_order(id):
        order = Order.query.get_or_404(id)
        order_id = order.id
        db.session.delete(order)
        db.session.commit()
        log_action("DELETE_ORDER", f"Deleted order #{order_id}")
        flash("Order removed", "success")
        return redirect(url_for("orders"))

    # -------- MENU --------
    @app.route("/menu", methods=["GET", "POST"])
    @login_required
    def menu():
        form = MenuItemForm()
        if form.validate_on_submit():
            if current_user.role not in ["admin", "manager"]:
                flash("Access denied", "danger")
                return redirect(url_for("menu"))
            
            item = MenuItem(
                name=form.name.data,
                description=form.description.data,
                price=form.price.data,
                category=form.category.data,
                available=form.available.data
            )
            db.session.add(item)
            db.session.commit()
            log_action("ADD_MENU_ITEM", f"Added menu item: {item.name} - ₹{item.price}")
            flash("Menu item added", "success")
            return redirect(url_for("menu"))

        menu_items = MenuItem.query.all()
        return render_template("menu.html", menu_items=menu_items, form=form)

    @app.route("/menu/delete/<int:id>", methods=["POST"])
    @login_required
    @require_role("admin", "manager")
    def delete_menu_item_route(id):
        item = MenuItem.query.get_or_404(id)
        item_name = item.name
        db.session.delete(item)
        db.session.commit()
        log_action("DELETE_MENU_ITEM", f"Deleted menu item: {item_name}")
        flash("Menu item deleted", "success")
        return redirect(url_for("menu"))

    @app.route("/menu/update/<int:id>", methods=["POST"])
    @login_required
    @require_role("admin", "manager")
    def update_menu_item_route(id):
        item = MenuItem.query.get_or_404(id)
        item.name = request.form.get("name")
        item.description = request.form.get("description")
        item.price = float(request.form.get("price"))
        item.category = request.form.get("category")
        item.available = request.form.get("available") == "on"
        
        db.session.commit()
        log_action("UPDATE_MENU_ITEM", f"Updated menu item: {item.name}")
        flash("Menu item updated", "success")
        return redirect(url_for("menu"))

    @app.route("/menu/edit/<int:id>", methods=["GET", "POST"])
    @login_required
    @require_role("admin", "manager")
    def edit_menu_item(id):
        item = MenuItem.query.get_or_404(id)
        
        if request.method == "POST":
            item.name = request.form.get("name")
            item.description = request.form.get("description")
            item.price = float(request.form.get("price"))
            item.category = request.form.get("category")
            item.available = request.form.get("available") == "on"
            
            db.session.commit()
            log_action("UPDATE_MENU_ITEM", f"Updated menu item: {item.name}")
            flash("Menu item updated successfully", "success")
            return redirect(url_for("menu"))
        
        return render_template("edit_menu_item.html", item=item)

    # -------- REPORTS --------
    @app.route("/reports")
    @login_required
    def reports():
        orders = Order.query.all()
        total_revenue = sum(order.total for order in orders)
        total_orders_count = len(orders)
        
        # Get orders by status
        pending_orders = len([o for o in orders if o.status == "Pending"])
        completed_orders = len([o for o in orders if o.status == "Completed"])
        
        # Get top performing staff
        staff_performance = {}
        for order in orders:
            if order.staff_id not in staff_performance:
                staff_performance[order.staff_id] = {'count': 0, 'total': 0, 'name': ''}
            staff_performance[order.staff_id]['count'] += 1
            staff_performance[order.staff_id]['total'] += order.total
            if order.staff_member:
                staff_performance[order.staff_id]['name'] = order.staff_member.name
        
        # Sort by total sales
        top_staff = sorted(staff_performance.items(), key=lambda x: x[1]['total'], reverse=True)[:5]
        
        # Get most ordered items
        item_counts = {}
        for order in orders:
            for item in order.items:
                menu_item = item.menu_item
                if menu_item:
                    if menu_item.id not in item_counts:
                        item_counts[menu_item.id] = {'name': menu_item.name, 'count': 0, 'revenue': 0}
                    item_counts[menu_item.id]['count'] += item.quantity
                    item_counts[menu_item.id]['revenue'] += menu_item.price * item.quantity
        
        most_ordered = sorted(item_counts.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
        
        return render_template(
            "reports.html",
            total_revenue=total_revenue,
            total_orders_count=total_orders_count,
            pending_orders=pending_orders,
            completed_orders=completed_orders,
            top_staff=top_staff,
            most_ordered=most_ordered
        )

    # -------- STAFF --------
    @app.route("/staff", methods=["GET", "POST"])
    @login_required
    @require_role("admin", "manager")
    def staff():
        form = StaffForm()
        if form.validate_on_submit():
            new_staff = Staff(
                name=form.name.data,
                position=form.position.data,
                contact=form.contact.data,
                staff_id=form.staff_id.data or str(random.randint(100, 999)),
                active=form.active.data
            )
            db.session.add(new_staff)
            db.session.commit()
            log_action("ADD_STAFF", f"Added staff member: {new_staff.name}")
            flash("Staff added", "success")
            return redirect(url_for("staff"))

        staff_list = Staff.query.all()
        return render_template("staff.html", staff=staff_list, form=form)

    @app.route("/staff/delete/<int:id>", methods=["POST"])
    @login_required
    @require_role("admin", "manager")
    def delete_staff_route(id):
        employee = Staff.query.get_or_404(id)
        emp_name = employee.name
        db.session.delete(employee)
        db.session.commit()
        log_action("DELETE_STAFF", f"Deleted staff member: {emp_name}")
        flash("Staff member deleted", "success")
        return redirect(url_for("staff"))

    @app.route("/staff/update/<int:id>", methods=["POST"])
    @login_required
    @require_role("admin", "manager")
    def update_staff_route(id):
        employee = Staff.query.get_or_404(id)
        employee.name = request.form.get("name")
        employee.position = request.form.get("position")
        employee.contact = request.form.get("contact")
        employee.active = request.form.get("active") == "on"
        
        db.session.commit()
        log_action("UPDATE_STAFF", f"Updated staff member: {employee.name}")
        flash("Staff member updated successfully", "success")
        return redirect(url_for("staff"))

    @app.route("/staff/edit/<int:id>", methods=["GET", "POST"])
    @login_required
    @require_role("admin", "manager")
    def edit_staff(id):
        staff = Staff.query.get_or_404(id)
        
        if request.method == "POST":
            staff.name = request.form.get("name")
            staff.position = request.form.get("position")
            staff.contact = request.form.get("contact")
            staff.active = request.form.get("active") == "on"
            
            db.session.commit()
            log_action("UPDATE_STAFF", f"Updated staff member: {staff.name}")
            flash("Staff member updated successfully", "success")
            return redirect(url_for("staff"))
        
        return render_template("edit_staff.html", staff=staff)

    # -------- USERS (ADMIN ONLY) --------
    @app.route("/users", methods=["GET", "POST"])
    @login_required
    @require_role("admin")
    def users():
        form = UserForm()
        if form.validate_on_submit():
            if User.query.filter_by(username=form.username.data).first():
                flash("Username already exists", "danger")
            elif User.query.filter_by(email=form.email.data).first():
                flash("Email already exists", "danger")
            else:
                new_user = User(
                    username=form.username.data,
                    email=form.email.data,
                    role=form.role.data
                )
                new_user.set_password(form.password.data)
                db.session.add(new_user)
                db.session.commit()
                log_action("CREATE_USER", f"Created user: {new_user.username} (Role: {new_user.role})")
                flash(f"User {new_user.username} created successfully", "success")
                return redirect(url_for("users"))

        users_list = User.query.all()
        return render_template("users.html", users=users_list, form=form)

    @app.route("/users/delete/<int:id>", methods=["POST"])
    @login_required
    @require_role("admin")
    def delete_user_route(id):
        if id == current_user.id:
            flash("Cannot delete your own account", "danger")
            return redirect(url_for("users"))
        
        user = User.query.get_or_404(id)
        username = user.username
        db.session.delete(user)
        db.session.commit()
        log_action("DELETE_USER", f"Deleted user: {username}")
        flash("User deleted", "success")
        return redirect(url_for("users"))

    @app.route("/users/update_role/<int:id>", methods=["POST"])
    @login_required
    @require_role("admin")
    def update_user_role(id):
        if id == current_user.id:
            flash("Cannot change your own role", "danger")
            return redirect(url_for("users"))
        
        user = User.query.get_or_404(id)
        new_role = request.form.get("role")
        
        if new_role in ["admin", "manager", "staff"]:
            old_role = user.role
            user.role = new_role
            db.session.commit()
            log_action("UPDATE_USER_ROLE", f"User {user.username}: {old_role} → {new_role}")
            flash(f"User role updated to {new_role}", "success")
        else:
            flash("Invalid role", "danger")
        
        return redirect(url_for("users"))

    # -------- API (FOR CHARTS) --------
    @app.route("/api/inventory_usage")
    @login_required
    def inventory_usage():
        return jsonify({
            "items": ["Beans", "Milk", "Syrup"],
            "levels": [20, 15, 10],
            "reorder_levels": [10, 10, 5]
        })
