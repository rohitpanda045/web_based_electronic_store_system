# TechMart - Online Electronics Store

A complete full-stack e-commerce application built with Flask (Backend), HTML/CSS/JavaScript (Frontend), and MySQL (Database).

## Project Structure

```
online_store/
├── app.py                 # Main Flask application
├── setup_db.py           # Database setup script
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── index.html
│   ├── registration.html
│   ├── login.html
│   ├── products.html
│   ├── cart.html
│   ├── admin_login.html
│   └── admin.html
└── static/
    ├── css/
    │   └── style.css     # Main stylesheet
    ├── js/
    │   ├── common.js
    │   ├── registration.js
    │   ├── login.js
    │   ├── products.js
    │   ├── cart.js
    │   ├── admin_login.js
    │   └── admin.js
    └── images/           # Product images
```

## Features

### User Features
- **Registration & Login**: Create account and securely login
- **Product Browsing**: View all available products with details
- **Shopping Cart**: Add products to cart and manage quantities
- **Order Placement**: Buy products directly or checkout from cart
- **Chatbot Support**: 24/7 automated customer support

### Admin Features
- **Admin Login**: Secure admin access
- **Product Management**: Add new products to catalog
- **Order Management**: View all orders with detailed information
- **Order Details**: Check individual order items and amounts

## Database Schema

### Tables
1. **ADMIN** - Admin accounts
2. **USER** - Customer accounts
3. **PRODUCT** - Product catalog
4. **REVIEW** - Customer reviews
5. **ORDER** - Customer orders
6. **ORDER_ITEM** - Items in each order
7. **CART** - Shopping cart items

## Installation & Setup

### Prerequisites
- Python 3.7+
- MySQL Server
- Git (optional)

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Create Database

First, ensure MySQL is running and accessible with:
- **Host**: localhost
- **User**: root
- **Password**: rohit

Then run the database setup script:

```bash
python setup_db.py
```

This will create:
- Database: `online_store`
- All required tables
- Sample admin account (ID: 1, Username: admin, Password: admin123)
- Sample products

### Step 3: Run the Flask Application

```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## Default Credentials

### Admin
- **Admin ID**: 1
- **Username**: admin
- **Password**: admin123

### Sample User (Optional - Create via registration)
- Create your own account using the registration page

## Usage

### For Users
1. Go to http://localhost:5000
2. Register a new account or login
3. Browse products
4. Add items to cart or buy directly
5. Checkout and place order

### For Admins
1. Go to http://localhost:5000/admin_login
2. Login with admin credentials
3. Add new products
4. View and manage customer orders

## Pages Overview

| Page | URL | Purpose |
|------|-----|---------|
| Home | / | Welcome page with store info |
| Registration | /registration | Create new user account |
| Login | /login | User login |
| Products | /products | Browse and buy products |
| Cart | /cart | Manage shopping cart |
| Admin Login | /admin_login | Admin authentication |
| Admin Panel | /admin | Manage products and orders |

## API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - User login
- `POST /api/admin_login` - Admin login
- `POST /api/logout` - Logout user

### Products
- `GET /api/products` - Get all products

### Cart
- `POST /api/add_to_cart` - Add product to cart
- `GET /api/get_cart` - Get user's cart
- `POST /api/remove_from_cart` - Remove from cart
- `POST /api/checkout` - Place order from cart

### Orders
- `POST /api/buy_now` - Place order directly
- `GET /api/get_all_orders` - Get all orders (Admin)
- `GET /api/get_order_details/<order_id>` - Get order details (Admin)

### Admin
- `POST /api/add_product` - Add new product (Admin)

### Chatbot
- `POST /api/chatbot` - Get chatbot response

## Design

- **Theme**: Dark Blue & Dark Green with gold accents
- **Responsive**: Works on desktop, tablet, and mobile
- **Animations**: Smooth transitions and hover effects

## Troubleshooting

### Database Connection Error
- Ensure MySQL is running
- Verify credentials in `app.py` match your MySQL setup
- Run `setup_db.py` to create database

### Port Already in Use
- Change port in `app.py`: `app.run(port=5001)`
- Or kill the process using port 5000

### CORS Issues
- The application is single-domain, no CORS issues expected

## Future Enhancements
- Payment gateway integration
- Email notifications
- Advanced product filtering
- User reviews and ratings
- Wishlist feature
- Order tracking

## Support

For issues or questions, use the in-app chatbot feature or contact support.

---

**Created**: January 27, 2026
**Version**: 1.0

