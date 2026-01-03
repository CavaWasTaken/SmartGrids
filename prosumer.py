"""
Prosumer class representing an individual energy consumer/producer
"""
import random
from typing import Dict, List, Tuple, Optional


class Prosumer:
    """
    Represents a prosumer in the energy community
    """
    
    def __init__(self, prosumer_id: int, pv_capacity: float, base_consumption: float, battery_capacity: float):
        """
        Initialize a prosumer
        
        Args:
            prosumer_id: Unique identifier
            pv_capacity: PV panel capacity in kW
            base_consumption: Base consumption level in kWh per time step
        """
        self.id = prosumer_id   # unique prosumer ID
        self.pv_capacity = pv_capacity   # PV panel capacity in kW
        self.base_consumption = base_consumption   # base consumption level in kWh per time step
        self.has_battery = battery_capacity > 0
        self.battery_capacity = battery_capacity    # kWh - battery capacity (if any)
        
        # Energy state
        self.pv_generation = 0.0  # kWh - current PV generation
        self.consumption = 0.0  # kWh - current energy consumption
        self.imbalance = 0.0  # kWh (positive = surplus, negative = deficit) - current energy imbalance
        
        # Trading state
        self.is_buyer = False   # whether prosumer is a buyer in current timestep
        self.is_seller = False  # whether prosumer is a seller in current timestep
        self.desired_quantity = 0.0  # kWh - desired trading quantity
        self.bid_price = 0.0  # €/kWh - bid price if buying
        self.ask_price = 0.0  # €/kWh - ask price if selling
        
        # Financial tracking
        self.balance = 0.0  # € - current financial balance
        self.renewable_usage = 0.0  # kWh - total renewable energy used
        self.p2p_trades = 0   # number of P2P trades participated in
        self.market_trades = 0   # number of local market trades participated
        self.market_quantity = 0.0  # kWh - total quantity traded on local market
        
        # Penalties and status
        self.is_banned = False  # whether prosumer is banned from trading
        self.ban_duration = 0   # duration of ban in timesteps
        self.reason_for_ban = ""  # reason for current ban
        self.total_profit = 0.0  # total profit accumulated
        self.penalties = 0.0  # € - total penalties incurred
        self.bonus = 0.0  # € - total bonuses received


    def update_energy_state(self, pv_generation: float, consumption: float):
        """
        Update prosumer's energy generation and consumption
        
        Args:
            pv_generation: PV generation in kWh
            consumption: Energy consumption in kWh
        """
        self.pv_generation = pv_generation  # overwrite current PV generation of the prosumer
        self.consumption = consumption  # overwrite current consumption of the prosumer
        
        # Step 1: Self-balancing
        self.imbalance = pv_generation - consumption    # evaluate imbalance (positive = surplus, negative = deficit)
        
        # Track renewable usage
        # if pv_generation > consumption: # all consumption is covered by renewable and excess is sold, consider the consumption only
        # if consumption >= pv_generation: # only part of consumption is covered by renewable, consider the pv generation only
        self.renewable_usage += min(pv_generation, consumption) # get the amount of renewable energy used by the prosumer
        
    def prepare_trading_offer(self, price_forecast: float, local_market_fee: float, max_trade_cap: float):
        """
        Prepare trading offer based on imbalance and price forecast
        
        Args:
            price_forecast: Forecasted market price in €/kWh
            local_market_fee: Fee for local market trading in €/kWh
            max_trade_cap: Maximum trade quantity per prosumer per time step in kWh
        """
        if self.is_banned:  # if the prosumer is banned, they cannot trade
            self.is_buyer = False   # reset buyer status
            self.is_seller = False  # reset seller status
            self.desired_quantity = 0.0 # reset desired quantity
            return
        
        if self.imbalance > 0.01:  # if there is Surplus - prosumer becomes seller
            self.is_seller = True   # set seller status
            self.is_buyer = False   # reset buyer status
            self.desired_quantity = min(self.imbalance, max_trade_cap)  # set desired quantity to surplus, capped by max trade cap

            grid_buy_price = price_forecast + (self.desired_quantity * local_market_fee)  # grid buy price including fee
            grid_sell_price = price_forecast - (self.desired_quantity * local_market_fee)   # grid sell price including fee

            spread = grid_buy_price - grid_sell_price  # evaluate spread between grid buy and sell prices
            urgency = self.desired_quantity / max_trade_cap  # evaluate urgency based on desired quantity

            noise = random.uniform(0.98, 1.05)   # strategic factor to adjust ask price
            
            calculated_ask = (grid_buy_price - (urgency * spread)) * noise  # set ask price lower than grid buy price based on urgency and strategic factor

            self.ask_price = min(calculated_ask, grid_buy_price * 0.99)  # ensure ask price is below grid buy price
            self.ask_price = max(self.ask_price, grid_sell_price * 1.01)  # ensure ask price is above grid sell price

        elif self.imbalance < -0.01:  # if there is Deficit - prosumer becomes buyer
            self.is_buyer = True   # set buyer status
            self.is_seller = False  # reset seller status
            self.desired_quantity = min(-self.imbalance, max_trade_cap)  # set desired quantity to deficit, capped by max trade cap
            
            grid_buy_price = price_forecast + (self.desired_quantity * local_market_fee)  # grid buy price including fee
            grid_sell_price = price_forecast - (self.desired_quantity * local_market_fee)   # grid sell price including fee

            spread = grid_buy_price - grid_sell_price  # evaluate spread between grid buy and sell prices
            urgency = self.desired_quantity / max_trade_cap  # evaluate urgency based on desired quantity
            
            noise = random.uniform(0.95, 1.02)   # strategic factor to adjust bid price

            calculated_bid = (grid_sell_price + (urgency * spread)) * noise  # set bid price higher than grid sell price based on urgency and strategic factor
            self.bid_price = max(calculated_bid, grid_sell_price * 1.01)  # ensure bid price is above grid sell price
            self.bid_price = min(self.bid_price, grid_buy_price * 0.99)  # ensure bid price is below grid buy price

        else:  # if balanced, no trading needed
            self.is_buyer = False   # reset buyer status
            self.is_seller = False  # reset seller status
            self.desired_quantity = 0.0 # reset desired quantity
    
    def accept_trade(self, quantity: float, price: float, is_buyer_role: bool, 
                     is_p2p: bool = True):
        """
        Accept a trade and update prosumer state
        
        Args:
            quantity: Energy trading quantity in kWh
            price: Trading price in €
            is_buyer_role: True if prosumer is buying, False if selling
            is_p2p: True if P2P trade, False if local market
        """
        if is_buyer_role:   # if the prosumer trading is in the buyer role
            # Buying energy
            self.imbalance += quantity  # increase imbalance by quantity bought
            self.balance -= price    # decrease balance by cost of purchase
        else:   # if the prosumer trading is in the seller role
            # Selling energy
            self.imbalance -= quantity  # decrease imbalance by quantity sold
            self.balance += price    # increase balance by revenue from sale
        
        self.desired_quantity = max(0, self.desired_quantity - quantity)    # update desired quantity (stored in absolute value) after trade by reducing it by traded quantity. Ensure no negative values.
        
        # Track trade type
        if is_p2p:  # if the trade is P2P
            self.p2p_trades += 1    # increment P2P trades count
        else:   # if the trade is local market
            self.market_trades += 1   # increment market trades count
    
    def calculate_remaining_imbalance(self) -> float:
        """
        Calculate remaining energy imbalance after trading
        
        Returns:
            Remaining imbalance in kWh
        """
        return self.imbalance   # return current imbalance (positive = surplus, negative = deficit)
    
    def apply_ban(self, duration: int, reason: str = ""):
        """
        Ban prosumer from trading
        
        Args:
            duration: Number of time steps to ban
        """
        self.is_banned = True   # set ban status to True
        self.ban_duration = duration    # set ban duration
        self.reason_for_ban = reason  # set reason for ban
    
    def reset_trading_state(self):
        """
        Reset trading state for next time step
        """
        self.is_buyer = False   # reset buyer status
        self.is_seller = False  # reset seller status
        self.desired_quantity = 0.0  # reset desired quantity
        self.bid_price = 0.0  # reset bid price
        self.ask_price = 0.0  # reset ask price
    
    def __repr__(self):
        return (f"Prosumer(id={self.id}, PV={self.pv_capacity:.1f}kW, "
                f"imbalance={self.imbalance:.2f}kWh, balance={self.balance:.2f}€)")
