"""
Trading mechanisms: P2P (peer-to-peer) and Local Market
"""
from typing import List, Tuple, Dict
from prosumer import Prosumer
import random


class Trade:
    """Represents a single trade transaction"""
    
    def __init__(self, buyer_id: int, seller_id: int, quantity: float, 
                 price: float, trade_type: str, timestamp: int):
        self.buyer_id = buyer_id    # ID of the buyer prosumer
        self.seller_id = seller_id  # ID of the seller prosumer
        self.quantity = quantity    # Energy trading quantity in kWh
        self.price = price          # Trading price per kWh in €
        self.trade_type = trade_type  # 'p2p' or 'local_market'
        self.timestamp = timestamp  # Timestamp of the trade
    
    def to_dict(self) -> dict:
        """Convert trade to dictionary for blockchain"""
        return {
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'quantity': round(self.quantity, 4),
            'price': round(self.price, 4),
            'total_cost': round(self.quantity * self.price, 4),
            'type': self.trade_type,
            'timestamp': self.timestamp
        }
    
    def __repr__(self):
        return (f"Trade(buyer={self.buyer_id}, seller={self.seller_id}, "
                f"qty={self.quantity:.2f}kWh, price={self.price:.3f}€/kWh, "
                f"type={self.trade_type})")


class P2PTradingMechanism:
    """
    Self-organized peer-to-peer trading mechanism
    Uses simple price matching: sort buyers and sellers by price
    """
    
    def __init__(self):
        self.trades = []    # list of executed trades
    
    def execute_p2p_trading(self, prosumers: List[Prosumer], 
                           timestamp: int) -> List[Trade]:
        """
        Execute P2P trading between prosumers
        
        Args:
            prosumers: List of prosumers
            timestamp: Current time step
        
        Returns:
            List of executed trades
        """
        trades = [] # list of executed trades at this time step
        
        # Get buyers and sellers (not banned)
        buyers = [p for p in prosumers if p.is_buyer and not p.is_banned 
                  and p.desired_quantity > 0.01]    # filter active buyers who are not banned and have desired quantity > 0.01
        sellers = [p for p in prosumers if p.is_seller and not p.is_banned 
                   and p.desired_quantity > 0.01]  # filter active sellers who are not banned and have desired quantity > 0.01
        
        if not buyers or not sellers:   # if no buyers or sellers, no trades possible
            return trades
        
        # Sort buyers by willingness to pay (highest first)
        buyers.sort(key=lambda x: x.bid_price, reverse=True)    # sort buyers by bid price descending
        
        # Sort sellers by asking price (lowest first)
        sellers.sort(key=lambda x: x.ask_price)    # sort sellers by ask price ascending
        
        # Match buyers and sellers
        buyer_idx = 0   # index for buyers
        seller_idx = 0  # index for sellers
        
        while buyer_idx < len(buyers) and seller_idx < len(sellers):    # iterate while there are buyers and sellers to match
            buyer = buyers[buyer_idx]   # current buyer
            seller = sellers[seller_idx]    # current seller
            
            # Check if trade is possible (buyer willing to pay >= seller asking)
            if buyer.bid_price >= seller.ask_price: # check if the buyer accepts to pay the seller's ask price
                # Calculate trade quantity - if the buyer wants more than the seller has, trade only what the seller has. If the buyer wants less, trade only what the buyer wants
                trade_quantity = min(buyer.desired_quantity, seller.desired_quantity)   # determine trade quantity based on seller and buyer desired quantities
                
                if trade_quantity > 0.01:  # Minimum trade size
                    # Trade price is average of bid and ask
                    trade_price = (buyer.bid_price + seller.ask_price) / 2
                    
                    # Execute trade
                    buyer.accept_trade(trade_quantity, trade_price, 
                                      is_buyer_role=True, is_p2p=True)
                    seller.accept_trade(trade_quantity, trade_price, 
                                       is_buyer_role=False, is_p2p=True)
                    
                    # Record trade
                    trade = Trade(buyer.id, seller.id, trade_quantity, 
                                 trade_price, 'p2p', timestamp) # create trade record
                    trades.append(trade)    # add trade to list
            
            # Move to next buyer or seller
            if buyer.desired_quantity < 0.01:   # if buyer has no more desired quantity
                buyer_idx += 1  # skip to next buyer
            if seller.desired_quantity < 0.01:  # if seller has no more desired quantity
                seller_idx += 1 # skip to next seller
            
            # If there is no seller willing to sell at buyer's bid price, let the buyer retry with a slightly higher bid or skip after 3 retries
            if buyer.bid_price < seller.ask_price:
                buyer_idx += 1
        
        self.trades.extend(trades)  # add executed trades to overall trade list
        return trades


