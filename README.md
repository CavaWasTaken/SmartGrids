# Prosumer Community Energy Trading Simulator

A blockchain-based simulator for a prosumer community with self-organized energy trading.

## Project Structure

```
SmartGrids/
├── README.md
├── requirements.txt
├── SETUP_INSTRUCTIONS.md
├── config.py              # Configuration parameters
├── prosumer.py            # Prosumer class with decision logic
├── trading.py             # P2P and local market trading
├── blockchain.py          # Blockchain with PoW consensus
├── regulator.py           # Regulator with strategy
├── data_generation.py     # PV and price forecasting
├── simulator.py           # Main simulation orchestrator
├── visualization.py       # Results plotting
└── main.py               # Entry point
```

## Features

- **100 Prosumers** with individual PV generation and consumption
- **3-Step Energy Balancing**: Self-balancing → P2P Trading → Local Market
- **Self-Organized Trading**: Bilateral negotiations between prosumers
- **Blockchain**: Proof-of-Work with 10+ miners (difficulty: 3 leading zeros)
- **Regulator**: Strategy to maximize renewable energy usage
- **24-Hour Simulation**: Hourly time steps with realistic data

## Quick Start

See `SETUP_INSTRUCTIONS.md` for detailed installation steps.

```bash
# Install dependencies
pip install -r requirements.txt

# Run simulation
python main.py
```

## Output

- Console logs showing trading activity
- Blockchain state (blocks, transactions)
- Results saved to `results/` directory
- Visualization plots in `results/plots/`
