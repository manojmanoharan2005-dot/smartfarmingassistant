import os
import sys

# Ensure root directory is in sys.path for Vercel runtime
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import the existing Flask application instance
from app import app

# Expose app for Vercel Serverless Function builder
app = app
