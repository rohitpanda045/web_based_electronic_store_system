# Blueprint exports
from .html_routes import html_bp
from .api_auth import auth_bp
from .api_products import products_bp
from .api_orders import orders_bp
from .api_admin import admin_bp
from .api_chat import chat_bp

def register_blueprints(app):
    app.register_blueprint(html_bp)
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(products_bp, url_prefix='/api')
    app.register_blueprint(orders_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(chat_bp, url_prefix='/api')
