from app.models.transaction import Transaction,TransactionType
from app.models.holding import Holding
from app.models.portfolio import PORTFOLIO
from flask import Blueprint,request, jsonify
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

transaction_bp = Blueprint('transaction',__name__,url_prefix='/transaction')

def get_owned_portfolio(portfolio_id):
    identity = get_jwt_identity()
    portfolio_row = db.session.query(PORTFOLIO).filter_by(user_id=identity,id=portfolio_id).first()
    if not portfolio_row:
        return None
    return portfolio_row
def get_avg_cost_basis(price,shares,portfolio_id):
    #write this after finishing other logic stuff

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
    holding = db.session.query(Holding).filter_by(symbol=symbol,portfolio_id=portfolio_id).first()
    holding_id = holding.id
    if holding:
        avg_cost_basis = get_avg_cost_basis(price,shares,portfolio_id)
        transaction = Transaction(holding_id=holding_id,avg_cost_basis=avg_cost_basis,transaction_type=transaction_type,shares=shares,price=price)
        db.session.add(transaction)
        db.session.commit()
    else:
        # make create holding function and call it here
        avg_cost_basis = get_avg_cost_basis(price,shares,portfolio_id)
    
       