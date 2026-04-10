import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Database connection configuration
db_config = {
    'host': os.getenv('DB_HOST', 'switchyard.proxy.rlwy.net'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'uxnLFmmHCnLVblKklWKEGxJFrcgqxUcu'),
    'database': os.getenv('DB_NAME', 'railway'),
    'port': int(os.getenv('DB_PORT', 26497))
}

def setup_database():
    conn = None
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            port=db_config['port']
        )
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        db_name = db_config['database']
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created or already exists.")
        
        # Use the database
        cursor.execute(f"USE {db_name}")
        
        # Create tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ADMIN (
            admin_id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(100) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
        """)
        print("ADMIN table created")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS USER (
            user_id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            address TEXT
        )
        """)
        print("USER table created")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS PRODUCT (
            product_id INT PRIMARY KEY AUTO_INCREMENT,
            p_name VARCHAR(150) NOT NULL UNIQUE,
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
        print("PRODUCT table created")
        
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
        print("ORDERS table created")
        
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
        print("ORDER_ITEM table created")
        
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
        print("CART table created")
        
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
        print("REVIEW table created")
        
        # Insert sample admin
        cursor.execute("INSERT IGNORE INTO ADMIN (admin_id, username, password) VALUES (1, 'rohit', '12345')")
        print("Sample admin inserted or already exists")
        
        # Clear existing data to ensure a clean, unique state
        cursor.execute("DELETE FROM PRODUCT")
        print("Existing product data cleared for fresh setup.")
        
        # Insert sample products
        sample_products = [
            ("iPhone 13 Pro", 81999.00, 10.00, 10, "https://images.unsplash.com/photo-1632661674596-df8be070a5c5?q=80&w=1000&auto=format&fit=crop", "6.1-inch display, A15 Bionic chip, 12MP camera", "2 years", "Smartphones", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=1000&auto=format&fit=crop"),
            ("Samsung Galaxy S21", 65599.00, 15.00, 15, "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?q=80&w=1000&auto=format&fit=crop", "6.2-inch display, Snapdragon 888, 64MP camera", "2 years", "Smartphones", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=1000&auto=format&fit=crop"),
            ("MacBook Pro M1", 106599.00, 5.00, 8, "https://images.pexels.com/photos/1229861/pexels-photo-1229861.jpeg", "13-inch display, M1 chip, 8GB RAM, 256GB SSD", "1 year", "Laptops", "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?q=80&w=1000&auto=format&fit=crop"),
            ("iPad Air", 49199.00, 0.00, 12, "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?q=80&w=1000&auto=format&fit=crop", "10.9-inch display, A14 Bionic, WiFi connectivity", "1 year", "Tablets", "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?q=80&w=1000&auto=format&fit=crop"),
            ("Sony WH-1000XM4", 28699.00, 20.00, 20, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=1000&auto=format&fit=crop", "Wireless headphones, Noise cancelling, 30hr battery", "2 years", "Accessories", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=1000&auto=format&fit=crop"),
        ]
        
        for product in sample_products:
            cursor.execute("""
            INSERT IGNORE INTO PRODUCT (p_name, price, discount, stock, image, features, warranty, category, category_image) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, product)
        print("Sample products inserted or already exists")
        
        conn.commit()
        print("\nDatabase setup completed successfully!")
        
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    setup_database()

