from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, Admin
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

# Failed login attempt tracking (in memory)
failed_logins = {} # {user_id: {'count': N, 'lock_until': datetime}}
MAX_FAILED_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 30

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user_id = data.get('user_id')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    address = data.get('address')
    
    try:
        user = User.query.get(user_id)
        if user:
            return jsonify({'success': False, 'message': 'User ID already exists'}), 400
            
        hashed_password = generate_password_hash(password)
        new_user = User(
            user_id=user_id,
            username=username,
            email=email,
            password=hashed_password,
            address=address
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Registration successful'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('user_id')
    password = data.get('password')
    
    try:
        if user_id in failed_logins:
            lock_info = failed_logins[user_id]
            if lock_info['count'] >= MAX_FAILED_ATTEMPTS:
                if datetime.now() < lock_info['lock_until']:
                    return jsonify({'success': False, 'message': f'Account locked due to multiple failed attempts. Try again after {lock_info["lock_until"].strftime("%H:%M:%S")}'}), 403
                else:
                    del failed_logins[user_id]

        user = User.query.get(user_id)
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            if user_id in failed_logins:
                del failed_logins[user_id]
            return jsonify({'success': True, 'message': 'Login successful'}), 200
        else:
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
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/admin_login', methods=['POST'])
def admin_login():
    data = request.get_json()
    admin_id = data.get('admin_id')
    password = data.get('password')
    
    try:
        admin = Admin.query.get(admin_id)
        if admin and admin.password == password:
            session['admin_id'] = admin.admin_id
            return jsonify({'success': True, 'message': 'Login successful'}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid admin ID or password'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200

@auth_bp.route('/user_profile', methods=['GET'])
def user_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    user_id = session['user_id']
    try:
        user = User.query.get(user_id)
        if user:
            return jsonify({
                'success': True, 
                'user_id': user.user_id, 
                'username': user.username, 
                'email': user.email,
                'address': user.address
            }), 200
        return jsonify({'success': False, 'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
