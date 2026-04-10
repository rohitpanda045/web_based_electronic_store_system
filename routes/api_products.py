from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Product

products_bp = Blueprint('products', __name__)

CATEGORY_PLACEHOLDER_PREFIX = 'cat_placeholder_'

@products_bp.route('/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    try:
        query = Product.query.filter(Product.p_name.notlike(f"{CATEGORY_PLACEHOLDER_PREFIX}%"))
        if category:
            query = query.filter_by(category=category)
            
        products = query.all()
        # Ensure exact keys needed by frontend
        result = [
            {
                'product_id': p.product_id, 'p_name': p.p_name, 'price': float(p.price), 
                'discount': float(p.discount) if p.discount else 0.0, 'stock': p.stock, 
                'image': p.image, 'features': p.features, 'warranty': p.warranty, 
                'category': p.category, 'category_image': p.category_image
            } for p in products
        ]
        return jsonify({'success': True, 'products': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@products_bp.route('/categories_with_count', methods=['GET'])
def categories_with_count():
    from sqlalchemy import func, case
    try:
        # Group by category
        query = db.session.query(
            Product.category,
            func.sum(case((Product.p_name.notlike(f"{CATEGORY_PLACEHOLDER_PREFIX}%"), 1), else_=0)).label('product_count'),
            func.max(Product.category_image).label('category_image')
        ).group_by(Product.category).order_by(Product.category).all()
        
        categories = []
        for row in query:
            categories.append({
                'category': row.category,
                'product_count': int(row.product_count) if row.product_count else 0,
                'category_image': row.category_image if row.category_image else '20260128190942_s25_ultra.jpg'
            })
        return jsonify({'success': True, 'categories': categories}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@products_bp.route('/categories', methods=['GET'])
def categories():
    try:
        query = db.session.query(Product.category).distinct().order_by(Product.category).all()
        categories_list = [row[0] for row in query if row[0]]
        return jsonify({'success': True, 'categories': categories_list}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
