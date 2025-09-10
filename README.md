Coffee House Management System
A comprehensive, web-based management system for a coffee house, built with Python, Flask, and SQLAlchemy. This application provides role-based access for administrators, managers, and staff to manage orders, menu items, staff, and view sales analytics.

✨ Features
Role-Based Access Control:

Admin: Full system access. Can manage staff, menu, and orders.

Manager: Can manage menu items and view reports.

Staff: Can view and manage orders.

Dashboard Analytics: A central dashboard with key metrics like total sales, total orders, and active staff count. Visual charts display daily sales trends and the most popular menu items.

Order Management: Create new orders, update their status (e.g., Pending, Completed, Cancelled), and view a history of all transactions.

Menu Management: Easily add, edit, and delete coffee, tea, pastries, and other menu items. Mark items as available or unavailable.

Staff Management: Add new staff members, update their details (position, contact), and manage their active status.

Responsive UI: A clean and modern user interface that works seamlessly across desktops, tablets, and mobile devices.

🚀 Getting Started
Follow these instructions to get a local copy of the project up and running.

Prerequisites
Python 3.11+

A database like PostgreSQL or you can use SQLite for local development by changing the config.

Installation & Setup
Clone the Repository:

git clone [https://github.com/your-username/coffee-house-management.git](https://github.com/your-username/coffee-house-management.git)
cd coffee-house-management

Create a Virtual Environment:

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
py -m venv venv
venv\Scripts\activate

Install Dependencies:

pip install -r requirements.txt

Configure Environment Variables:
Create a .env file in the root directory. For local development, you can use SQLite.

For SQLite (simple setup):

# A strong, random secret key for session management
SESSION_SECRET="your_strong_secret_key"
# Database URL for SQLite
DATABASE_URL="sqlite:///coffeehouse.db"

For PostgreSQL (production setup):

# A strong, random secret key for session management
SESSION_SECRET="your_strong_secret_key"
# Your PostgreSQL database connection string
# Format: postgresql://[user]:[password]@[host]:[port]/[dbname]
DATABASE_URL="postgresql://user:password@localhost:5432/coffee_db"

Run the Application:

flask run

The application will be available at http://127.0.0.1:5000.

📋 Usage
Default Login Credentials:

Admin: username: admin, password: admin123

Manager: username: manager, password: manager123

Staff: username: staff, password: staff123

Navigate through the sidebar to access different management pages based on your role.

The dashboard provides an at-a-glance view of the coffee house's performance.

🛠️ Built With
Flask - The web framework used.

SQLAlchemy - The ORM for database interaction.

Flask-Login - For handling user sessions.

Flask-WTF - For form handling and validation.

Chart.js - For creating interactive charts.

📜 License
This project is licensed under the MIT License - see the LICENSE file for details.