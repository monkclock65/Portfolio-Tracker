from app.models.transaction import Transaction,TransactionType
from app.models.holding import Holding
from app.models.portfolio import Portfolio
from flask import Blueprint,request, jsonify
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from decimal import Decimal, InvalidOperation
from app.services.pricing import PriceService

transaction_bp = Blueprint('transaction',__name__,url_prefix='/transaction')

def get_owned_portfolio(portfolio_id):
    identity = get_jwt_identity()
    portfolio_row = db.session.query(Portfolio).filter_by(user_id=identity,id=portfolio_id).first()
    if not portfolio_row:
        return None
    return portfolio_row
def get_avg_cost_basis(price,shares,portfolio_id,symbol,transaction_type):
    holding = db.session.query(Holding).filter_by(symbol=symbol,portfolio_id=portfolio_id).first()
    if holding:
        holding_id = holding.id
        transactions = db.session.query(Transaction).filter_by(holding_id=holding_id).all()
        total_amount = Decimal('0')
        shares_count = Decimal('0')
        for transaction in transactions:
            transaction_amount = transaction.price * transaction.shares
            if transaction.transaction_type == TransactionType.BUY:
                shares_count = transaction.shares + shares_count
                total_amount = transaction_amount + total_amount
            if transaction.transaction_type == TransactionType.SELL:
                shares_sold = transaction.shares
                avg_cost = total_amount / shares_count if shares_count else Decimal('0')
                total_amount = total_amount - (shares_sold * avg_cost)
                shares_count = shares_count - shares_sold
        if transaction_type == TransactionType.BUY:
            new_transaction_total = price * shares
            holding_total = total_amount + new_transaction_total
            total_holding_shares = shares_count + shares
            avg_cost_basis = holding_total/total_holding_shares if total_holding_shares else Decimal('0')
            return avg_cost_basis
        if transaction_type == TransactionType.SELL:
            avg_cost_basis = total_amount / shares_count if shares_count else Decimal('0')
            return avg_cost_basis
    else:
        new_transaction_total = price * shares
        holding_total_shares = shares
        avg_cost_basis = new_transaction_total/holding_total_shares if holding_total_shares else Decimal('0')
        return avg_cost_basis
    


@transaction_bp.route('/add_transaction/<uuid:portfolio_id>',methods=['POST'])
@jwt_required()
def insert(portfolio_id):
    portfolio = get_owned_portfolio(portfolio_id)
    if portfolio is None:
        return jsonify({'message': 'portfolio not found'}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'message': 'invalid request body'}), 400

    symbol = str(data.get('symbol') or '').strip().upper()
    if not symbol:
        return jsonify({'message': 'symbol is required'}), 400

    raw_type = data.get('transaction_type')
    try:
        transaction_type = TransactionType(raw_type)
    except ValueError:
        return jsonify({'message': 'invalid transaction_type'}), 400

    try:
        shares = Decimal(str(data.get('shares')))
    except (InvalidOperation, TypeError, ValueError):
        return jsonify({'message': 'shares must be a positive number'}), 400

    if shares <= 0:
        return jsonify({'message': 'shares must be greater than zero'}), 400

    holding = db.session.query(Holding).filter_by(symbol=symbol,portfolio_id=portfolio_id).first()
    provided_price = data.get('price')

    if transaction_type == TransactionType.SELL:
        if holding is None:
            return jsonify({'message': 'no holding with shares found'}), 404
        if holding.shares < shares:
            return jsonify({'message': 'sell amount exceeds available shares'}), 400

        if provided_price is not None:
            try:
                price = Decimal(str(provided_price))
            except (InvalidOperation, TypeError, ValueError):
                return jsonify({'message': 'price must be a valid number'}), 400
        else:
            try:
                price_data = PriceService.get_price(symbol)
                if price_data is None:
                    return jsonify({'message': f'could not fetch current price for {symbol}'}), 400
                price = Decimal(str(price_data['current_price']))
            except Exception as e:
                return jsonify({'message': f'error fetching price: {str(e)}'}), 500
    else:
        price = provided_price
        if price is None:
            return jsonify({'message': 'price is required for BUY transactions'}), 400
        try:
            price = Decimal(str(price))
        except (InvalidOperation, TypeError, ValueError):
            return jsonify({'message': 'price must be a valid number'}), 400
        if price <= 0:
            return jsonify({'message': 'price must be greater than zero'}), 400

    if holding is not None:
        holding_id = holding.id
        avg_cost_basis = get_avg_cost_basis(price,shares,portfolio_id,symbol,transaction_type)
        transaction = Transaction(holding_id=holding_id,transaction_type=transaction_type,shares=shares,price=price)
        holding.avg_cost_basis = avg_cost_basis
        if transaction.transaction_type == TransactionType.BUY:
            holding.shares = holding.shares + shares
        if transaction.transaction_type == TransactionType.SELL:
            holding.shares = holding.shares - shares
        db.session.add(holding)
        db.session.add(transaction)
        db.session.commit()
        return jsonify({
            'message': 'transaction added',
            'symbol': symbol,
            'holding_id': str(holding_id),
            'id': str(transaction.id),
        }), 201

    avg_cost_basis = get_avg_cost_basis(price,shares,portfolio_id,symbol,transaction_type)
    holding = Holding(portfolio_id=portfolio_id,symbol=symbol,shares=shares,avg_cost_basis=avg_cost_basis)
    db.session.add(holding)
    db.session.commit()
    holding_id = holding.id
    transaction = Transaction(holding_id=holding_id,transaction_type=transaction_type,shares=shares,price=price)
    db.session.add(transaction)
    db.session.commit()
    return jsonify({
        'message': 'transaction added',
        'symbol': symbol,
        'holding_id': str(holding_id),
        'id': str(transaction.id),
    }), 201
    
    
@transaction_bp.route('/read_all_transactions/<uuid:portfolio_id>', methods=['GET'])      
@jwt_required()
def read_all(portfolio_id):
    portfolio = get_owned_portfolio(portfolio_id)
    if portfolio is None:
        return jsonify ({'message': 'portfolio not found'}), 404
    transaction_list = []
    holdings = db.session.query(Holding).filter_by(portfolio_id=portfolio_id).all()
    for holding in holdings:
        symbol = holding.symbol
        holding_id=holding.id
        transactions = db.session.query(Transaction).filter_by(holding_id=holding_id).order_by(Transaction.transacted_at).all()
        for transaction in transactions:
            transaction_type = transaction.transaction_type.value
            shares = transaction.shares
            price = transaction.price
            id = transaction.id
            transaction_dict = {
                'symbol': symbol,
                'type'  : transaction_type,
                'shares': str(shares),
                'price': str(price),
                'id':    str(id)
                }
            transaction_list.append(transaction_dict)
    return jsonify({'transactions': transaction_list}), 200