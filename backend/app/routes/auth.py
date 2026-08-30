from flask import Blueprint, request, jsonify
from app.extensions import db, bcrypt
from email_validator import validate_email, EmailNotValidError
from app.models.user import User
from app.models.portfolio import Portfolio, AccountType
from app.models.holding import Holding
from app.models.transaction import Transaction, TransactionType
from flask_jwt_extended import create_access_token, get_jwt_identity, create_refresh_token, jwt_required, get_jwt
from app.models.token_blocklist import TokenBlocklist
from app.services.pricing import PriceService
from decimal import Decimal
import random

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    # request registration data
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
         return jsonify({'message': 'invalid data'}), 400
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
    try: validate_email(email,check_deliverability=False)
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

def reset_demo_user_data(user):
    if not user:
        return

    for portfolio in list(user.portfolios):
        for holding in list(portfolio.holdings):
            for transaction in list(holding.transactions):
                db.session.delete(transaction)
            db.session.delete(holding)
        db.session.delete(portfolio)

    db.session.commit()


def seed_demo_portfolio(user):
    portfolio = Portfolio(
        name='Demo Portfolio',
        account_type=AccountType.taxable,
        user_id=user.id,
    )
    db.session.add(portfolio)
    db.session.flush()

    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'JPM', 'V']
    selected_symbols = random.sample(symbols, 5)

    for symbol in selected_symbols:
        market_price = PriceService.read_price(symbol)
        if market_price is None:
            continue

        discount = Decimal(str(random.uniform(0.05, 0.15)))
        trade_price = Decimal(str(market_price)) * (Decimal('1') - discount)
        shares = Decimal(str(random.randint(1, 10)))

        holding = Holding(
            portfolio_id=portfolio.id,
            symbol=symbol,
            shares=shares,
            avg_cost_basis=trade_price,
        )
        db.session.add(holding)
        db.session.flush()

        transaction = Transaction(
            holding_id=holding.id,
            transaction_type=TransactionType.BUY,
            shares=shares,
            price=trade_price,
        )
        db.session.add(transaction)

    db.session.commit()
    return portfolio


@auth_bp.route('/demo-login', methods=['POST'])
def demo_login():
    data = request.get_json(silent=True) or {}
    username = data.get('username') or 'Demo_User'
    password = data.get('password') or 'Password123'

    if username != 'Demo_User' or password != 'Password123':
        return jsonify({'Error': 'username or password is incorrect'}), 401

    user = User.query.filter_by(username=username).first()
    if not user:
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email='demo@gmail.com', hashed_passwd=password_hash)
        db.session.add(user)
        db.session.commit()

    reset_demo_user_data(user)
    seed_demo_portfolio(user)

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200


@auth_bp.route('/login', methods=['POST'])
def login():
   data = request.get_json(silent=True)
   if not isinstance(data, dict):
            return jsonify({'message': 'invalid data'}), 400
   username = data.get('username')
   password = data.get('password')
   if not username or not password:
        return jsonify({'Error':'username or password missing'}),400
   
   user = User.query.filter_by(username=username).first()

   if not user or not bcrypt.check_password_hash(user.hashed_passwd,password):
        return jsonify({'Error':'username or password is incorrect'}),401
   access_token = create_access_token(identity=str(user.id))
   refresh_token = create_refresh_token(identity=str(user.id))
   return jsonify({'access_token':access_token,'refresh_token':refresh_token}),200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity=get_jwt_identity()
    access_token=create_access_token(identity=identity)
    return jsonify({'access_token':access_token}),200

@auth_bp.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
     jti=get_jwt()['jti']
     db.session.add(TokenBlocklist(jti=jti))
     db.session.commit()
     return jsonify({'message':'jwt revoked'}),200