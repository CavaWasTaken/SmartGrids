"""
Data generation for PV generation and price forecasting
"""
import math
import random
from typing import List

def generate_pv_generation(hour: int, pv_capacity: float) -> float:
    """
    Generate PV generation based on hour and capacity using a sinusoidal pattern
    
    Args:
        hour: Hour of day (0-23)
        pv_capacity: PV capacity of the prosumer in kW
    
    Returns:
        PV generation of the prosumer in kWh for the hour
    """
    # PV generation only during daylight hours (sunrise ~6am, sunset ~6pm)
    if hour < 5 or hour > 19:   # before 5 am and after 7 pm no generation
        return 0.0
    
    # Sinusoidal pattern peaking at noon
    daylight_hour = hour - 5    # 0 to 14 hours of daylight
    
    # Calculate generation factor (0 to 1) - peak at 12 PM - at 5 am and 7 pm is 0
    angle = math.pi * daylight_hour / 14  # 14 hours of daylight
    generation_factor = math.sin(angle)

    # Add some randomness for clouds/weather
    weather_factor = random.uniform(0.7, 1.0)
    
    # Calculate actual generation (kWh = kW * hours * factors)
    generation = pv_capacity * 1.0 * generation_factor * weather_factor
    
    return max(0.0, generation) # return the pv generation and ensure non-negative values


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
        0: 0.5, 1: 0.4, 2: 0.4, 3: 0.4, 4: 0.5, 5: 0.7,  # Night to early morning
        6: 1.2, 7: 1.5, 8: 1.3, 9: 1.0, 10: 0.9, 11: 1.0,  # Morning peak
        12: 1.1, 13: 0.9, 14: 0.8, 15: 0.8, 16: 0.9, 17: 1.0,  # Afternoon
        18: 1.4, 19: 1.6, 20: 1.5, 21: 1.3, 22: 1.0, 23: 0.7   # Evening peak
    }
    
    pattern_factor = consumption_patterns.get(hour, 1.0)    # get pattern factor for the hour of the day with default 1.0
    
    # Add some randomness for individual behavior
    variation = random.uniform(0.8, 1.2)
    
    consumption = base_consumption * pattern_factor * variation
    
    return max(0.1, consumption)    # return consumption ensuring a minimum consumption


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


def generate_hourly_data(num_hours: int = 24) -> List[dict]:
    """
    Generate complete hourly data for simulation
    
    Args:
        num_hours: Number of hours to generate data for
    
    Returns:
        List of dictionaries with hour, price forecast
    """
    data = []
    
    for hour in range(num_hours):
        data.append({
            'hour': hour,
            'price_forecast': forecast_price(hour)
        })
    
    return data
