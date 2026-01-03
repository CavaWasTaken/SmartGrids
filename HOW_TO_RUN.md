# How to Run the Prosumer Community Simulator

## Quick Start Guide

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation (2 minutes)

1. **Open terminal and navigate to project directory:**
   ```bash
   cd /home/cavallinux/Backup/Magistrale/SmartGrids
   ```

2. **Install required packages:**
   ```bash
   pip install numpy matplotlib pandas
   ```
   
   Or use requirements file:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Simulation (30 seconds)

**Basic execution:**
```bash
python main.py
```

Or with Python 3 explicitly:
```bash
python3 main.py
```

### What Happens During Execution

The simulator will:
1. ✓ Initialize 100 prosumers with random PV/consumption characteristics
2. ✓ Simulate 24 hours of energy trading (24 timesteps)
3. ✓ Execute P2P trading between prosumers each hour
4. ✓ Execute local market trading for remaining imbalances
5. ✓ Mine blockchain blocks with Proof-of-Work
6. ✓ Apply regulator incentives and penalties
7. ✓ Generate final reports and visualizations

**Expected runtime**: 20-40 seconds (depending on system performance)

### Output Files

After completion, check the `results/` directory:

```
results/
├── blockchain.json          # Complete blockchain with all blocks
├── summary.json            # High-level simulation summary
├── prosumers.json          # Individual prosumer statistics
├── simulation_log.json     # Timestep-by-timestep log
└── plots/                  # Visualization charts
    ├── balance_distribution.png
    ├── trading_activity.png
    ├── price_forecast.png
    ├── p2p_vs_market.png
    ├── renewable_usage.png
    ├── top_prosumers.png
    └── blockchain_growth.png
```

### Viewing Results

**View plots:**
```bash
# Linux
xdg-open results/plots/trading_activity.png

# Mac
open results/plots/trading_activity.png

# Or use any image viewer
```

**View JSON results:**
```bash
# Pretty print blockchain
cat results/blockchain.json | python -m json.tool | less

# View summary
cat results/summary.json
```

**View all plots at once:**
```bash
ls results/plots/*.png | xargs xdg-open
```

## Customizing the Simulation

### Edit Configuration Parameters

Open `config.py` and modify parameters:

```python
# Change number of prosumers
NUM_PROSUMERS = 50  # Default: 100

# Change simulation duration
TIME_STEPS = 48  # Default: 24 (two days instead of one)

# Change blockchain difficulty (higher = slower but more secure)
DIFFICULTY_TARGET = 4  # Default: 3 (requires 4 leading zeros)

# Change regulator objective
REGULATOR_OBJECTIVE = "maximize_profit"  # Default: "maximize_renewable"
# Options: "maximize_renewable", "maximize_profit", "maximize_p2p"

# Enable/disable verbose output
VERBOSE = False  # Default: True (set to False for cleaner output)
```

### Run with Custom Config

After editing `config.py`:
```bash
python main.py
```

## Advanced Usage

### Run Multiple Simulations

Create a bash script to run multiple configurations:

```bash
#!/bin/bash
# run_multiple.sh

for obj in "maximize_renewable" "maximize_profit" "maximize_p2p"; do
    echo "Running with objective: $obj"
    sed -i "s/REGULATOR_OBJECTIVE = .*/REGULATOR_OBJECTIVE = \"$obj\"/" config.py
    python main.py
    mv results results_$obj
done
```

### Collect Specific Statistics

```python
# Add to main.py after simulation completes
print("\nCustom Statistics:")
for p in simulator.prosumers:
    if p.p2p_trades > 20:
        print(f"Active trader: Prosumer {p.id} - {p.p2p_trades} P2P trades")
```

## Troubleshooting

