from app.services.pricing import PriceService
from app.extensions import db
from app.models.holding import Holding
from decimal import Decimal

class portfolio_service:
    def portfolio_summary(portfolio_id):
        total_value = 0
        cost_basis = 0
        gain_loss = 0 
        value = 0
        total_cost_basis = 0
        holdings = db.session.query(Holding).filter_by(portfolio_id=portfolio_id).all()
        if not holdings:
            result = []
            portfolio_summary = {'total_value':0,
                                 'total_cost_basis':0,
                                 'total_gain_loss':0,
                                 'total_gain_loss_pct':0}
            return {'holdings_summary':result,'portfolio_summary':portfolio_summary}
        result = []
        for h in holdings:
                price = PriceService.read_price(h.symbol)
                price_is_estimated = price is None
                if price_is_estimated:
                     price = h.avg_cost_basis
                     
                
                value = price * h.shares
                cost_basis = h.avg_cost_basis * h.shares
                gain_loss = value - cost_basis
                total_value = total_value + value
                total_cost_basis = total_cost_basis + cost_basis

                result.append({
                'price_is_estimated': price_is_estimated,
                'symbol': h.symbol,
                'value': str(value),
                'price' : str(price),
                'shares': str(h.shares),
                'gain_loss':str(gain_loss),
                'avg_cost_basis': str(h.avg_cost_basis),
                'id': str(h.id),
                })
        total_gain_loss = total_value - total_cost_basis
        total_gain_loss_pct = total_gain_loss/total_cost_basis if total_cost_basis else 0
        for item in result:
                  item['allocation_pct'] = Decimal(item['value'])/total_value if total_value else 0

        portfolio_summary = {
             'total_value': total_value,
             'total_cost_basis': total_cost_basis,
             'total_gain_loss': total_gain_loss,
             'total_gain_loss_pct': total_gain_loss_pct
            }
        return {'holdings_summary':result,'portfolio_summary':portfolio_summary}