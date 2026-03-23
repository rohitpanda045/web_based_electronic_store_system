from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import json
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

# Load environment variables from .env in the same directory as this file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.secret_key = 'your_secret_key_here'

# Category placeholder prefix - reserved for internal use; product names must not start with this
CATEGORY_PLACEHOLDER_PREFIX = 'cat_placeholder_'

# MySQL Database Configuration
db_config = {
    'host': os.getenv('DB_HOST', 'mysql.railway.internal'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'uxnLFmmHCnLVblKklWKEGxJFrcgqxUcu'),
    'database': os.getenv('DB_NAME', 'railway'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# Failed login attempt tracking
failed_logins = {} # {user_id: {'count': N, 'lock_until': datetime}}
MAX_FAILED_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 30

def sanitize_input(data):
    """Recursively check for forbidden consecutive hyphens in dictionary/list/string data to prevent SQL injection"""
    if isinstance(data, str):
        if '--' in data:
            raise ValueError("Input contains forbidden characters ('--').")
        return data
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(i) for i in data]
    return data

@app.before_request
def validate_inputs():
    """Middleware-like check for all incoming JSON or Form data"""
    try:
        if request.is_json:
            sanitize_input(request.get_json(silent=True))
        if request.form:
            sanitize_input(request.form)
        if request.args:
            sanitize_input(request.args)
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400

def get_db_connection():
    """Create a database connection"""
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    """Ensure database and tables exist"""
    # Use config without database first to ensure database exists if allowed by user
    # But since database name is given as 'railway', we assume it exists or use it directly
    conn = get_db_connection()
    if not conn:
        print("Could not connect to database for initialization.")
        return
    
    cursor = conn.cursor()
    try:
        # Create tables if they don't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ADMIN (
            admin_id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(100) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS USER (
            user_id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            address TEXT
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS PRODUCT (
            product_id INT PRIMARY KEY AUTO_INCREMENT,
            p_name VARCHAR(150) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            discount DECIMAL(5,2) DEFAULT 0.00,
            stock INT NOT NULL,
            image VARCHAR(255),
            features TEXT,
            warranty VARCHAR(100),
            category VARCHAR(100),
            category_image VARCHAR(255)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ORDERS (
            order_id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            order_date DATE NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            status VARCHAR(50) DEFAULT 'Pending',
            return_reason TEXT
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ORDER_ITEM (
            order_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT NOT NULL,
            sum_amount DECIMAL(10,2) NOT NULL,
            PRIMARY KEY (order_id, product_id),
            FOREIGN KEY (order_id) REFERENCES ORDERS(order_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id) ON DELETE CASCADE
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS CART (
            user_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            PRIMARY KEY (user_id, product_id),
            FOREIGN KEY (user_id) REFERENCES USER(user_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id) ON DELETE CASCADE
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS REVIEW (
            r_id INT PRIMARY KEY AUTO_INCREMENT,
            rating INT NOT NULL,
            comment TEXT,
            review_date DATE NOT NULL,
            user_id INT NOT NULL,
            product_id INT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES USER(user_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id) ON DELETE CASCADE
        )
        """)
        
        # Insert sample admin if missing
        cursor.execute("SELECT COUNT(*) FROM ADMIN")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO ADMIN (username, password) VALUES ('rohit', '12345')")
            
        conn.commit()
        print("Database initialized successfully.")
    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        cursor.close()
        conn.close()

# Initialize database on startup
init_db()

def generate_whatsapp_invoice_text(order_id, items, total_amount):
    """Generate a formatted invoice text for WhatsApp"""
    text = f"🏪 *TechMart Invoice*\nOrder ID: #{order_id}\n\n*Items:*\n"
    for item in items:
        text += f"• {item['p_name']} (x{item['quantity']}): ₹{item['sum_amount']:.2f}\n"
    text += f"\n*Total Amount:* ₹{total_amount:.2f}\n"
    text += "\nThank you for shopping with us!"
    return text

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registration')
def registration():
    return render_template('registration.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/products')
def products():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('products.html')

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('cart.html')

@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin')
def admin():
    # session['admin_id'] = 1 # Remove forced login for security in real app, but keep for now if needed. 
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

# API Endpoints

@app.route('/api/register', methods=['POST'])
def api_register():
    """Register a new user"""
    data = request.get_json()
    user_id = data.get('user_id')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    address = data.get('address')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor()
    try:
        # Check if user_id already exists
        cursor.execute("SELECT user_id FROM USER WHERE user_id = %s", (user_id,))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'User ID already exists'}), 400
        
        # Insert new user with hashed password
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO USER (user_id, username, email, password, address) VALUES (%s, %s, %s, %s, %s)",
                      (user_id, username, email, hashed_password, address))
        conn.commit()
        return jsonify({'success': True, 'message': 'Registration successful'}), 201
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/login', methods=['POST'])
def api_login():
    """Login user"""
    data = request.get_json()
    user_id = data.get('user_id')
    password = data.get('password')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, password FROM USER WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        # Check if account is locked
        if user_id in failed_logins:
            lock_info = failed_logins[user_id]
            if lock_info['count'] >= MAX_FAILED_ATTEMPTS:
                if datetime.now() < lock_info['lock_until']:
                    return jsonify({'success': False, 'message': f'Account locked due to multiple failed attempts. Try again after {lock_info["lock_until"].strftime("%H:%M:%S")}'}), 403
                else:
                    # Reset after lock period
                    del failed_logins[user_id]

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            # Reset failed attempts on success
            if user_id in failed_logins:
                del failed_logins[user_id]
            return jsonify({'success': True, 'message': 'Login successful'}), 200
        else:
            # Track failed attempt
            if user_id not in failed_logins:
                failed_logins[user_id] = {'count': 1, 'lock_until': datetime.now() + timedelta(minutes=LOCK_DURATION_MINUTES)}
            else:
                failed_logins[user_id]['count'] += 1
                failed_logins[user_id]['lock_until'] = datetime.now() + timedelta(minutes=LOCK_DURATION_MINUTES)
            
            remaining = MAX_FAILED_ATTEMPTS - failed_logins[user_id]['count']
            msg = 'Invalid user ID or password'
            if remaining > 0:
                msg += f'. {remaining} attempts remaining before lock.'
            else:
                msg = f'Account locked for {LOCK_DURATION_MINUTES} minutes.'
            
            return jsonify({'success': False, 'message': msg}), 401
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin_login', methods=['POST'])
def api_admin_login():
    """Login admin"""
    data = request.get_json()
    admin_id = data.get('admin_id')
    password = data.get('password')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT admin_id, password FROM ADMIN WHERE admin_id = %s", (admin_id,))
        admin = cursor.fetchone()
        
        if admin:
            # Store fetched credentials in variables
            fetched_admin_id = admin[0]
            fetched_password = admin[1]
            
            # Compare with provided credentials
            if fetched_password == password:
                session['admin_id'] = fetched_admin_id
                return jsonify({'success': True, 'message': 'Login successful'}), 200
            else:
                return jsonify({'success': False, 'message': 'Invalid admin ID or password'}), 401
        else:
            return jsonify({'success': False, 'message': 'Invalid admin ID or password'}), 401
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/products', methods=['GET'])
def api_get_products():
    """Get all products or filter by category"""
    category = request.args.get('category')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        placeholder_pattern = CATEGORY_PLACEHOLDER_PREFIX + "%"
        if category:
            cursor.execute("SELECT * FROM PRODUCT WHERE category = %s AND p_name NOT LIKE %s", (category, placeholder_pattern))
        else:
            cursor.execute("SELECT * FROM PRODUCT WHERE p_name NOT LIKE %s", (placeholder_pattern,))
        products = cursor.fetchall()
        
        # DEBUG LOGGING FOR STOCK ISSUE
        print(f"--- DEBUG: Fetching products for category {category} ---")
        for p in products:
            print(f"Product ID: {p['product_id']}, Name: {p['p_name']}, Stock: {p['stock']}")
        
        return jsonify({'success': True, 'products': products}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/add_to_cart', methods=['POST'])
def api_add_to_cart():
    """Add product to cart"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    amount = data.get('amount')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Check available stock
        cursor.execute("SELECT stock, price, discount FROM PRODUCT WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        if not product:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        
        if product['stock'] < quantity:
            return jsonify({'success': False, 'message': f'Only {product["stock"]} items available in stock'}), 400

        # Check if product already in cart
        cursor.execute("SELECT quantity, amount FROM CART WHERE user_id = %s AND product_id = %s", 
                      (user_id, product_id))
        existing = cursor.fetchone()
        
        # Calculate correct amount based on current price/discount to ensure accuracy
        price = product['price']
        discount = product['discount'] if product['discount'] else 0
        discounted_price = price - (price * discount / 100)
        
        if existing:
            new_quantity = existing['quantity'] + quantity
            if product['stock'] < new_quantity:
                return jsonify({'success': False, 'message': f'Cannot add more items. Total in cart ({new_quantity}) exceeds available stock ({product["stock"]})'}), 400
            
            new_amount = discounted_price * new_quantity
            cursor.execute("UPDATE CART SET quantity = %s, amount = %s WHERE user_id = %s AND product_id = %s",
                          (new_quantity, new_amount, user_id, product_id))
        else:
            new_amount = discounted_price * quantity
            cursor.execute("INSERT INTO CART (user_id, product_id, quantity, amount) VALUES (%s, %s, %s, %s)",
                          (user_id, product_id, quantity, new_amount))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Product added to cart'}), 201
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/get_cart', methods=['GET'])
def api_get_cart():
    """Get user's cart"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""SELECT c.product_id, p.p_name, p.price, p.discount, c.quantity, c.amount, p.image
                         FROM CART c
                         JOIN PRODUCT p ON c.product_id = p.product_id
                         WHERE c.user_id = %s""", (user_id,))
        cart_items = cursor.fetchall()
        
        # Calculate discounted price for display
        for item in cart_items:
            discount_amount = (item['price'] * item['discount']) / 100
            item['discounted_price'] = item['price'] - discount_amount
        
        return jsonify({'success': True, 'cart': cart_items}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/remove_from_cart', methods=['POST'])
def api_remove_from_cart():
    """Remove product from cart"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    product_id = data.get('product_id')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM CART WHERE user_id = %s AND product_id = %s", 
                      (user_id, product_id))
        conn.commit()
        return jsonify({'success': True, 'message': 'Product removed from cart'}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    """Create order from cart and send WhatsApp invoice"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    # ... (existing checkout logic)
    # After conn.commit():
    # send_whatsapp_invoice(order_id)
    
    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor()
    try:
        # Get cart items with discounts
        cursor.execute("SELECT c.product_id, c.quantity, c.amount, p.price, p.discount FROM CART c JOIN PRODUCT p ON c.product_id = p.product_id WHERE c.user_id = %s", (user_id,))
        cart_items = cursor.fetchall()
        
        if not cart_items:
            return jsonify({'success': False, 'message': 'Cart is empty'}), 400
        
        # Calculate total with discounted prices
        total_amount = 0
        updated_cart_items = []
        
        for item in cart_items:
            product_id, quantity, stored_amount, price, discount = item
            discount = discount if discount else 0
            discounted_price = price - (price * discount / 100)
            item_total = discounted_price * quantity
            total_amount += item_total
            updated_cart_items.append((product_id, quantity, item_total))
        
        # Create order
        cursor.execute("INSERT INTO ORDERS (user_id, order_date, total_amount) VALUES (%s, %s, %s)",
                      (user_id, datetime.now().date(), total_amount))
        order_id = cursor.lastrowid
        
        # Add order items and update stock
        order_items_details = []
        for product_id, quantity, amount in updated_cart_items:
            # Verify stock one last time before reduction (handles items added to cart earlier)
            cursor.execute("SELECT p_name, stock FROM PRODUCT WHERE product_id = %s", (product_id,))
            p_data = cursor.fetchone()
            if not p_data or p_data[1] < quantity:
                conn.rollback()
                return jsonify({'success': False, 'message': f'Insufficient stock for {p_data[0] if p_data else "Product ID "+str(product_id)}. Please update your cart.'}), 400
            
            p_name = p_data[0]
            current_product_stock = p_data[1]
            order_items_details.append({'p_name': p_name, 'quantity': quantity, 'sum_amount': amount})

            cursor.execute("INSERT INTO ORDER_ITEM (order_id, product_id, quantity, sum_amount) VALUES (%s, %s, %s, %s)",
                          (order_id, product_id, quantity, amount))
            
            # Decrease product stock with race condition protection
            print(f"--- DEBUG: Updating stock for product_id {product_id} ---")
            print(f"Current stock: {current_product_stock}, Attempting to subtract: {quantity}")
            
            cursor.execute("UPDATE PRODUCT SET stock = stock - %s WHERE product_id = %s AND stock >= %s",
                          (quantity, product_id, quantity))
            
            if cursor.rowcount == 0:
                conn.rollback()
                return jsonify({'success': False, 'message': f'Stock for {p_name} was updated by another process. Please try again.'}), 409
            
            # Re-verify stock immediately for debug
            cursor.execute("SELECT p_name, stock FROM PRODUCT WHERE product_id = %s", (product_id,))
            v_p = cursor.fetchone()
            print(f"Post-update verification: {v_p}")
        
        # Clear cart
        cursor.execute("DELETE FROM CART WHERE user_id = %s", (user_id,))
        conn.commit()
        
        invoice_text = generate_whatsapp_invoice_text(order_id, order_items_details, total_amount)
        
        return jsonify({'success': True, 'message': 'Order placed successfully', 'order_id': order_id, 'invoice_text': invoice_text}), 201
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/buy_now', methods=['POST'])
def api_buy_now():
    """Buy product directly"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Get product price, discount and STOCK
        cursor.execute("SELECT price, discount, stock, p_name FROM PRODUCT WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        
        if product['stock'] < quantity:
            return jsonify({'success': False, 'message': f'Insufficient stock. Only {product["stock"]} available.'}), 400
            
        price = product['price']
        discount = product['discount'] if product['discount'] else 0
        discounted_price = price - (price * discount / 100)
        total_amount = discounted_price * quantity
        p_name = product['p_name']
        
        # Create order
        cursor.execute("INSERT INTO ORDERS (user_id, order_date, total_amount) VALUES (%s, %s, %s)",
                      (user_id, datetime.now().date(), total_amount))
        order_id = cursor.lastrowid
        
        # Add order item
        cursor.execute("INSERT INTO ORDER_ITEM (order_id, product_id, quantity, sum_amount) VALUES (%s, %s, %s, %s)",
                      (order_id, product_id, quantity, total_amount))
        
        # Decrease product stock with a check to ensure it doesn't drop below zero
        print(f"--- DEBUG: Updating stock for product_id {product_id} ---")
        print(f"Current stock: {product['stock']}, Attempting to subtract: {quantity}")
        
        cursor.execute("UPDATE PRODUCT SET stock = stock - %s WHERE product_id = %s AND stock >= %s",
                      (quantity, product_id, quantity))
        
        if cursor.rowcount == 0:
            # This should ideally not happen because of the check above, but handles race conditions
            conn.rollback()
            return jsonify({'success': False, 'message': 'Stock was updated by another process. Please try again.'}), 409
        
        # Re-verify stock immediately for debug
        cursor.execute("SELECT p_name, stock FROM PRODUCT WHERE product_id = %s", (product_id,))
        v_p = cursor.fetchone()
        print(f"Post-update verification: {v_p}")
        
        conn.commit()
        
        invoice_text = generate_whatsapp_invoice_text(order_id, [{'p_name': p_name, 'quantity': quantity, 'sum_amount': total_amount}], total_amount)
        
        return jsonify({'success': True, 'message': 'Order placed successfully', 'order_id': order_id, 'invoice_text': invoice_text}), 201
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/categories_with_count', methods=['GET'])
def api_categories_with_count():
    """Get all product categories with product counts and images"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor()
    try:
        placeholder_like = CATEGORY_PLACEHOLDER_PREFIX + "%"
        cursor.execute("""
            SELECT p.category, 
                   SUM(CASE WHEN p.p_name NOT LIKE %s THEN 1 ELSE 0 END) as product_count, 
                   (SELECT category_image FROM PRODUCT sub 
                    WHERE sub.category = p.category AND category_image IS NOT NULL AND category_image != '' LIMIT 1) as category_image
            FROM PRODUCT p 
            GROUP BY p.category 
            ORDER BY p.category
        """, (placeholder_like,))
        categories = []
        for row in cursor.fetchall():
            categories.append({
                'category': row[0],
                'product_count': row[1],
                'category_image': row[2] if row[2] else '20260128190942_s25_ultra.jpg'  # default image
            })
        return jsonify({'success': True, 'categories': categories}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/add_category', methods=['POST'])
def api_add_category():
    """Add new product category (Admin)"""
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    data = request.get_json()
    category_name = data.get('category', '').strip()
    category_image = data.get('category_image', '').strip()
    
    if not category_name:
        return jsonify({'success': False, 'message': 'Category name is required'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor()
    try:
        # Check if category already exists (including placeholder)
        cursor.execute("SELECT COUNT(*) FROM PRODUCT WHERE category = %s", (category_name,))
        if cursor.fetchone()[0] > 0:
            return jsonify({'success': False, 'message': 'Category already exists'}), 400
        
        # Insert a placeholder product to establish the category (categories are derived from PRODUCT.category)
        # Placeholder is filtered from product listings via p_name LIKE 'cat_placeholder_%'
        cursor.execute("""
            INSERT INTO PRODUCT (p_name, price, discount, stock, image, features, warranty, category, category_image) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (f"{CATEGORY_PLACEHOLDER_PREFIX}{category_name}", 0.00, 0.00, 0, "", "", "", category_name, category_image))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Category added successfully'}), 201
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/delete_category', methods=['POST'])
def api_delete_category():
    """Delete product category (Admin)"""
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    data = request.get_json()
    category_name = data.get('category', '').strip()
    
    if not category_name:
        return jsonify({'success': False, 'message': 'Category name is required'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor()
    try:
        placeholder_pattern = CATEGORY_PLACEHOLDER_PREFIX + "%"
        # Delete placeholder products (they only exist to establish the category; no user data)
        cursor.execute("DELETE FROM PRODUCT WHERE category = %s AND p_name LIKE %s",
                       (category_name, placeholder_pattern))
        # Move remaining real products to "Uncategorized"
        cursor.execute("UPDATE PRODUCT SET category = 'Uncategorized' WHERE category = %s", (category_name,))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Category deleted successfully'}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/categories', methods=['GET'])
def api_categories():
    """Get all product categories"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT category FROM PRODUCT ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        return jsonify({'success': True, 'categories': categories}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/add_product', methods=['POST'])
def api_add_product():
    """Add new product (Admin)"""
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['p_name', 'price', 'stock', 'image', 'features', 'warranty', 'category']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'{field} is required'}), 400
    
    # Reject product names that conflict with internal category placeholder naming
    p_name = str(data.get('p_name', '')).strip()
    if p_name.startswith(CATEGORY_PLACEHOLDER_PREFIX):
        return jsonify({'success': False, 'message': f'Product name cannot start with "{CATEGORY_PLACEHOLDER_PREFIX}" (reserved for system use)'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO PRODUCT (p_name, price, discount, stock, image, features, warranty, category) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                      (data.get('p_name'), data.get('price'), data.get('discount', 0), data.get('stock'), 
                       data.get('image'), data.get('features'), data.get('warranty'), data.get('category')))
        conn.commit()
        return jsonify({'success': True, 'message': 'Product added successfully'}), 201
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/get_all_orders', methods=['GET'])
def api_get_all_orders():
    """Get all orders (Admin)"""
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""SELECT o.order_id, o.user_id, u.username, DATE_FORMAT(o.order_date, '%Y-%m-%d') as order_date, 
                                o.total_amount, o.status, o.return_reason, GROUP_CONCAT(p.p_name SEPARATOR ', ') as product_names
                         FROM ORDERS o
                         JOIN USER u ON o.user_id = u.user_id
                         LEFT JOIN ORDER_ITEM oi ON o.order_id = oi.order_id
                         LEFT JOIN PRODUCT p ON oi.product_id = p.product_id
                         GROUP BY o.order_id
                         ORDER BY o.order_date DESC""")
        orders = cursor.fetchall()
        return jsonify({'success': True, 'orders': orders}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/get_order_details/<int:order_id>', methods=['GET'])
def api_get_order_details(order_id):
    """Get order details"""
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""SELECT oi.product_id, p.p_name, oi.quantity, oi.sum_amount, p.price, o.status, o.return_reason
                         FROM ORDER_ITEM oi
                         JOIN PRODUCT p ON oi.product_id = p.product_id
                         JOIN ORDERS o ON oi.order_id = o.order_id
                         WHERE oi.order_id = %s""", (order_id,))
        results = cursor.fetchall()
        
        # Get return reason if any
        return_reason = results[0]['return_reason'] if results else None
        
        return jsonify({'success': True, 'items': results, 'return_reason': return_reason}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/generate_bill/<int:order_id>', methods=['GET'])
def generate_bill(order_id):
    """Generate HTML bill for printing or PDF"""
    if 'user_id' not in session and 'admin_id' not in session:
        return "Unauthorized: Please log in to view bills.", 401

    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Check authorization (if user is logged in, they must own the order)
        if 'user_id' in session and 'admin_id' not in session:
            cursor.execute("SELECT user_id FROM ORDERS WHERE order_id = %s", (order_id,))
            order_owner = cursor.fetchone()
            if not order_owner or order_owner['user_id'] != session['user_id']:
                return "Unauthorized: You do not have permission to view this bill.", 403

        # Fetch Order details
        cursor.execute("""
            SELECT o.order_id, o.order_date, o.total_amount, o.status, u.username, u.email
            FROM ORDERS o
            JOIN USER u ON o.user_id = u.user_id
            WHERE o.order_id = %s
        """, (order_id,))
        order = cursor.fetchone()

        if not order:
            return "Order not found", 404

        # Fetch Order Items
        cursor.execute("""
            SELECT p.p_name, oi.quantity, p.price, oi.sum_amount
            FROM ORDER_ITEM oi
            JOIN PRODUCT p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cursor.fetchall()
        
        return render_template('invoice.html', order=order, items=items)

    except Error as e:
        return str(e), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/analytics', methods=['GET'])
def api_admin_analytics():
    """Get dashboard analytics (Admin)"""
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor()
    try:
        # Total Sales
        cursor.execute("SELECT SUM(total_amount) FROM ORDERS WHERE status = 'Delivered'")
        total_sales = cursor.fetchone()[0] or 0.00
        
        # Total Orders
        cursor.execute("SELECT COUNT(*) FROM ORDERS")
        total_orders = cursor.fetchone()[0]
        
        # Total Users
        cursor.execute("SELECT COUNT(*) FROM USER")
        total_users = cursor.fetchone()[0]
        
        return jsonify({
            'success': True, 
            'total_sales': float(total_sales),
            'total_orders': total_orders,
            'total_users': total_users
        }), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/delivered_products', methods=['GET'])
def api_delivered_products():
    """Get list of delivered products with price details"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.p_name, p.price, p.discount, oi.quantity, oi.sum_amount, DATE_FORMAT(o.order_date, '%Y-%m-%d') as order_date
            FROM ORDER_ITEM oi
            JOIN PRODUCT p ON oi.product_id = p.product_id
            JOIN ORDERS o ON oi.order_id = o.order_id
            WHERE o.user_id = %s AND o.status = 'Delivered'
            ORDER BY o.order_date DESC
        """, (user_id,))
        products = cursor.fetchall()
        return jsonify({'success': True, 'products': products}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/update_order_status', methods=['POST'])
def api_update_order_status():
    """Update order status (Admin)"""
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    data = request.get_json()
    order_id = data.get('order_id')
    status = data.get('status')
    
    valid_statuses = ['Pending', 'Shipped', 'On the way', 'Out for delivery', 'Delivered', 'Return Requested', 'Returned']
    if status not in valid_statuses:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE ORDERS SET status = %s WHERE order_id = %s", (status, order_id))
        conn.commit()
        
        return jsonify({'success': True, 'message': f'Order marked as {status}'}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/delivered_products', methods=['GET'])
def api_admin_delivered_products():
    """Get list of all delivered products across all users (Admin)"""
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT o.order_id, u.username, p.p_name, oi.quantity, oi.sum_amount, DATE_FORMAT(o.order_date, '%Y-%m-%d') as order_date
            FROM ORDER_ITEM oi
            JOIN PRODUCT p ON oi.product_id = p.product_id
            JOIN ORDERS o ON oi.order_id = o.order_id
            JOIN USER u ON o.user_id = u.user_id
            WHERE o.status = 'Delivered'
            ORDER BY o.order_date DESC
        """)
        products = cursor.fetchall()
        return jsonify({'success': True, 'products': products}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/update_category_image', methods=['POST'])
def api_update_category_image():
    """Update category image (Admin)"""
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    data = request.get_json()
    category_name = data.get('category', '').strip()
    category_image = data.get('category_image', '').strip()
    
    if not category_name:
        return jsonify({'success': False, 'message': 'Category name is required'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor()
    try:
        # Update category_image for all products in this category
        cursor.execute("UPDATE PRODUCT SET category_image = %s WHERE category = %s", (category_image, category_name))
        conn.commit()
        return jsonify({'success': True, 'message': 'Category image updated successfully'}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/get_all_users', methods=['GET'])
def api_get_all_users():
    """Get all users (Admin)"""
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_id, username, email FROM USER")
        users = cursor.fetchall()
        return jsonify({'success': True, 'users': users}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/chatbot', methods=['POST'])
def api_chatbot():
    """AI chatbot for electronic products"""
    import urllib.request
    import json
    
    data = request.get_json()
    user_message = data.get('message', '').lower().strip()
    
    if not user_message:
        return jsonify({'success': True, 'response': 'Please ask me something!'}), 200
    
    # Try Gemini API first, fallback to original logic if it fails
    try:
        api_key = "AIzaSyBBWBTdar33sLoNlSbwx43sVZ-fH69fKiY"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        # Get all products from database
        conn = get_db_connection()
        products = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("SELECT p_name, price, features, warranty, category FROM PRODUCT")
                products = cursor.fetchall()
            except Error:
                products = []
            finally:
                cursor.close()
                conn.close()
        
        # Format product information for AI
        product_info = ""
        if products:
            for p in products:
                product_info += f"{p['p_name']} - ₹{p['price']}. Category: {p['category']}. Features: {p['features']}. Warranty: {p['warranty']}\\n"
        
        # Build prompt: explicitly forbid asterisks
        prompt = f"You are a helpful AI assistant for TechMart, an online electronic store. Help customers choose products, explain specifications, prices, and offers. Be friendly and professional.\\n\\nCRITICAL RULES FOR YOUR RESPONSES:\\n1. ALWAYS provide your answers in a concise format.\\n2. NEVER write long, lengthy paragraphs. Keep it short and scannable.\\n3. DO NOT use asterisks (**) for bolding or any other purpose. Use plain text or other markers if needed.\\n4. Provide step-by-step or bulleted lists WITHOUT using asterisks as bullets.\\n\\nAvailable products in our store:\\n{product_info}\\n\\nCustomer message: {user_message}"
        
        # Prepare request
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 500
            }
        }
        
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        
        ai_response = result['candidates'][0]['content']['parts'][0]['text']
        
        # Save to chat history
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS online_store.chat_history (id INT AUTO_INCREMENT PRIMARY KEY, user_message TEXT, bot_reply TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
                )
                cursor.execute(
                    "INSERT INTO online_store.chat_history (user_message, bot_reply) VALUES (%s, %s)",
                    (user_message, ai_response)
                )
                conn.commit()
                cursor.close()
                conn.close()
        except Exception:
            pass
        
        return jsonify({'success': True, 'response': ai_response}), 200
        
    except Exception as e:
        # Fallback to original logic if AI fails
        print(f"OpenAI error: {e}")
        return original_chatbot_logic(user_message)

def original_chatbot_logic(user_message):
    """Fallback chatbot logic with enhanced comparison capabilities"""
    # Get all products from database
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': True, 'response': 'I\'m temporarily unavailable. Please try again later.'}), 200
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT p_name, price, features, warranty, category FROM PRODUCT")
        products = cursor.fetchall()
    except Error:
        products = []
    finally:
        cursor.close()
        conn.close()
    
    # Enhanced keywords for better detection
    electronics_keywords = ['phone', 'laptop', 'iphone', 'samsung', 'product', 'price', 'specs', 'features', 
                          'warranty', 'buy', 'order', 'galaxy', 'macbook', 'dell', 'hp', 'asus', 'tablet',
                          'camera', 'headphones', 'speaker', 'monitor', 'keyboard', 'mouse', 'charger',
                          'battery', 'processor', 'ram', 'storage', 'display', 'screen', 'camera', 'specs',
                          'electronic', 'gadget', 'device', 'tech', 'tech store', 'electronics store',
                          'compare', 'comparison', 'better', 'best', 'vs', 'versus', 'difference']
    
    comparison_keywords = ['compare', 'vs', 'versus', 'better', 'best', 'difference', 'which is better', 
                          'compare with', 'compared to', 'pros and cons', 'advantages', 'disadvantages']
    
    # Check if question is about electronics
    is_electronics_related = any(keyword in user_message for keyword in electronics_keywords)
    is_comparison_request = any(keyword in user_message for keyword in comparison_keywords)
    
    # Greeting responses
    greetings = ['hello', 'hi', 'hey', 'greetings', 'namaste']
    farewells = ['bye', 'goodbye', 'thanks', 'thank you', 'no thanks']
    
    if any(greeting in user_message for greeting in greetings):
        return jsonify({'success': True, 'response': 'Hello! 👋 Welcome to TechMart! I\'m here to help you with electronic products and gadgets. What can I assist you with?'}), 200
    
    if any(farewell in user_message for farewell in farewells):
        return jsonify({'success': True, 'response': 'Thank you for visiting TechMart! Feel free to ask anytime. Have a great day! 😊'}), 200
    
    # Handle product comparisons
    if is_comparison_request and products:
        return handle_product_comparison(user_message, products)
    
    # Check for product queries
    if 'product' in user_message or 'available' in user_message or 'stock' in user_message:
        if products:
            product_list = '\n'.join([f"• {p['p_name']} - ₹{p['price']}" for p in products])
            return jsonify({'success': True, 'response': f'We have these electronic products available:\n\n{product_list}\n\nWould you like more information about any product?'}), 200
        else:
            return jsonify({'success': True, 'response': 'We currently have no products in stock. Please check back soon!'}), 200
    
    # Check for price queries
    if 'price' in user_message or 'cost' in user_message or 'how much' in user_message:
        if products:
            price_info = '\n'.join([f"• {p['p_name']}: ₹{p['price']}" for p in products])
            return jsonify({'success': True, 'response': f'Here are our current prices:\n\n{price_info}\n\nInterested in any of these?'}), 200
        else:
            return jsonify({'success': True, 'response': 'I don\'t have pricing information available at the moment.'}), 200
    
    # Check for feature/specs queries
    if 'feature' in user_message or 'specs' in user_message or 'specifications' in user_message:
        if products:
            specs_info = '\n'.join([f"• {p['p_name']}: {p['features']}" for p in products if p['features']])
            if specs_info:
                return jsonify({'success': True, 'response': f'Here are the features of our products:\n\n{specs_info}'}), 200
        return jsonify({'success': True, 'response': 'Please visit our product page to view detailed specifications.'}), 200
    
    # Check for warranty queries
    if 'warranty' in user_message or 'guarantee' in user_message:
        warranty_info = '\n'.join([f"• {p['p_name']}: {p['warranty']}" for p in products if p['warranty']])
        if warranty_info:
            return jsonify({'success': True, 'response': f'Our warranty information:\n\n{warranty_info}'}), 200
        return jsonify({'success': True, 'response': 'Most of our electronic products come with 1-2 year warranty. Please check product details for specific information.'}), 200
    
    # If question is not about electronics
    if not is_electronics_related:
        return jsonify({'success': True, 'response': 'I\'m specialized in electronic products and gadgets. Please ask me questions related to our tech products, pricing, features, or warranty! 📱💻'}), 200
    
    # Generic helpful response
    return jsonify({'success': True, 'response': 'That\'s a great question! I specialize in electronics and gadgets. Feel free to ask about our products, prices, features, warranty, or anything else related to technology!'}), 200

def handle_product_comparison(user_message, products):
    """Handle product comparison requests with detailed analysis"""
    
    # Extract product names from the message
    product_names = []
    for product in products:
        product_name_lower = product['p_name'].lower()
        # Check if product name is mentioned in the query
        if product_name_lower in user_message or product_name_lower.replace(' ', '') in user_message.replace(' ', ''):
            product_names.append(product)
    
    # If no specific products mentioned, compare all products
    if len(product_names) < 2:
        product_names = products[:3]  # Compare first 3 products if not specified
    
    if len(product_names) < 2:
        return jsonify({'success': True, 'response': 'I need at least 2 products to compare. Please specify which products you\'d like to compare.'}), 200
    
    # Generate detailed comparison
    comparison_result = generate_detailed_comparison(product_names)
    return jsonify({'success': True, 'response': comparison_result}), 200

def generate_detailed_comparison(products):
    """Generate detailed product comparison with pros and cons"""
    
    comparison_text = "📊 **PRODUCT COMPARISON ANALYSIS** 📊\n\n"
    
    # Header with products being compared
    product_names = [p['p_name'] for p in products]
    comparison_text += f"Comparing: {' vs '.join(product_names)}\n\n"
    
    # Price comparison
    comparison_text += "💰 **PRICE COMPARISON**\n"
    sorted_by_price = sorted(products, key=lambda x: x['price'])
    for i, product in enumerate(sorted_by_price):
        price_rank = ["🏆 Best Value", "🥈 Mid-range", "🥉 Premium"][i] if i < 3 else f"#{i+1}"
        comparison_text += f"• {product['p_name']}: ₹{product['price']} {price_rank}\n"
    comparison_text += "\n"
    
    # Feature analysis
    comparison_text += "⚡ **FEATURE ANALYSIS**\n"
    for product in products:
        features = product['features'] if product['features'] else "Standard features"
        comparison_text += f"\n**{product['p_name']}**:\n"
        
        # Extract key features and categorize as pros/cons
        feature_list = features.lower().split('.')
        pros = []
        cons = []
        
        # Common positive feature indicators
        positive_indicators = ['high', 'fast', 'large', 'premium', 'advanced', 'latest', 'excellent', 'superior']
        negative_indicators = ['basic', 'standard', 'limited', 'budget', 'entry-level']
        
        for feature in feature_list:
            feature = feature.strip()
            if not feature:
                continue
                
            if any(pos in feature for pos in positive_indicators):
                pros.append(feature.capitalize())
            elif any(neg in feature for neg in negative_indicators):
                cons.append(feature.capitalize())
            else:
                # Neutral features - categorize based on context
                if 'gb' in feature or 'mp' in feature or 'ghz' in feature:
                    pros.append(feature.capitalize())
                else:
                    pros.append(feature.capitalize())  # Default to pros for neutral features
    
        # Add pros
        if pros:
            comparison_text += "✅ **Strengths:**\n"
            for pro in pros[:3]:  # Limit to 3 main pros
                comparison_text += f"   • {pro}\n"
        
        # Add cons
        if cons:
            comparison_text += "⚠️ **Considerations:**\n"
            for con in cons[:2]:  # Limit to 2 main cons
                comparison_text += f"   • {con}\n"
        else:
            # Generate some cons based on missing premium features
            comparison_text += "⚠️ **Considerations:**\n"
            comparison_text += "   • May lack premium features found in higher-end models\n"
            comparison_text += "   • Standard specifications for basic usage\n"
        
        comparison_text += "\n"
    
    # Warranty comparison
    comparison_text += "🛡️ **WARRANTY & SUPPORT**\n"
    warranty_info = []
    for product in products:
        warranty = product['warranty'] if product['warranty'] else "1 year standard"
        warranty_info.append(f"• {product['p_name']}: {warranty}")
    comparison_text += "\n".join(warranty_info) + "\n\n"
    
    # Recommendation
    comparison_text += "🎯 **RECOMMENDATION**\n"
    best_value = min(products, key=lambda x: x['price'])
    best_features = max(products, key=lambda x: len(x['features']) if x['features'] else 0)
    
    if best_value == best_features:
        comparison_text += f"🏆 **Best Overall Choice**: {best_value['p_name']}\n"
        comparison_text += f"   Perfect balance of price and features!\n"
    else:
        comparison_text += f"💰 **Best Value**: {best_value['p_name']} (₹{best_value['price']})\n"
        comparison_text += f"⚡ **Best Features**: {best_features['p_name']}\n"
        comparison_text += "   Choose based on your priorities - budget vs features!\n"
    
    comparison_text += "\nWould you like me to explain any specific aspect in more detail?"
    
    return comparison_text



@app.route('/api/share_invoice/<int:order_id>', methods=['GET'])
def api_share_invoice(order_id):
    """Generate WhatsApp invoice text for a past order"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Verify order belongs to user
        cursor.execute("SELECT order_id, total_amount FROM ORDERS WHERE order_id = %s AND user_id = %s", (order_id, user_id))
        order = cursor.fetchone()
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        # Get order items
        cursor.execute("""
            SELECT p.p_name, oi.quantity, oi.sum_amount
            FROM ORDER_ITEM oi
            JOIN PRODUCT p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cursor.fetchall()
        
        invoice_text = generate_whatsapp_invoice_text(order_id, items, float(order['total_amount']))
        return jsonify({'success': True, 'invoice_text': invoice_text}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/return_order', methods=['POST'])
def api_return_order():
    """Request a return for a delivered order"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    data = request.get_json()
    order_id = data.get('order_id')
    reason = data.get('reason', '')
    
    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Verify order belongs to user and is delivered
        cursor.execute("SELECT order_id, status FROM ORDERS WHERE order_id = %s AND user_id = %s", (order_id, user_id))
        order = cursor.fetchone()
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        if order['status'] != 'Delivered':
            return jsonify({'success': False, 'message': f'Only delivered orders can be returned. Current status: {order["status"]}'}), 400
        
        # Update order status to Return Requested and save reason
        cursor.execute("UPDATE ORDERS SET status = 'Return Requested', return_reason = %s WHERE order_id = %s", (reason, order_id))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Return request submitted successfully'}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Logout user"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200

@app.route('/api/user_profile', methods=['GET'])
def api_user_profile():
    """Get user profile information"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_id, username, email, address FROM USER WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if user:
            return jsonify({
                'success': True, 
                'user_id': user['user_id'], 
                'username': user['username'], 
                'email': user['email'],
                'address': user['address']
            }), 200
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/user_orders', methods=['GET'])
def api_user_orders():
    """Get user's orders"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""SELECT o.order_id, DATE_FORMAT(o.order_date, '%Y-%m-%d') as order_date, 
                                o.total_amount, o.status, GROUP_CONCAT(p.p_name SEPARATOR ', ') as product_names
                         FROM ORDERS o 
                         LEFT JOIN ORDER_ITEM oi ON o.order_id = oi.order_id
                         LEFT JOIN PRODUCT p ON oi.product_id = p.product_id
                         WHERE o.user_id = %s 
                         GROUP BY o.order_id
                         ORDER BY o.order_date DESC""", (user_id,))
        orders = cursor.fetchall()
        return jsonify({'success': True, 'orders': orders}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/add_review', methods=['POST'])
def api_add_review():
    """Add product review"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    product_id = data.get('product_id')
    rating = data.get('rating')
    comment = data.get('comment')
    
    # Validate rating
    if not (1 <= rating <= 5):
        return jsonify({'success': False, 'message': 'Rating must be between 1 and 5'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO REVIEW (rating, comment, review_date, user_id, product_id) VALUES (%s, %s, %s, %s, %s)",
                      (rating, comment, datetime.now().date(), user_id, product_id))
        conn.commit()
        return jsonify({'success': True, 'message': 'Review added successfully'}), 201
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/edit_product', methods=['POST'])
def api_edit_product():
    """Edit product details (Admin)"""
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    data = request.get_json()
    product_id = data.get('product_id')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("""UPDATE PRODUCT SET p_name = %s, price = %s, discount = %s, stock = %s, features = %s, warranty = %s 
                         WHERE product_id = %s""",
                      (data.get('p_name'), data.get('price'), data.get('discount', 0), data.get('stock'), 
                       data.get('features'), data.get('warranty'), product_id))
        conn.commit()
        return jsonify({'success': True, 'message': 'Product updated successfully'}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/delete_product', methods=['POST'])
def api_delete_product():
    """Delete product (Admin)"""
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    data = request.get_json()
    product_id = data.get('product_id')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = conn.cursor()
    try:
        # Delete from related tables first to avoid foreign key conflicts
        cursor.execute("DELETE FROM CART WHERE product_id = %s", (product_id,))
        cursor.execute("DELETE FROM ORDER_ITEM WHERE product_id = %s", (product_id,))
        cursor.execute("DELETE FROM REVIEW WHERE product_id = %s", (product_id,))
        # Now delete the product
        cursor.execute("DELETE FROM PRODUCT WHERE product_id = %s", (product_id,))
        conn.commit()
        return jsonify({'success': True, 'message': 'Product deleted successfully'}), 200
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()



if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
