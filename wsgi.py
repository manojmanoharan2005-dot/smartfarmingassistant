"""
WSGI entry point for production deployment
"""
from app import app

# This is the application object that should be used by WSGI servers
application = app

if __name__ == "__main__":
    app.run()
