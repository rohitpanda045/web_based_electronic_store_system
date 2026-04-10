from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Product, Order, User, OrderItem
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

CATEGORY_PLACEHOLDER_PREFIX = 'cat_placeholder_'

def admin_required(f):
    def wrap(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@admin_bp.route('/admin/analytics', methods=['GET'])
@admin_required
def analytics():
    try:
        total_sales = db.session.query(func.sum(Order.total_amount)).filter(Order.status == 'Delivered').scalar() or 0.00
        total_orders = db.session.query(func.count(Order.order_id)).scalar()
        total_users = db.session.query(func.count(User.user_id)).scalar()
        
        return jsonify({
            'success': True,
            'total_sales': float(total_sales),
            'total_orders': total_orders,
            'total_users': total_users
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/get_all_orders', methods=['GET'])
@admin_required
def get_all_orders():
    try:
        orders = Order.query.order_by(Order.order_date.desc()).all()
        result = []
        for o in orders:
            product_names = ", ".join([item.product.p_name for item in o.items])
            result.append({
                'order_id': o.order_id,
                'user_id': o.user_id,
                'username': o.user.username,
                'order_date': o.order_date.strftime('%Y-%m-%d'),
                'total_amount': float(o.total_amount),
                'status': o.status,
                'return_reason': o.return_reason,
                'product_names': product_names
            })
        return jsonify({'success': True, 'orders': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/update_order_status', methods=['POST'])
@admin_required
def update_order_status():
    data = request.get_json()
    order_id = data.get('order_id')
    status = data.get('status')
    valid_statuses = ['Pending', 'Shipped', 'On the way', 'Out for delivery', 'Delivered', 'Return Requested', 'Returned']
    
    if status not in valid_statuses:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
        
    try:
        order = Order.query.get(order_id)
        if order:
            order.status = status
            db.session.commit()
            return jsonify({'success': True, 'message': f'Order marked as {status}'}), 200
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/get_all_users', methods=['GET'])
@admin_required
def get_all_users():
    try:
        users = User.query.all()
        result = [{'user_id': u.user_id, 'username': u.username, 'email': u.email} for u in users]
        return jsonify({'success': True, 'users': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/add_product', methods=['POST'])
@admin_required
def add_product():
    data = request.get_json()
    required_fields = ['p_name', 'price', 'stock', 'image', 'features', 'warranty', 'category']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'{field} is required'}), 400
            
    p_name = str(data.get('p_name', '')).strip()
    if p_name.startswith(CATEGORY_PLACEHOLDER_PREFIX):
        return jsonify({'success': False, 'message': 'Reserved prefix name error'}), 400
        
    try:
        product = Product(
            p_name=p_name,
            price=data.get('price'),
            discount=data.get('discount', 0),
            stock=data.get('stock'),
            image=data.get('image'),
            features=data.get('features'),
            warranty=data.get('warranty'),
            category=data.get('category')
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Product added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/edit_product', methods=['POST'])
@admin_required
def edit_product():
    data = request.get_json()
    try:
        product = Product.query.get(data.get('product_id'))
        if product:
            product.p_name = data.get('p_name')
            product.price = data.get('price')
            product.discount = data.get('discount', 0)
            product.stock = data.get('stock')
            product.features = data.get('features')
            product.warranty = data.get('warranty')
            db.session.commit()
            return jsonify({'success': True, 'message': 'Product updated successfully'}), 200
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/delete_product', methods=['POST'])
@admin_required
def delete_product():
    try:
        product = Product.query.get(request.get_json().get('product_id'))
        if product:
            db.session.delete(product)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Product deleted successfully'}), 200
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/add_category', methods=['POST'])
@admin_required
def add_category():
    data = request.get_json()
    category_name = data.get('category', '').strip()
    category_image = data.get('category_image', '').strip()
    
    if not category_name:
        return jsonify({'success': False, 'message': 'Category name is required'}), 400
        
    try:
        exists = Product.query.filter_by(category=category_name).first()
        if exists:
            return jsonify({'success': False, 'message': 'Category already exists'}), 400
            
        placeholder = Product(
            p_name=f"{CATEGORY_PLACEHOLDER_PREFIX}{category_name}",
            price=0.00, discount=0.00, stock=0,
            image="", features="", warranty="",
            category=category_name, category_image=category_image
        )
        db.session.add(placeholder)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Category added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/delete_category', methods=['POST'])
@admin_required
def delete_category():
    data = request.get_json()
    category_name = data.get('category', '').strip()
    if not category_name:
        return jsonify({'success': False, 'message': 'Category name is required'}), 400
        
    try:
        # Delete placeholders
        Product.query.filter(Product.category == category_name, Product.p_name.like(f"{CATEGORY_PLACEHOLDER_PREFIX}%")).delete(synchronize_session=False)
        # Move remaining
        products = Product.query.filter_by(category=category_name).all()
        for p in products:
            p.category = 'Uncategorized'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Category deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
