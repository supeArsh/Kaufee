import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-dev-key")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize SQLAlchemy
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Add context processor for common template variables
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Import routes after app initialization to avoid circular imports
# This import is handled after our file is loaded, so it's fine to have it
# Since it will use our app instance

# Make sure to import routes
import routes

# Create database tables
with app.app_context():
    db.create_all()
    
    # Initialize default admin user if no users exist
    from models import User
    if not User.query.first():
        admin = User(username='admin', email='admin@coffeehouse.com', role='admin')
        admin.set_password('admin123')
        manager = User(username='manager', email='manager@coffeehouse.com', role='manager')
        manager.set_password('manager123')
        staff = User(username='staff', email='staff@coffeehouse.com', role='staff')
        staff.set_password('staff123')
        
        db.session.add(admin)
        db.session.add(manager)
        db.session.add(staff)
        db.session.commit()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
