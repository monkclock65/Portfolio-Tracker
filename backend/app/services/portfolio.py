from app.services.pricing import PriceService
from flask import jsonify
from app.extensions import db
from app.models.holding import Holding

class portfolio_service:
    def portfolio_summary(portfolio_id):
        total_value = 0
        cost_basis = 0 
        holdings = db.session.query(Holding).filter_by(portfolio_id=portfolio_id).all()
        if not holdings:
            return jsonify({'message':'no holdings found'}), 404
        result = []
        for h in holdings:
                price = PriceService.read_price(h.symbol)
                result.append({
                'price' : str(price),
                'symbol': h.symbol,
                'shares': str(h.shares),
                'avg_cost_basis': str(h.avg_cost_basis),
                'id': str(h.id),
                })
        return jsonify(result), 200