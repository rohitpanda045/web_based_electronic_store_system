import os
from dotenv import load_dotenv

# Load environment variables from .env in the same directory as this file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key_123')
    
    # Database Configuration
    DB_TYPE = os.environ.get('DB_TYPE', 'sqlite') # Default to sqlite for easy local setup
    
    if DB_TYPE == 'mysql':
        DB_USER = os.environ.get('DB_USER', 'root')
        DB_PASSWORD = os.environ.get('DB_PASSWORD', 'uxnLFmmHCnLVblKklWKEGxJFrcgqxUcu')
        DB_HOST = os.environ.get('DB_HOST', 'switchyard.proxy.rlwy.net')
        DB_PORT = os.environ.get('DB_PORT', '26497')
        DB_NAME = os.environ.get('DB_NAME', 'railway')
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        DB_NAME = os.environ.get('DB_NAME', 'local_store.db')
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_NAME}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
