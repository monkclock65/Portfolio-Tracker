from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.portfolio import Portfolio, AccountType
from app.models.user import User
from flask_jwt_extended import jwt_required,get_jwt_identity

portfolio_bp = Blueprint('portfolio',__name__,url_prefix='/portfolio')

@portfolio_bp.route('/add_portfolio', methods=['POST'])
@jwt_required()
def insert():
    data = request.get_json()
    identity = get_jwt_identity()
    account_type = data.get('account_type')
    name = data.get('name')
    if not isinstance(name, str):
        return jsonify({'message': 'name must be a string'}), 400
    try:
        account_type = AccountType(account_type)
    except ValueError:
        return jsonify({'message': f'account_type must be one of {[e.value for e in AccountType]}'}), 400
    portfolio = Portfolio(account_type=account_type,user_id=identity,name=name)
    db.session.add(portfolio)
    db.session.commit()
    return jsonify({'message':'portfolio added successfully'}),200

@portfolio_bp.route('portfolio/<uuid:portfolio_id>',methods=['PATCH'])
@jwt_required()
def update(portfolio_id):
    data = request.get_json()
    identity = get_jwt_identity()
    account_type = data.get('account_type')
    name = data.get('name')
    if not name and not account_type:
        return jsonify({'message':'no valid update fields provided'}),400
    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id, user_id=identity).first()
    if not portfolio:
        return jsonify({'message': 'portfolio not found'}), 404
    if name:
        portfolio.name = name
    if account_type:
         try:
            portfolio.account_type = AccountType(account_type)
         except ValueError:
            return jsonify({'message': f'account_type must be one of {[e.value for e in AccountType]}'}), 400
    db.session.commit()
    return jsonify({'message':'portfolio updated successfully'}),200


@portfolio_bp.route('/<uuid:portfolio_id>',methods=['GET'])
@jwt_required()
def read(portfolio_id):
    identity = get_jwt_identity()
    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id, user_id=identity).first()
    if not portfolio:
        return jsonify({'message':'portfolio not found'}), 404
    return jsonify({
            'name': portfolio.name,
    'account_type': portfolio.account_type.value,
              'id': str(portfolio.id),
         'user id': str(portfolio.user_id),
                     }), 200

@portfolio_bp.route('/read_portfolio',methods=['GET'])
@jwt_required()
def read_all():
    identity = get_jwt_identity()
    portfolios = db.session.query(Portfolio).filter_by(user_id=identity).all()
    if not portfolios:
        return jsonify({'message':'no portfolios found'}), 404
    result = []
    for p in portfolios:
        result.append({
            'name': p.name,
    'account_type': p.account_type.value,
              'id': str(p.id)
        })
    return jsonify(result), 200
    
@portfolio_bp.route('/<uuid:portfolio_id>',methods=['DELETE'])
@jwt_required()
def delete(portfolio_id):
    identity = get_jwt_identity()
    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id, user_id=identity).first()
    if not portfolio:
        return jsonify({'message':'portfolio not found'}), 404
    db.session.delete(portfolio)
    db.session.commit()
    return jsonify({'message':'portfolio deleted successfully'}), 200
