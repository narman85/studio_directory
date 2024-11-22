from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from whitenoise import WhiteNoise
from supabase import create_client, Client

load_dotenv()

def create_app():
    app = Flask(__name__, 
                static_folder='../static',
                template_folder='../templates')
    
    # Set up environment variables
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key')
    app.config['SUPABASE_URL'] = os.environ.get('SUPABASE_URL')
    app.config['SUPABASE_KEY'] = os.environ.get('SUPABASE_KEY')
    app.config['ADMIN_USERNAME'] = os.environ.get('ADMIN_USERNAME', 'admin')
    app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', '1234')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize WhiteNoise for serving static files
    app.wsgi_app = WhiteNoise(app.wsgi_app, root='../static/')
    
    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'admin_login'
    
    supabase: Client = create_client(
        app.config['SUPABASE_URL'],
        app.config['SUPABASE_KEY']
    )
    
    from app import routes
    
    return app

app = create_app()
