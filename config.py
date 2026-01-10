# Simulation parameters
NUM_PROSUMERS = 100
TIME_STEPS = 24  # 24 hours
TIME_STEP_DURATION = 1  # hours

# Prosumer parameters
PV_CAPACITY = [ 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0 ]  # kW
BASE_CONSUMPTION = [ 0.35, 0.45, 0.55, 0.65, 0.75, 0.90, 1.05, 1.20, 1.35, 1.50 ]  # kWh per time step
HAS_BATTERY = 0.8  # 80% of prosumers have a battery
BATTERY_CAPACITY = [ 5.0, 7.0, 8.0, 10.0, 12.0, 13.0, 15.0, 17.0, 18.0, 20.0 ]  # kWh possible battery capacities
BATTERY_EFFICIENCY = 0.95  # Round-trip efficiency (5% loss on charge/discharge cycle)
BATTERY_MIN_SOC = 0.1  # Minimum state of charge (10% reserve)
BATTERY_MAX_SOC = 0.95  # Maximum state of charge (95% to protect battery)

# Grid parameters
BASE_PRICE = 0.15  # €/kWh
MAX_TRADE_CAP = 3.0  # kWh maximum trade quantity per prosumer per time step

# Trading parameters
LOCAL_MARKET_FEE = 0.03  # €/kWh fee for local market trading
IMBALANCE_THRESHOLD = 0.05  # kWh threshold for balancing the amount of energy to trade

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