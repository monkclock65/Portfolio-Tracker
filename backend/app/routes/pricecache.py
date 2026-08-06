from flask import Blueprint, request, jsonify
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.pricing import finnhub_api


pricecache_bp = Blueprint('pricecache',__name__,url_prefix='/pricecache')

@pricecache_bp.route('/read_price/<symbol>',methods=['GET'])
@jwt_required()
def read(symbol):
    price = finnhub_api.read_price(symbol)
    return jsonify({'message':'price read successfully','price':str(price)}), 200

    
    
        