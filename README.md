# Prosumer Community Energy Trading Simulator

A comprehensive blockchain-based simulation platform for modeling self-organized energy trading within prosumer communities, featuring autonomous decision-making, Proof-of-Work consensus, battery storage management, and regulatory mechanisms.

## Project Overview

This simulator models a decentralized energy community where 100 prosumers (producer-consumers) with photovoltaic panels and battery storage systems autonomously trade energy through a three-tier balancing mechanism: **self-consumption with battery management**, **peer-to-peer (P2P) bilateral trading**, and **local market aggregation**. All transactions are recorded on a blockchain using Proof-of-Work consensus with 15 distributed miners.

The system implements intelligent prosumer agents that make autonomous decisions based on economic optimization, a regulatory framework that incentivizes renewable energy usage while penalizing excessive grid dependency, and comprehensive data logging with visualization capabilities for analysis.

## System Architecture

### Core Components

1. **Prosumer Agents** (`prosumer.py`)
   - Autonomous energy agents with PV generation (2.5-7.0 kW capacity)
   - Smart battery storage systems (5-20 kWh capacity, 95% round-trip efficiency)
   - Dynamic consumption patterns based on 10 home type profiles
   - Intelligent trading strategies (bidding/asking prices based on imbalance and forecasts)
   - Financial tracking with balance, penalties, bonuses, and renewable usage metrics
   - Ban management system for rule enforcement

2. **Energy Balancing Mechanisms**
   - **Phase 1**: Self-consumption with battery optimization (charge surplus, discharge deficit)
   - **Phase 2**: P2P bilateral trading with intelligent price negotiation
   - **Phase 3**: Local market aggregation for remaining imbalances
   - Maximum trade cap: 3.0 kWh per prosumer per timestep
   - Local market transaction fee: 0.03 €/kWh

3. **Blockchain Infrastructure** (`blockchain.py`)
   - Distributed ledger with Proof-of-Work consensus
   - 15 competing miners validating transactions
   - Difficulty target: 3 leading zeros in block hash
   - Block reward: 0.1 € per mined block
   - Maximum 50 transactions per block
   - Genesis block initialization with complete transaction history

4. **Regulatory Framework** (`regulator.py`)
   - Objective: Maximize renewable energy usage
   - Incentives: 0.02 €/kWh bonus for renewable self-consumption
   - Penalties: 0.02 €/kWh for local market usage (instead of P2P)
   - Rule enforcement: Bans prosumers with excessive market usage or negative balance
   - Ban durations: 2-3 timesteps based on violation severity

5. **Simulation Orchestrator** (`simulator.py`)
   - 24-hour simulation with hourly timesteps
   - 100 prosumers with randomized but consistent home types
   - Real-time energy state updates and trading execution
   - CSV-based data logging for efficient time-series storage
   - Blockchain transaction recording and mining coordination

6. **Data Generation** (`data_generation.py`)
   - Realistic PV generation curves based on solar irradiance patterns
   - Time-varying consumption profiles with peak demand periods
   - Dynamic price forecasting (0.10-0.20 €/kWh range)

7. **Visualization System** (`plot_results.py`)
   - 20+ comprehensive plots analyzing simulation results
   - Community-level metrics (energy flows, trading activity, imbalances)
   - Individual prosumer analysis (energy states, battery usage, financial tracking)
   - Trading mechanism comparison (P2P vs market efficiency)
   - Blockchain statistics (mining activity, transaction distribution)
   - Regulatory impact assessment (bonuses, penalties, ban patterns)

## Project Structure

