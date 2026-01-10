"""
Prosumer class representing an individual energy consumer/producer
"""
import random
from typing import Dict, List, Tuple, Optional
import config


class Prosumer:
    """
    Represents a prosumer in the energy community
    """
    
    def __init__(self, prosumer_id: int, pv_capacity: float, base_consumption: float, battery_capacity: float, home_type_index: int = 0):
        """
        Initialize a prosumer
        
        Args:
            prosumer_id: Unique identifier
            pv_capacity: PV panel capacity in kW
            base_consumption: Base consumption level in kWh per time step
            battery_capacity: Battery capacity in kWh
            home_type_index: Index of the home configuration type
        """
        self.id = prosumer_id   # unique prosumer ID
        self.home_type_index = home_type_index  # home configuration index
        self.pv_capacity = pv_capacity   # PV panel capacity in kW
        self.base_consumption = base_consumption   # base consumption level in kWh per time step
        self.has_battery = battery_capacity > 0.0  # whether prosumer has a battery
        self.battery_capacity = battery_capacity    # kWh - battery capacity (if any)
        
        # Energy state
        self.pv_generation = 0.0  # kWh - current PV generation
        self.consumption = 0.0  # kWh - current energy consumption
        self.imbalance = 0.0  # kWh (positive = surplus, negative = deficit) - current energy imbalance
        self.battery_level = battery_capacity / 2 if self.has_battery else 0.0  # kWh - current battery level (initialized to half capacity if battery exists)

        # Trading state
        self.is_buyer = False   # whether prosumer is a buyer in current timestep
        self.is_seller = False  # whether prosumer is a seller in current timestep
        self.desired_quantity = 0.0  # kWh - desired trading quantity
        self.bid_price = 0.0  # €/kWh - bid price if buying
        self.ask_price = 0.0  # €/kWh - ask price if selling
        self.selling_from_battery = False  # whether selling energy is from battery
        
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
        self.total_profit = 0.0  # € - total profit accumulated
        self.penalties = 0.0  # € - total penalties incurred
        self.bonus = 0.0  # € - total bonuses received
        
        # Battery energy flow tracking (reset each timestep)
        self.battery_charged_kwh = 0.0  # Energy charged into battery this timestep
        self.battery_discharged_kwh = 0.0  # Energy discharged from battery this timestep


    def update_energy_state(self, pv_generation: float, consumption: float):
        """
        Update prosumer's energy generation and consumption with battery management
        
        Args:
            pv_generation: PV generation in kWh
            consumption: Energy consumption in kWh
        """
        self.pv_generation = pv_generation  # overwrite current PV generation of the prosumer
        self.consumption = consumption  # overwrite current consumption of the prosumer
        
        # Step 1: Calculate initial imbalance (before battery)
        initial_imbalance = pv_generation - consumption    # evaluate imbalance (positive = surplus, negative = deficit)
        
        # Track renewable usage (direct PV to consumption)
        self.renewable_usage += min(pv_generation, consumption) # get the amount of renewable energy used by the prosumer
        
        # Reset battery flow tracking for this timestep
        self.battery_charged_kwh = 0.0
        self.battery_discharged_kwh = 0.0
        
        # Step 2: Battery management to minimize grid dependency
        if self.has_battery:
            if initial_imbalance > 0:  # SURPLUS - try to store in battery
                # Calculate how much we can store (respecting max SoC and efficiency)
                max_level = self.battery_capacity * config.BATTERY_MAX_SOC
                available_space = max(0, max_level - self.battery_level)
                
                # Account for efficiency loss: if we have X space, we can input X/efficiency
                # This ensures battery reaches exactly max_level when fully charged
                max_input_energy = available_space / config.BATTERY_EFFICIENCY
                energy_to_store = min(initial_imbalance, max_input_energy)
                
                # Store energy in battery (with charging efficiency loss)
                actual_stored = energy_to_store * config.BATTERY_EFFICIENCY
                self.battery_level += actual_stored
                self.imbalance = initial_imbalance - energy_to_store
                
                # Track energy charged into battery (input energy before efficiency loss)
                self.battery_charged_kwh = energy_to_store
                
            elif initial_imbalance < 0:  # DEFICIT - try to discharge from battery
                # Calculate how much we can discharge (respecting min SoC and efficiency)
                min_level = self.battery_capacity * config.BATTERY_MIN_SOC
                available_energy = max(0, self.battery_level - min_level)
                energy_needed = abs(initial_imbalance)
                
                # Discharge energy from battery (with discharging efficiency loss)
                energy_to_discharge = min(energy_needed / config.BATTERY_EFFICIENCY, available_energy)
                actual_output = energy_to_discharge * config.BATTERY_EFFICIENCY
                
                self.battery_level -= energy_to_discharge
                self.imbalance = initial_imbalance + actual_output
                
                # Track energy discharged from battery (output energy after efficiency loss)
                self.battery_discharged_kwh = actual_output
                
                # Track renewable usage (discharged energy was renewable and is now consumed)
                self.renewable_usage += actual_output
            else:
                self.imbalance = initial_imbalance
        else:
            self.imbalance = initial_imbalance

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

            grid_buy_price = price_forecast + local_market_fee  # grid buy price including fee
            grid_sell_price = price_forecast - local_market_fee   # grid sell price including fee

            spread = grid_buy_price - grid_sell_price  # evaluate spread between grid buy and sell prices
            urgency = self.desired_quantity / max_trade_cap  # evaluate urgency based on desired quantity

            noise = random.uniform(0.98, 1.05)   # strategic factor to adjust ask price
            
            calculated_ask = (grid_sell_price + (urgency * spread)) * noise  # set ask price starting from grid_sell_price, increasing with urgency

            self.ask_price = max(calculated_ask, grid_sell_price * 1.01)  # ensure ask price is above grid sell price
            self.ask_price = min(self.ask_price, grid_buy_price * 0.95)  # ensure ask price leaves room for P2P matching

        elif self.imbalance < -0.01:  # if there is Deficit - prosumer becomes buyer
            self.is_buyer = True   # set buyer status
            self.is_seller = False  # reset seller status
            self.desired_quantity = min(-self.imbalance, max_trade_cap)  # set desired quantity to deficit, capped by max trade cap
            
            grid_buy_price = price_forecast + local_market_fee  # grid buy price including fee
            grid_sell_price = price_forecast - local_market_fee   # grid sell price including fee

            spread = grid_buy_price - grid_sell_price  # evaluate spread between grid buy and sell prices
            urgency = self.desired_quantity / max_trade_cap  # evaluate urgency based on desired quantity
            
            noise = random.uniform(0.97, 1.01)   # strategic factor to adjust bid price

            # Buyers bid closer to grid_buy_price as urgency increases (willing to pay more when desperate)
            # Start from midpoint and move toward grid_buy with urgency
            midpoint = (grid_sell_price + grid_buy_price) / 2
            calculated_bid = (midpoint + (urgency * spread * 0.5)) * noise  # willing to pay more when urgent
            
            self.bid_price = min(calculated_bid, grid_buy_price * 0.97)  # ensure bid price is below grid buy price
            self.bid_price = max(self.bid_price, grid_sell_price * 1.08)  # ensure bid price leaves room for P2P matching

        else:  # if balanced, no trading needed
            self.is_buyer = False   # reset buyer status
            self.is_seller = False  # reset seller status
            self.desired_quantity = 0.0 # reset desired quantity

    def becomes_seller(self, offered_quantity: float, price_forecast: float, local_market_fee: float, max_trade_cap: float):
        """
        Make prosumer a seller of the offered quantity from battery
        Battery sellers price more competitively than PV surplus sellers to facilitate P2P trades
        
        Args:
            offered_quantity: Quantity offered to sell in kWh
            price_forecast: Forecasted market price in €/kWh
            local_market_fee: Fee for local market trading in €/kWh
            max_trade_cap: Maximum trade quantity per prosumer per time step in kWh
        """

        self.selling_from_battery = True  # indicate that the prosumer is selling energy from battery
        self.desired_quantity += offered_quantity  # set desired quantity to offered quantity
        self.is_seller = True   # set seller status
        self.is_buyer = False   # reset buyer status
        self.desired_quantity = min(self.desired_quantity, max_trade_cap)  # set desired quantity to surplus, capped by max trade cap

        grid_buy_price = price_forecast + local_market_fee  # grid buy price including fee
        grid_sell_price = price_forecast - local_market_fee   # grid sell price including fee

        spread = grid_buy_price - grid_sell_price  # evaluate spread between grid buy and sell prices
        urgency = self.desired_quantity / max_trade_cap  # evaluate urgency based on desired quantity

        # Battery sellers price more competitively (lower noise, smaller urgency factor)
        # This makes them attractive to buyers who would otherwise go to local market
        noise = random.uniform(0.95, 1.00)   # lower noise range than PV sellers (0.98-1.05)
        
        # midpoint between grid_sell and price_forecast, not grid_sell_price
        # This accounts for battery storage costs but remains competitive
        base_battery_price = (grid_sell_price + price_forecast) / 2  # ~0.135 for forecast=0.15
        
        # Add smaller urgency premium (0.3x instead of 1.0x of spread)
        calculated_ask = (base_battery_price + (urgency * spread * 0.3)) * noise
        
        # Ensure price is above grid_sell but below typical buyer bids
        self.ask_price = max(calculated_ask, grid_sell_price * 1.03)  # min 3% above grid sell
        self.ask_price = min(self.ask_price, grid_buy_price * 0.85)  # max 85% of grid buy (vs 95% for PV)

    
    def get_min_soc(self) -> float:
        """
        Get minimum state of charge (SoC) for the battery
        
        Returns:
            Minimum SoC in kWh
        """
        if not self.has_battery:
            return 0.0
        return self.battery_capacity * config.BATTERY_MIN_SOC
    
    def accept_trade(self, quantity: float, price: float, is_buyer_role: bool, 
                     is_p2p: bool = True):
        """
        Accept a trade and update prosumer state
        
        Args:
            quantity: Energy trading quantity in kWh
            price: Trading price in €/kWh
            is_buyer_role: True if prosumer is buying, False if selling
            is_p2p: True if P2P trade, False if local market
        """
        if is_buyer_role:   # if the prosumer trading is in the buyer role
            # Buying energy
            self.imbalance += quantity  # increase imbalance by quantity bought
            self.balance -= price * quantity    # decrease balance by cost of purchase
        else:   # if the prosumer trading is in the seller role
            # Selling energy
            if not self.selling_from_battery:
                self.imbalance -= quantity  # decrease imbalance by quantity sold
            else:
                self.battery_level -= quantity  # decrease battery level by quantity sold
                self.battery_discharged_kwh += quantity  # track energy discharged for sale
            self.balance += price * quantity    # increase balance by revenue from sale
        
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
            duration: Number of timesteps to ban
            reason: Reason for the ban
        """
        self.is_banned = True
        self.ban_duration = duration
        self.reason_for_ban = reason
    
    def update_ban_status(self):
        """
        Update ban status - decrement duration and lift ban if expired
        Called at the start of each timestep
        """
        if self.is_banned and self.ban_duration > 0:
            self.ban_duration -= 1
            if self.ban_duration <= 0:
                self.is_banned = False
                self.ban_duration = 0
                self.reason_for_ban = ""
    
    def reset_trading_state(self):
        """
        Reset trading state for next time step
        """
        self.is_buyer = False   # reset buyer status
        self.is_seller = False  # reset seller status
        self.selling_from_battery = False  # reset selling from battery status
        self.desired_quantity = 0.0  # reset desired quantity
        self.bid_price = 0.0  # reset bid price
        self.ask_price = 0.0  # reset ask price
    
    def get_battery_info(self) -> dict:
        """
        Get battery information for logging
        
        Returns:
            Dictionary with battery stats
        """
        if not self.has_battery:
            return {
                'has_battery': False,
                'capacity': 0,
                'level': 0,
                'soc': 0
            }
        
        return {
            'has_battery': True,
            'capacity': round(self.battery_capacity, 2),
            'level': round(self.battery_level, 2),
            'soc': round(self.battery_level / self.battery_capacity * 100, 1) if self.battery_capacity > 0 else 0
        }
    
    def __repr__(self):
        battery_info = f", Battery: {self.battery_level:.1f}/{self.battery_capacity:.1f}kWh" if self.has_battery else ""
        return (f"Prosumer(id={self.id}, PV={self.pv_capacity:.1f}kW{battery_info}, "
                f"imbalance={self.imbalance:.2f}kWh, balance={self.balance:.2f}€)")
