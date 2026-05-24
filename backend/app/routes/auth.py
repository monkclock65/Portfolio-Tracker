from flask import Blueprint, request, jsonify
from app.extensions import db, bcrypt
from email_validator import validate_email, EmailNotValidError
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    # request registration data
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    #check for required fields
    if not username or not email or not password:
            return jsonify({
                'Error': 'Missing username, email, or password'
            }), 400
    
    #check if user exists
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({
            'Error': 'Username or email already exists'
        }), 400
    
    #check password security
    if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
        return jsonify({
            'Error': 'Password must be at least 8 characters long and contain both letters and numbers'
        }), 400
    
    #check for valid email
    try: validate_email(email)
    except EmailNotValidError: return jsonify({
        'Error': 'Invalid email format'}), 400
    
    #hash password
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    #insert user into database
    user = User(username=username, email=email, hashed_passwd=password_hash)
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'message': 'User registered successfully'
    }), 201