```
SmartGrids/
├── README.md                  # Project documentation
├── config.py                  # Simulation parameters and constants
├── prosumer.py                # Prosumer agent class (342 lines)
├── blockchain.py              # Blockchain with PoW consensus (227 lines)
├── regulator.py               # Regulatory framework (167 lines)
├── data_generation.py         # Energy and price generation
├── simulator.py               # Main simulation orchestrator (389 lines)
├── plot_results.py            # Visualization module (635 lines)
├── main.py                    # Entry point
├── ProjectDescription.txt     # Original project requirements
└── results/                   # Simulation outputs (created at runtime)
    ├── prosumer_energy.csv    # Timestep-by-timestep energy states
    ├── prosumer_trading.csv   # Trading roles and activity
    ├── all_trades.csv         # Complete trade log (P2P + market)
    ├── regulator_actions.csv  # Bonuses, penalties, and bans
    ├── community_summary.csv  # Aggregated community metrics
    └── plots/                 # Generated visualizations (20+ plots)
```

## Key Features

### Energy Management
- **Smart Battery Storage**: 80% of prosumers have batteries (5-20 kWh capacity)
- **Battery Efficiency**: 95% round-trip efficiency with 10-95% SoC operating range
- **Self-Consumption Optimization**: Automatic battery charge/discharge based on PV-load balance
- **Renewable Usage Tracking**: Real-time monitoring of renewable energy utilization

### Trading Mechanisms
- **Three-Tier Balancing**: Self → P2P → Local Market cascade
- **Intelligent P2P Matching**: Buyers and sellers negotiate bilateral trades
- **Price Discovery**: Dynamic bid/ask prices based on imbalance and market forecasts
- **Trade Execution**: Maximum 3.0 kWh per prosumer per timestep
- **Market Aggregation**: Local market handles remaining imbalances with 0.03 €/kWh fee

### Blockchain & Consensus
- **Distributed Mining**: 15 independent miners compete to validate blocks
- **Proof-of-Work**: SHA-256 hashing with 3 leading zero difficulty
- **Transaction Recording**: All P2P and market trades recorded on-chain
- **Mining Rewards**: 0.1 € per block incentivizes miner participation
- **Block Size Limit**: Maximum 50 transactions per block

### Regulatory System
- **Renewable Incentives**: 0.02 €/kWh bonus for self-consumed renewable energy
- **Market Penalties**: 0.02 €/kWh penalty for using local market instead of P2P
- **Rule Enforcement**: Automatic bans for excessive penalties or negative balance
- **Ban Mechanisms**: Temporary exclusion (2-3 timesteps) with reason tracking
- **Financial Tracking**: Complete audit trail of bonuses, penalties, and balances

### Data Analysis
- **Comprehensive Logging**: 6 CSV files capturing all simulation metrics
- **Time-Series Analysis**: Hourly tracking of energy states, trades, and financial flows
- **Multi-Level Aggregation**: Individual prosumer and community-wide statistics
- **Visualization Suite**: 20+ plots covering energy, trading, blockchain, and regulatory aspects

## Simulation Parameters (config.py)

| Parameter | Value | Description |
|-----------|-------|-------------|
| `NUM_PROSUMERS` | 100 | Number of prosumers in community |
| `TIME_STEPS` | 24 | Simulation duration (hours) |
| `PV_CAPACITY` | 2.5-7.0 kW | PV panel capacity range (10 types) |
| `BASE_CONSUMPTION` | 0.35-1.50 kWh | Hourly consumption range (10 types) |
| `HAS_BATTERY` | 80% | Percentage of prosumers with batteries |
| `BATTERY_CAPACITY` | 5-20 kWh | Battery capacity range (10 types) |
| `BATTERY_EFFICIENCY` | 95% | Round-trip charge/discharge efficiency |
| `BATTERY_MIN_SOC` | 10% | Minimum state of charge (reserve) |
| `BATTERY_MAX_SOC` | 95% | Maximum state of charge (protection) |
| `BASE_PRICE` | 0.15 €/kWh | Base energy price |
| `MAX_TRADE_CAP` | 3.0 kWh | Maximum trade per prosumer per timestep |
| `LOCAL_MARKET_FEE` | 0.03 €/kWh | Transaction fee for local market |
| `NUM_MINERS` | 15 | Number of blockchain miners |
| `DIFFICULTY_TARGET` | 3 | PoW difficulty (leading zeros) |
| `BLOCK_REWARD` | 0.1 € | Mining reward per block |
| `RENEWABLE_BONUS` | 0.02 €/kWh | Bonus for renewable self-consumption |
| `PENALTY_FOR_MARKET` | 0.02 €/kWh | Penalty for using local market |

