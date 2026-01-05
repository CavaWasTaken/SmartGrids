"""
Data generation for PV generation and price forecasting
"""
import math
import random
from typing import List

def generate_pv_generation(hour: int, pv_capacity: float) -> float:
    """
    Generate realistic residential PV generation (kWh) per hour
    """

    # Daylight hours: 6 AM to 6 PM
    if hour < 6 or hour >= 18:
        return 0.0

    # Map hour to daylight index: 0 → 12
    daylight_hour = hour - 6

    # Sinusoidal solar curve (peak at noon)
    angle = math.pi * daylight_hour / 12
    generation_factor = math.sin(angle)

    # System losses & panel efficiency (inverter, temperature, dust)
    system_efficiency = 0.88   # realistic residential average

    # Weather variability (clouds, haze)
    weather_factor = random.uniform(0.5, 1.0)

    # kWh = kW * 1h * factors
    generation = (
        pv_capacity
        * generation_factor
        * system_efficiency
        * weather_factor
    )

    return max(0.0, generation)

def generate_consumption(hour: int, base_consumption: float) -> float:
    """
    Generate consumption based on hour and base consumption with typical daily pattern
    
    Args:
        hour: Hour of day (0-23)
        base_consumption: Base consumption level of the prosumer in kWh
    
    Returns:
        Consumption of the prosumer in kWh for the hour
    """
    # Typical consumption pattern with peaks in morning and evening
    consumption_patterns = {
        0: 0.4, 1: 0.35, 2: 0.35, 3: 0.35, 4: 0.4, 5: 0.6,
        6: 1.1, 7: 1.4, 8: 1.2, 9: 0.9, 10: 0.8, 11: 0.9,
        12: 1.0, 13: 0.9, 14: 0.8, 15: 0.8, 16: 0.9, 17: 1.1,
        18: 1.6, 19: 1.9, 20: 1.7, 21: 1.4, 22: 1.0, 23: 0.6
    }
    
    pattern_factor = consumption_patterns.get(hour, 1.0)    # get pattern factor for the hour of the day with default 1.0
    
    # Add some randomness for individual behavior
    variation = random.uniform(0.85, 1.15)
    
    consumption = base_consumption * pattern_factor * variation
    
    return max(0.25, consumption)    # return consumption ensuring a minimum consumption


def forecast_price(hour: int, base_price: float = 0.15) -> float:
    """
    Forecast electricity price based on hour with typical price patterns
    
    Args:
        hour: Hour of day (0-23)
        base_price: Base price in €/kWh
    
    Returns:
        Forecasted price in €/kWh
    """
    # Price patterns following demand (higher during peak hours)
    price_factors = {
        0: 0.7, 1: 0.6, 2: 0.6, 3: 0.6, 4: 0.7, 5: 0.9,  # Night low prices
        6: 1.3, 7: 1.5, 8: 1.4, 9: 1.2, 10: 1.1, 11: 1.2,  # Morning high
        12: 1.3, 13: 1.1, 14: 1.0, 15: 1.0, 16: 1.1, 17: 1.2,  # Afternoon
        18: 1.5, 19: 1.6, 20: 1.5, 21: 1.3, 22: 1.1, 23: 0.9   # Evening peak
    }
    
    factor = price_factors.get(hour, 1.0)   # get price factor for the hour of the day with default 1.0
    
    # Add small random variation for forecast uncertainty
    uncertainty = random.uniform(0.95, 1.05)
    
    price = base_price * factor * uncertainty
    
    return round(price, 4)  # return price rounded to 4 decimal places
