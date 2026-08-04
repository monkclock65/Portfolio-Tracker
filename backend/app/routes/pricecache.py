from flask import Blueprint, request, jsonify
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.pricing import finnhub_api
from app.models.pricecache import PriceCache

pricecache_bp = Blueprint('pricecache',__name__,url_prefix='/pricecache')

@pricecache_bp.route('/add_price',methods=['POST'])
@jwt_required()
def update():
    data = request.get_json()
    symbol = data.get('symbol')
    if not symbol:
        return jsonify({'message':'request missing symbol'}), 400
    finnhub_api.add_price(symbol)
    return jsonify({'message':'price added successfully'}), 201

    
    
        