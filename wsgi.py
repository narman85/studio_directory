import sys
import os

# Import and set environment variables
import env_vars

# Add application directory to path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

from app import app as application

if __name__ == '__main__':
    application.run()