### Problem: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'numpy'
```

**Solution:**
```bash
pip install numpy matplotlib pandas
```

### Problem: Permission Denied on results/

```
PermissionError: [Errno 13] Permission denied: 'results'
```

**Solution:**
```bash
# Create directory with proper permissions
mkdir -p results/plots
chmod 755 results
```

### Problem: Simulation Too Slow

**Causes:**
- High number of prosumers (100+)
- High blockchain difficulty (4+)

**Solutions:**
1. Reduce prosumers in `config.py`:
   ```python
   NUM_PROSUMERS = 50
   ```

2. Reduce blockchain difficulty:
   ```python
   DIFFICULTY_TARGET = 2
   ```

3. Disable verbose output:
   ```python
   VERBOSE = False
   ```

### Problem: No Plots Generated

**Check:**
```bash
ls results/plots/
```

**Solution:**
If empty, matplotlib might not be properly installed:
```bash
pip uninstall matplotlib
pip install matplotlib
```

Or disable plot generation:
```python
# In config.py
GENERATE_PLOTS = False
```

## Testing Individual Components

### Test Prosumer Creation
```bash
python -c "from prosumer import Prosumer; p = Prosumer(1, 5.0, 2.0); print(p)"
```

### Test Blockchain
```bash
python -c "from blockchain import Blockchain; bc = Blockchain(); print(bc.is_chain_valid())"
```

### Test Data Generation
```bash
python -c "from data_generation import generate_pv_generation; print(generate_pv_generation(12, 5.0))"
```

## Performance Benchmarks

Expected performance on modern hardware:

| Configuration | Time | Blocks | Transactions |
|--------------|------|--------|--------------|
| 100 prosumers, 24h | 30s | ~13 | ~380 |
| 50 prosumers, 24h | 15s | ~7 | ~190 |
| 100 prosumers, 48h | 60s | ~26 | ~760 |

## Understanding the Output

### Console Output Explained

```
======================================================================
TIMESTEP 7 (Hour 7:00)
======================================================================
Price Forecast: €0.223/kWh          # Predicted electricity price
Total Surplus: 0.03 kWh              # Total energy available to sell
Total Deficit: 334.44 kWh            # Total energy needed to buy
Active Buyers: 99 | Active Sellers: 1

P2P Trading: 1 trades executed       # Peer-to-peer matches
  Total Energy: 0.03 kWh             # Energy traded in P2P
  Avg Price: €0.237/kWh              # Average P2P price

Local Market Trading: 0 trades       # Aggregator trades

⛏ Block #X mined                     # Blockchain update
  Hash: 000abc...                    # Hash with leading zeros
  (Nonce: 12345)                     # Proof-of-work solution
```

### Final Report Explained

```
💰 TOP 5 PROSUMERS (by balance)
  1. Prosumer 54: €11.38            # Final balance
     (P2P: 11,                      # Number of P2P trades
      Market: 0,                    # Number of market trades
      Renewable: 49.4 kWh)          # Self-consumed renewable energy
```

## For Presentation Demo

### Recommended Demo Flow

1. **Show configuration** (15 seconds):
   ```bash
   cat config.py | grep -E "NUM_PROSUMERS|TIME_STEPS|OBJECTIVE"
   ```

2. **Run simulation** (30 seconds):
   ```bash
   python main.py
   ```

3. **Show results directory** (10 seconds):
   ```bash
   tree results/  # or ls -R results/
   ```

4. **Display key plot** (20 seconds):
   ```bash
   xdg-open results/plots/trading_activity.png
   ```

5. **Show blockchain structure** (20 seconds):
   ```bash
   cat results/blockchain.json | python -m json.tool | head -50
   ```

**Total demo time**: ~2 minutes

## Support and Issues

If you encounter any issues:

1. Check Python version: `python --version` (should be 3.8+)
2. Verify all dependencies: `pip list | grep -E "numpy|matplotlib|pandas"`
3. Check file permissions: `ls -la`
4. Review error messages in terminal output

For the presentation, have a backup recording of the simulation run in case of technical difficulties.
