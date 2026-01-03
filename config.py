"""
Configuration parameters for the prosumer community simulator
"""

# Simulation parameters
NUM_PROSUMERS = 10
TIME_STEPS = 24  # 24 hours
TIME_STEP_DURATION = 1  # hours

# Prosumer parameters
MIN_PV_CAPACITY = 3  # kW
MAX_PV_CAPACITY = 10  # kW
MIN_BASE_CONSUMPTION = 0.3  # kWh per hour
MAX_BASE_CONSUMPTION = 3.0  # kWh per hour
BATTERY_CAPACITY = [0, 5, 10, 15, 20]  # kWh possible battery capacities

# Grid parameters
BASE_PRICE = 0.15  # €/kWh
MAX_TRADE_CAP = 3.0  # kWh maximum trade quantity per prosumer per time step

# Trading parameters
MAX_PRICE = 0.30  # €/kWh
MIN_PRICE = 0.05  # €/kWh
LOCAL_MARKET_FEE = 0.02  # €/kWh fee for local market trading

# Blockchain parameters
NUM_MINERS = 15
DIFFICULTY_TARGET = 3  # Number of leading zeros required
BLOCK_REWARD = 0.1  # € reward for mining a block
MAX_TRANSACTIONS_PER_BLOCK = 50

# Regulator strategy
REGULATOR_OBJECTIVE = "maximize_renewable"  # maximize_renewable, maximize_profit, maximize_p2p
RENEWABLE_BONUS = 0.02  # €/kWh bonus for using renewable energy
P2P_BONUS = 0.01  # €/kWh bonus for P2P trading
PENALTY_FOR_MARKET = 0.02  # €/kWh penalty for using local market

# Output settings
VERBOSE = True
SAVE_RESULTS = True
GENERATE_PLOTS = True
RESULTS_DIR = "results"
