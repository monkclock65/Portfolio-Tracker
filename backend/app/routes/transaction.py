from app.models.transaction import Transaction,TransactionType
from app.models.holding import Holding
from app.models.portfolio import Portfolio
from flask import Blueprint,request, jsonify
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from decimal import Decimal

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
        total_amount = 0
        shares_count = 0
        for transaction in transactions:
            transaction_amount = transaction.price * transaction.shares
            if transaction.transaction_type == TransactionType.BUY:
                shares_count = transaction.shares + shares_count
                total_amount = transaction_amount + total_amount
            if transaction.transaction_type == TransactionType.SELL:
                shares_sold = transaction.shares
                avg_cost = total_amount/shares_count
                total_amount = total_amount - (shares_sold * avg_cost)
                shares_count = shares_count - shares_sold
        if transaction_type == TransactionType.BUY:
            new_transaction_total = price * shares
            holding_total = total_amount + new_transaction_total
            total_holding_shares = shares_count + shares
            avg_cost_basis = holding_total/total_holding_shares if total_holding_shares else 0
            return avg_cost_basis
        if transaction_type == TransactionType.SELL:
            avg_cost_basis = total_amount/shares_count
            return avg_cost_basis
    else: 
        new_transaction_total = price * shares
        holding_total_shares = shares
        avg_cost_basis = new_transaction_total/holding_total_shares
        return avg_cost_basis
    #can't sell shares if holding doesn't exist so no need to check for transaction type
    


@transaction_bp.route('/add_transaction/<uuid:portfolio_id>',methods=['POST'])
@jwt_required()
def insert(portfolio_id):
    portfolio = get_owned_portfolio(portfolio_id)
    if portfolio is None:
        return jsonify({'message': 'portfolio not found'}), 404
    data = request.get_json()
    symbol = data.get('symbol')
    raw_type = data.get('transaction_type')
    try:
        transaction_type = TransactionType(raw_type)
    except ValueError:
        return jsonify({'message': 'invalid transaction_type'}), 400
    shares = data.get('shares')
    price = data.get('price')
    price = Decimal(str(price))
    shares = Decimal(str(shares))

    holding = db.session.query(Holding).filter_by(symbol=symbol,portfolio_id=portfolio_id).first()
    if holding:
        holding_id = holding.id
        avg_cost_basis = get_avg_cost_basis(price,shares,portfolio_id,symbol,transaction_type)
        transaction = Transaction(holding_id=holding_id,transaction_type=transaction_type,shares=shares,price=price)
        holding.avg_cost_basis = avg_cost_basis
        if transaction.transaction_type == TransactionType.BUY:
            holding.shares = holding.shares + shares
        if transaction.transaction_type == TransactionType.SELL:
            holding.shares = holding.shares - shares
            if holding.shares < 0:
                return jsonify({'message':'shares amount cannot be set below zero'}), 400
        db.session.add(transaction)
        db.session.commit()
        return jsonify({'message':'transaction added','holding id': str(holding_id)}), 201
    else:
        if transaction_type == TransactionType.SELL:
            return jsonify({'message':'no holding with shares found'}),404
        avg_cost_basis = get_avg_cost_basis(price,shares,portfolio_id,symbol,transaction_type)
        holding = Holding(portfolio_id=portfolio_id,symbol=symbol,shares=shares,avg_cost_basis=avg_cost_basis)
        db.session.add(holding)
        db.session.commit()
        holding_id = holding.id
        transaction = Transaction(holding_id=holding_id,transaction_type=transaction_type,shares=shares,price=price)
        db.session.add(transaction)
        db.session.commit()
        return jsonify({'message':'transaction added','holding id': str(holding_id)}), 201
    
    
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