# Setup Instructions

## Requirements

- Python 3.8 or higher
- pip package manager

## Installation Steps

1. **Navigate to project directory**
   ```bash
   cd /path/to/SmartGrids
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # OR
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Simulator

**Basic run:**
```bash
python main.py
```

**With custom parameters:**
Edit `config.py` to adjust:
- Number of prosumers
- Simulation duration
- Blockchain difficulty
- Regulator strategy parameters

## Output

Results will be saved in:
- `results/simulation_log.txt` - Detailed logs
- `results/blockchain.json` - Final blockchain state
- `results/summary.json` - Simulation summary
- `results/plots/` - Visualization charts

## Troubleshooting

- **ImportError**: Make sure all dependencies are installed with `pip install -r requirements.txt`
- **Permission errors**: Ensure the `results/` directory can be created
- **Slow execution**: Reduce number of prosumers or time steps in `config.py`
