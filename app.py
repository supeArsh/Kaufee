# This file is now just a placeholder to maintain compatibility
# All functionality has been moved to main.py and routes.py

# Import the app instance from main.py
from main import app

# This ensures that when we import 'app' from other modules, we get the app instance
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)