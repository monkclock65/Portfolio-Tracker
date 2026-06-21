from app.models.transaction import Transaction,TransactionType
from app.models.holding import Holding
from app.models.portfolio import PORTFOLIO
from flask import Blueprint,request, jsonify
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

transaction_bp = Blueprint('transaction',__name__,url_prefix='/transaction')

@transaction_bp.route('/add_transaction/<uuid:portfolio_id>',methods=['POST'])
@jwt_required()
def insert(portfolio_id):
    identity = get_jwt_identity()
    portfolio_user_id = db.session.query(PORTFOLIO).filter_by(user_id=identity,id=portfolio_id)
    if not portfolio_user_id:
        return jsonify({'message':'portfolio not found'}), 404
    data = request.get_json()
    