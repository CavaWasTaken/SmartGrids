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

    def balance_trading_offers(self, prosumers: List[Prosumer], imbalance_threshold: float, price_forecast: float, local_market_fee: float, max_trade_cap: float):
        """
        Balance the total amount of energy to be traded among prosumers
        by finding prosumers with batteries that can offert their energy to who need it.
        
        Args:
            prosumers: List of prosumers
            imbalance_threshold: Threshold for balancing in kWh
            price_forecast: Forecasted market price in €/kWh
            local_market_fee: Fee for local market trading in €/kWh
            max_trade_cap: Maximum trade quantity per prosumer per time step in kWh
        """
        total_demand = sum(p.desired_quantity for p in prosumers 
                           if p.is_buyer and not p.is_banned)   # total demand from buyers
        total_supply = sum(p.desired_quantity for p in prosumers 
                           if p.is_seller and not p.is_banned)  # total supply from sellers
        
        imbalance = total_demand - total_supply  # calculate imbalance
        
        if abs(imbalance) <= imbalance_threshold:
            return  # no significant imbalance, no adjustment needed
        
        # extract usable battery levels from prosumers (not banned and with battery level above min soc)
        available_battery_levels = {p.id: p.battery_level - p.get_min_soc() for p in prosumers if not p.is_banned and p.battery_level > p.get_min_soc() and not p.is_buyer and not p.is_seller}

        # sort battery levels in descending order
        available_battery_levels = sorted(available_battery_levels.items(), key=lambda x: x[1], reverse=True)

        if imbalance > 0:  # excess demand
            # prosumers with higher battery levels can offer their energy
            for prosumer_id, available_battery_level in available_battery_levels:
                prosumer = next(p for p in prosumers if p.id == prosumer_id)
                # the prosumer becomes a seller of up to half of its available battery level
                offered_quantity = min(available_battery_level * 0.5, imbalance)
                prosumer.becomes_seller(offered_quantity, price_forecast, local_market_fee, max_trade_cap)
                imbalance -= offered_quantity
                if imbalance <= imbalance_threshold:
                    break  # stop if imbalance is resolved
    
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
                  and p.desired_quantity > 0]    # filter active buyers who are not banned and have desired quantity > 0
        sellers = [p for p in prosumers if p.is_seller and not p.is_banned 
                   and p.desired_quantity > 0]  # filter active sellers who are not banned and have desired quantity > 0
        
        if not buyers or not sellers:   # if no buyers or sellers, no trades possible
            return trades
        
        # Sort buyers by willingness to pay (highest first)
        buyers.sort(key=lambda x: x.bid_price, reverse=True)    # sort buyers by bid price descending
        
        # Sort sellers by asking price (lowest first)
        sellers.sort(key=lambda x: x.ask_price)    # sort sellers by ask price ascending
        
        # Match buyers and sellers - improved algorithm to maximize P2P trades
        # Try to match each buyer with compatible sellers
        for buyer in buyers:
            if buyer.desired_quantity < 0.01:  # Skip if buyer already satisfied
                continue
                
            # Find all sellers that this buyer can trade with (bid >= ask)
            for seller in sellers:
                if seller.desired_quantity < 0.01:  # Skip if seller already sold all
                    continue
                    
                # Check if trade is possible (buyer willing to pay >= seller asking)
                if buyer.bid_price >= seller.ask_price:
                    # Calculate trade quantity
                    trade_quantity = min(buyer.desired_quantity, seller.desired_quantity)
                    
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
                                     trade_price, 'p2p', timestamp)
                        trades.append(trade)
                        
                        # Check if buyer is satisfied
                        if buyer.desired_quantity < 0.01:
                            buyer.desired_quantity = 0.0
                            break  # Move to next buyer
        
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
