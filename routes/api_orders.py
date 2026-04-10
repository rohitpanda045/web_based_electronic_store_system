from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Product, Cart, Order, OrderItem, Review
from datetime import datetime
import json

orders_bp = Blueprint('orders', __name__)

def generate_whatsapp_invoice_text(order_id, items, total_amount):
    """Generate a formatted invoice text for WhatsApp"""
    text = f"🏪 *TechMart Invoice*\\nOrder ID: #{order_id}\\n\\n*Items:*\\n"
    for item in items:
        text += f"• {item['p_name']} (x{item['quantity']}): ₹{item['sum_amount']:.2f}\\n"
    text += f"\\n*Total Amount:* ₹{total_amount:.2f}\\n"
    text += "\\nThank you for shopping with us!"
    return text

@orders_bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
            
        if product.stock < quantity:
            return jsonify({'success': False, 'message': f'Only {product.stock} items available in stock'}), 400
            
        existing_cart = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
        
        price = float(product.price)
        discount = float(product.discount) if product.discount else 0.0
        discounted_price = price - (price * discount / 100)
        
        if existing_cart:
            new_quantity = existing_cart.quantity + quantity
            if product.stock < new_quantity:
                return jsonify({'success': False, 'message': f'Cannot add more items. Total exceeds available stock.'}), 400
            
            existing_cart.quantity = new_quantity
            existing_cart.amount = discounted_price * new_quantity
        else:
            new_amount = discounted_price * quantity
            new_cart = Cart(user_id=user_id, product_id=product_id, quantity=quantity, amount=new_amount)
            db.session.add(new_cart)
            
        db.session.commit()
        return jsonify({'success': True, 'message': 'Product added to cart'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@orders_bp.route('/get_cart', methods=['GET'])
def get_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    try:
        user_id = session['user_id']
        cart_items = Cart.query.filter_by(user_id=user_id).join(Product).all()
        
        result = []
        for c in cart_items:
            product = Product.query.get(c.product_id)
            price = float(product.price)
            discount = float(product.discount) if product.discount else 0.0
            discounted_price = price - (price * discount / 100)
            
            result.append({
                'product_id': c.product_id,
                'p_name': product.p_name,
                'price': price,
                'discount': discount,
                'quantity': c.quantity,
                'amount': float(c.amount),
                'image': product.image,
                'discounted_price': discounted_price
            })
            
        return jsonify({'success': True, 'cart': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@orders_bp.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    data = request.get_json()
    try:
        cart_item = Cart.query.filter_by(user_id=session['user_id'], product_id=data.get('product_id')).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
        return jsonify({'success': True, 'message': 'Product removed from cart'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@orders_bp.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
        
    user_id = session['user_id']
    try:
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        if not cart_items:
            return jsonify({'success': False, 'message': 'Cart is empty'}), 400
            
        total_amount = 0
        order_items_details = []
        updated_cart_items = []
        
        for item in cart_items:
            product = Product.query.get(item.product_id)
            if not product or product.stock < item.quantity:
                db.session.rollback()
                return jsonify({'success': False, 'message': f'Insufficient stock for {product.p_name if product else "Product"}.'}), 400
            
            price = float(product.price)
            discount = float(product.discount) if product.discount else 0.0
            discounted_price = price - (price * discount / 100)
            item_total = discounted_price * item.quantity
            
            total_amount += item_total
            updated_cart_items.append((product, item.quantity, item_total))
            order_items_details.append({'p_name': product.p_name, 'quantity': item.quantity, 'sum_amount': item_total})
            
        # Create order
        new_order = Order(user_id=user_id, order_date=datetime.now().date(), total_amount=total_amount)
        db.session.add(new_order)
        db.session.flush() # Get order_id
        
        # Deduct stock and create order items
        for product, quantity, amount in updated_cart_items:
            product.stock -= quantity
            order_item = OrderItem(order_id=new_order.order_id, product_id=product.product_id, quantity=quantity, sum_amount=amount)
            db.session.add(order_item)
            
        # Clear Cart
        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        invoice_text = generate_whatsapp_invoice_text(new_order.order_id, order_items_details, total_amount)
        return jsonify({'success': True, 'message': 'Order placed successfully', 'order_id': new_order.order_id, 'invoice_text': invoice_text}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@orders_bp.route('/buy_now', methods=['POST'])
def buy_now():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    user_id = session['user_id']
    
    try:
        product = Product.query.get(product_id)
        if not product or product.stock < quantity:
            return jsonify({'success': False, 'message': 'Insufficient stock.'}), 400
            
        price = float(product.price)
        discount = float(product.discount) if product.discount else 0.0
        discounted_price = price - (price * discount / 100)
        total_amount = discounted_price * quantity
        
        new_order = Order(user_id=user_id, order_date=datetime.now().date(), total_amount=total_amount)
        db.session.add(new_order)
        db.session.flush()
        
        product.stock -= quantity
        order_item = OrderItem(order_id=new_order.order_id, product_id=product_id, quantity=quantity, sum_amount=total_amount)
        db.session.add(order_item)
        db.session.commit()
        
        invoice_text = generate_whatsapp_invoice_text(new_order.order_id, [{'p_name': product.p_name, 'quantity': quantity, 'sum_amount': total_amount}], total_amount)
        return jsonify({'success': True, 'message': 'Order placed successfully', 'order_id': new_order.order_id, 'invoice_text': invoice_text}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@orders_bp.route('/user_orders', methods=['GET'])
def user_orders():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    try:
        user_id = session['user_id']
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.order_date.desc()).all()
        result = []
        for o in orders:
            product_names = ", ".join([item.product.p_name for item in o.items])
            result.append({
                'order_id': o.order_id,
                'order_date': o.order_date.strftime('%Y-%m-%d'),
                'total_amount': float(o.total_amount),
                'status': o.status,
                'product_names': product_names
            })
        return jsonify({'success': True, 'orders': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@orders_bp.route('/add_review', methods=['POST'])
def add_review():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    data = request.get_json()
    rating = int(data.get('rating'))
    if not (1 <= rating <= 5):
        return jsonify({'success': False, 'message': 'Rating must be between 1 and 5'}), 400
        
    try:
        new_review = Review(
            rating=rating,
            comment=data.get('comment'),
            review_date=datetime.now().date(),
            user_id=session['user_id'],
            product_id=data.get('product_id')
        )
        db.session.add(new_review)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Review added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
        
@orders_bp.route('/delivered_products', methods=['GET'])
def delivered_products():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    try:
        orders = Order.query.filter_by(user_id=session['user_id'], status='Delivered').order_by(Order.order_date.desc()).all()
        products = []
        for o in orders:
            for item in o.items:
                products.append({
                    'p_name': item.product.p_name,
                    'price': float(item.product.price),
                    'discount': float(item.product.discount) if item.product.discount else 0.0,
                    'quantity': item.quantity,
                    'sum_amount': float(item.sum_amount),
                    'order_date': o.order_date.strftime('%Y-%m-%d')
                })
        return jsonify({'success': True, 'products': products}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@orders_bp.route('/return_order', methods=['POST'])
def return_order():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    data = request.get_json()
    order_id = data.get('order_id')
    try:
        order = Order.query.filter_by(order_id=order_id, user_id=session['user_id']).first()
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        if order.status != 'Delivered':
            return jsonify({'success': False, 'message': 'Only delivered orders can be returned.'}), 400
            
        order.status = 'Return Requested'
        order.return_reason = data.get('reason', '')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Return request submitted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
