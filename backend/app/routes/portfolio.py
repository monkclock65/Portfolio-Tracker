from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.portfolio import Portfolio
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
    if not account_type or not name:
        return jsonify({'message':'missing account_type or name fields'}),400
    if not isinstance(account_type,str) or not isinstance(name,str):
        return jsonify({'message':'account_type and name must be strings'}),400
    portfolio = Portfolio(account_type=account_type,user_id=identity,name=name)
    db.session.add(portfolio)
    db.session.commit()
    return jsonify({'message':'portfolio added successfully'}),200

@portfolio_bp.route('/<uuid:portfolio_id>',methods=['PATCH'])
@jwt_required()
def update(portfolio_id):
    data = request.get_json()
    identity = get_jwt_identity()
    account_type = data.get('account_type')
    name = data.get('name')
    if not name and not account_type:
        return jsonify({'messge':'no valid update fields provided'}),400
    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id, user_id=identity).first()
    if not portfolio:
        return jsonify({'message': 'portfolio not found'}), 404
    if name:
        portfolio.name = name
    if account_type:
        portfolio.account_type = account_type
    db.session.commit()
    return jsonify({'message':'portfolio updated successfully'}),200


