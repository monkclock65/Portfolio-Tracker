from app.models.transaction import Transaction,TransactionType
from app.models.holding import Holding
from app.models.portfolio import PORTFOLIO
from flask import Blueprint,request, jsonify
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from decimal import Decimal

transaction_bp = Blueprint('transaction',__name__,url_prefix='/transaction')

def get_owned_portfolio(portfolio_id):
    identity = get_jwt_identity()
    portfolio_row = db.session.query(PORTFOLIO).filter_by(user_id=identity,id=portfolio_id).first()
    if not portfolio_row:
        return None
    return portfolio_row
def get_avg_cost_basis(price,shares,portfolio_id,symbol):
    holding = db.session.query(Holding).filter_by(symbol=symbol,portfolio_id=portfolio_id).first()
    if holding:
        holding_shares = holding.shares
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

        new_transaction_total = price * shares
        holding_total = total_amount + new_transaction_total
        total_holding_shares = holding_shares + shares
        avg_cost_basis = holding_total/total_holding_shares
        return avg_cost_basis
    else: 
        new_transaction_total = price * shares
        holding_total_shares = shares
        avg_cost_basis = new_transaction_total/holding_total_shares
        return avg_cost_basis
    
    


@transaction_bp.route('/add_transaction/<uuid:portfolio_id>',methods=['POST'])
@jwt_required()
def insert(portfolio_id):
    portfolio = get_owned_portfolio(portfolio_id)
    if portfolio is None:
        return jsonify({'message': 'portfolio not found'}), 404
    data = request.get_json()
    symbol = data.get('symbol')
    transaction_type = data.get('transaction_type')
    shares = data.get('shares')
    price = data.get('price')
    price = Decimal(str(price))
    shares = Decimal(str(shares))

    holding = db.session.query(Holding).filter_by(symbol=symbol,portfolio_id=portfolio_id).first()
    if holding:
        holding_id = holding.id
        avg_cost_basis = get_avg_cost_basis(price,shares,portfolio_id,symbol)
        transaction = Transaction(holding_id=holding_id,avg_cost_basis=avg_cost_basis,transaction_type=transaction_type,shares=shares,price=price)
        holding.avg_cost_basis = avg_cost_basis
        holding.shares = holding.shares + shares
        db.session.add(transaction)
        db.session.commit()
    else:
        avg_cost_basis = get_avg_cost_basis(price,shares,portfolio_id,symbol)
        holding = Holding(symbol=symbol,shares=shares,avg_cost_basis=avg_cost_basis)
        db.session.add(holding)
        db.session.commit()
        holding_id = holding.id
        transaction = Transaction(holding_id=holding_id,avg_cost_basis=avg_cost_basis,transaction_type=transaction_type,shares=shares,price=price)
        db.session.add(transaction)
        db.session.commit()
    
    
       