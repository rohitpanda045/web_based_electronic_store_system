from flask import Flask, request, jsonify
from config import Config
from extensions import db
from routes import register_blueprints
import os

def create_app():
    # Provide the template and static folder pointers exactly as before
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Sanitize inputs via global middleware (preserving exact legacy functionality)
    @app.before_request
    def validate_inputs():
        def sanitize_input(data):
            if isinstance(data, str):
                if '--' in data:
                    raise ValueError("Input contains forbidden characters ('--').")
                return data
            elif isinstance(data, dict):
                return {k: sanitize_input(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [sanitize_input(i) for i in data]
            return data
            
        try:
            if request.is_json:
                sanitize_input(request.get_json(silent=True))
            if request.form:
                sanitize_input(request.form)
            if request.args:
                sanitize_input(request.args)
        except ValueError as e:
            return jsonify({'success': False, 'message': str(e)}), 400

    # Register blueprints
    register_blueprints(app)
    
    # Optional Database Initialization on Startup (can be safely skipped if using railway persistent db)
    with app.app_context():
        try:
            db.create_all()
            
            # Seed admin if missing
            from models import Admin, Product
            if Admin.query.count() == 0:
                admin = Admin(username='rohit', password='12345')
                db.session.add(admin)
                db.session.commit()
                print("Database initialized with sample admin.")

            # Auto-update broken macbook images for existing DBs
            macbooks = Product.query.filter(Product.p_name.contains('MacBook')).all()
            for mb in macbooks:
                if "unsplash" in mb.image:
                    mb.image = "https://images.pexels.com/photos/1229861/pexels-photo-1229861.jpeg"
            db.session.commit()

            # Seed products if missing
            if Product.query.count() == 0:
                sample_products = [
                    Product(p_name="iPhone 13 Pro", price=81999.00, discount=10.00, stock=10, 
                            image="https://images.unsplash.com/photo-1632661674596-df8be070a5c5?q=80&w=1000&auto=format&fit=crop",
                            features="6.1-inch display, A15 Bionic chip, 12MP camera", warranty="2 years", category="Smartphones"),
                    Product(p_name="Samsung Galaxy S21", price=65599.00, discount=15.00, stock=15, 
                            image="https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?q=80&w=1000&auto=format&fit=crop",
                            features="6.2-inch display, Snapdragon 888, 64MP camera", warranty="2 years", category="Smartphones"),
                    Product(p_name="MacBook Air / Pro M1", price=106599.00, discount=5.00, stock=8, 
                            image="https://images.pexels.com/photos/1229861/pexels-photo-1229861.jpeg",
                            features="13-inch display, M1 chip, 8GB RAM, 256GB SSD", warranty="1 year", category="Laptops"),
                    Product(p_name="iPad Air", price=49199.00, discount=0.00, stock=12, 
                            image="https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?q=80&w=1000&auto=format&fit=crop",
                            features="10.9-inch display, A14 Bionic, WiFi connectivity", warranty="1 year", category="Tablets"),
                    Product(p_name="Sony WH-1000XM4", price=28699.00, discount=20.00, stock=20, 
                            image="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=1000&auto=format&fit=crop",
                            features="Wireless headphones, Noise cancelling, 30hr battery", warranty="2 years", category="Accessories")
                ]
                db.session.bulk_save_objects(sample_products)
                db.session.commit()
                print("Database initialized with sample products.")
        except Exception as e:
            print(f"Warning: Database creation error or DB not accessible yet: {e}")

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("DEBUG", "True").lower() == "true"
    app.run(debug=debug, host=host, port=port)
