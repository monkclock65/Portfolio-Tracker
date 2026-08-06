from decimal import Decimal
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.pricing import PriceService

pricecache_bp = Blueprint('pricecache', __name__, url_prefix='/pricecache')

@pricecache_bp.route('/read_price/<symbol>', methods=['GET'])
@jwt_required()
def read(symbol):
    price = PriceService.read_price(symbol)
    if price == 0 or price == Decimal('0'):
        return jsonify({'message': 'price lookup failure. try again later'}), 400
    return jsonify({'message': 'price read successfully', 'price': str(price)}), 200

    
    
        