class LocalMarketMechanism:
    """
    Local market trading through aggregator
    Uses simple order matching with market price
    """
    
    def __init__(self, aggregator_id: int = -1, transaction_fee: float = 0.02):
        self.aggregator_id = aggregator_id  # ID of the aggregator which manages the market
        self.transaction_fee = transaction_fee  # €/kWh fee charged by aggregator to each trade
        self.trades = []
    
    def execute_local_market(self, prosumers: List[Prosumer], 
                            market_price: float, timestamp: int) -> List[Trade]:
        """
        Execute local market trading for remaining imbalances, where prosumers trade with the aggregator their energy at market price plus/minus fee.
        
        Args:
            prosumers: List of prosumers
            market_price: Current market price in €/kWh
            timestamp: Current time step
        
        Returns:
            List of executed trades
        """
        trades = [] # list of executed trades at this time step
        
        # Get prosumers still with imbalance after P2P
        buyers = [p for p in prosumers if not p.is_banned and 
                  p.desired_quantity > 0.01 and 
                  p.calculate_remaining_imbalance() < -0.01]    # buyers needing energy
        
        sellers = [p for p in prosumers if not p.is_banned and 
                   p.desired_quantity > 0.01 and 
                   p.calculate_remaining_imbalance() > 0.01]   # sellers with surplus energy
        
        if not buyers and not sellers:  # if no buyers or sellers, no trades possible
            return trades

        # satisfy sellers and buyers at market price, Sellers will sell their energy to the grid via the aggregator, Buyers will buy their energy from the grid via the aggregator
        for seller in sellers:
            if seller.desired_quantity > 0.01:
                trade_quantity = seller.desired_quantity
                market_sell_price = market_price - (self.transaction_fee * trade_quantity)  # price received by seller after fee
                seller.accept_trade(trade_quantity, market_sell_price, 
                                   is_buyer_role=False, is_p2p=False)
                
                seller.market_quantity += trade_quantity  # track quantity traded on local market

                # Record trade
                trade = Trade(self.aggregator_id, seller.id, trade_quantity, 
                             market_sell_price, 'local_market', timestamp)
                trades.append(trade)

        for buyer in buyers:
            if buyer.desired_quantity > 0.01:
                trade_quantity = buyer.desired_quantity
                market_buy_price = market_price + (self.transaction_fee * trade_quantity)  # price paid by buyer including fee
                buyer.accept_trade(trade_quantity, market_buy_price, 
                                  is_buyer_role=True, is_p2p=False)
                
                buyer.market_quantity += trade_quantity  # track quantity traded on local market
                
                # Record trade
                trade = Trade(buyer.id, self.aggregator_id, trade_quantity, 
                             market_buy_price, 'local_market', timestamp)
                trades.append(trade)

        self.trades.extend(trades)  # add executed trades to overall trade list
        return trades

    def calculate_aggregator_profit(self) -> float:
        """Calculate total profit for aggregator from fees"""
        total_profit = 0.0
        for trade in self.trades:
            if trade.trade_type == 'local_market':
                total_profit += trade.quantity * self.transaction_fee * 2
        return total_profit
