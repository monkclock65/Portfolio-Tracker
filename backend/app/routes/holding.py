from app.models.holding import Holding
from app.extensions import db
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.portfolio import Portfolio

holding_bp = Blueprint('holding',__name__,url_prefix='/holding')

@holding_bp.route('/create_holding', methods=['POST'])
@jwt_required()
def insert():
    data = request.get_json()
    identity = get_jwt_identity()
    #get portfolio id to check user owns portfolio
    portfolio_id = data.get('portfolio_id')
    if not portfolio_id:
        return jsonify({'message': 'missing portfolio_id'}), 400
    #check if user owns portfolio
    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id,user_id=identity).first()
    if not portfolio:
        return jsonify({'message':'portfolio not found'}), 404
    #temporary, will use transaction history to auto fill in holdings later
    symbol = data.get('symbol')
    shares = data.get('shares')
    avg_cost_basis = data.get('avg_cost_basis')
    if not symbol or not shares or not avg_cost_basis:
        return jsonify({'message':'missing required fields'}), 400
    holding = Holding(symbol=symbol,shares=shares,avg_cost_basis=avg_cost_basis,portfolio_id=portfolio_id)
    db.session.add(holding)
    db.session.commit()
    return jsonify({'message':'holding added successfully'}), 201

#no update since holding will be based on transaction 

@holding_bp.route('/<uuid:holding_id>',methods=['GET'])
@jwt_required()
def read(holding_id):
    identity = get_jwt_identity()
    holding = db.session.query(Holding).filter_by(id=holding_id).first()
    if not holding:
        return jsonify({'message':'holding not found'}), 404
    portfolio = db.session.query(Portfolio).filter_by(user_id=identity,id=holding.portfolio_id).first()
    if not portfolio:
        return jsonify({'message':'holding not found'}), 404
    return jsonify({
        'symbol': holding.symbol,
        'shares': str(holding.shares),
        'avg_cost_basis': str(holding.avg_cost_basis),
        'id': str(holding.id),
        'portfolio_id': str(holding.portfolio_id)
    }), 200

@holding_bp.route('/read_holdings/<uuid:portfolio_id>',methods=['GET'])
@jwt_required()
def read_all(portfolio_id):
    identity = get_jwt_identity()
    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id,user_id=identity).first()
    if not portfolio: 
        return jsonify({'message':'no holdings found'}), 404
    holdings = db.session.query(Holding).filter_by(portfolio_id=portfolio_id).all()
    if not holdings:
        return jsonify({'message':'no holdings found'}), 404
    result = []
    for h in holdings:
        result.append({
             'symbol': h.symbol,
        'shares': str(h.shares),
        'avg_cost_basis': str(h.avg_cost_basis),
        'id': str(h.id),
        'portfolio_id': str(h.portfolio_id)
        })
    return jsonify(result), 200

#no delete in holding because will be in transaction
    

