from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from models import db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

app.secret_key = "dev-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///coffeehouse.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["WTF_CSRF_ENABLED"] = True

csrf = CSRFProtect(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Add global template context
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

with app.app_context():
    db.create_all()
    
    # Initialize default admin user if no users exist
    if User.query.count() == 0:
        admin = User(
            username='admin',
            email='admin@coffeehouse.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin user created (username: admin, password: admin123)")

# Import and register routes AFTER app is fully initialized
from routes import register_routes
register_routes(app, login_manager)

if __name__ == "__main__":
    print("FINAL URL MAP:")
    print(app.url_map)
    app.run(debug=True, host='0.0.0.0', port=5000)