## How to Run

### Prerequisites

```bash
# Python 3.8+ required
python --version

# Install dependencies
pip install pandas matplotlib seaborn numpy scipy
```

### Execution

```bash
# Navigate to project directory
cd /path/to/SmartGrids

# Run simulation (takes 1-2 minutes)
python main.py
```

### Simulation Flow

1. **Initialization** (timestep 0)
   - Create 100 prosumers with randomized home types
   - Initialize blockchain with genesis block
   - Setup CSV logging infrastructure

2. **Hourly Simulation Loop** (timesteps 1-24)
   - Generate PV production and consumption data
   - Update prosumer energy states
   - Execute battery management (charge/discharge)
   - Phase 1: Self-consumption optimization
   - Phase 2: P2P bilateral trading
   - Phase 3: Local market aggregation
   - Record trades on blockchain
   - Apply regulatory incentives/penalties
   - Log all metrics to CSV files

3. **Results Generation**
   - Save complete simulation data to `results/`
   - Generate 20+ visualization plots in `results/plots/`
   - Display summary statistics

### Output Files

**CSV Data Files** (in `results/`):
- `prosumer_energy.csv`: Energy states (PV, consumption, battery, imbalances)
- `prosumer_trading.csv`: Trading roles, prices, quantities
- `all_trades.csv`: Complete trade log with buyer/seller IDs
- `regulator_actions.csv`: Bonuses, penalties, bans
- `community_summary.csv`: Aggregated hourly statistics

**Visualization Plots** (in `results/plots/`):
- Community energy flows (generation, consumption, trading)
- Battery usage patterns and SOC distribution
- Trading activity (P2P vs market comparison)
- Price dynamics and imbalance trends
- Financial analysis (balances, penalties, bonuses)
- Blockchain statistics (mining activity, block distribution)
- Regulatory impact (ban patterns, renewable usage)
- Individual prosumer deep-dives (top/bottom performers)

## Example Results

**Community Metrics** (typical 24-hour simulation):
- Total PV generation: ~800-1000 kWh
- Total consumption: ~700-900 kWh
- P2P trades: 200-400 transactions
- Local market trades: 100-200 transactions
- Blocks mined: 10-20 blocks
- Prosumers banned: 2-5 at peak times
- Total renewable usage: 70-80%

**Blockchain Performance**:
- Average mining time: 20-60 seconds per block
- Transactions per block: 30-50 (near maximum)
- Mining reward distribution: ~Uniform across 15 miners
- Total fees collected: 2-5 €

## Technologies Used

- **Python 3.8+**: Core simulation engine
- **Pandas**: Time-series data management and CSV I/O
- **Matplotlib/Seaborn**: Comprehensive visualization
- **NumPy**: Numerical computations
- **SciPy**: Statistical analysis and forecasting
- **Hashlib**: SHA-256 for blockchain PoW
- **JSON**: Blockchain data serialization

## Academic Context

This project was developed for the **Smart Grids** course, demonstrating advanced concepts in:
- Decentralized energy systems
- Multi-agent simulation
- Blockchain applications in energy trading
- Regulatory mechanisms and incentive design
- Battery storage optimization
- Peer-to-peer market mechanisms

## Future Enhancements

Potential extensions for this simulation platform:
- Real-time network topology and transmission losses
- Machine learning for predictive prosumer behavior
- Time-of-use tariffs and dynamic pricing
- Electric vehicle integration
- Weather-based PV generation variability
- Prosumer coalition formation and strategic behavior
- Alternative consensus mechanisms (PoS, PBFT)
- Grid stability analysis and frequency regulation

## License

Academic project for educational purposes.
