"""
Visualization and results export utilities
"""
import json
import os
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict


def save_results(simulation_data: dict, results_dir: str = "results"):
    """
    Save simulation results to files
    
    Args:
        simulation_data: Dictionary with all simulation data
        results_dir: Directory to save results
    """
    # Create results directory if it doesn't exist
    os.makedirs(results_dir, exist_ok=True)
    
    # Save blockchain
    blockchain_path = os.path.join(results_dir, "blockchain.json")
    with open(blockchain_path, 'w') as f:
        json.dump(simulation_data['blockchain'], f, indent=2)
    print(f"✓ Blockchain saved to {blockchain_path}")
    
    # Save summary
    summary_data = {
        'config': simulation_data['config'],
        'regulator': simulation_data['regulator'],
        'prosumer_summary': {
            'total_prosumers': len(simulation_data['prosumers']),
            'total_balance': sum(p['balance'] for p in simulation_data['prosumers']),
            'total_renewable_usage': sum(p['renewable_usage'] for p in simulation_data['prosumers']),
            'total_p2p_trades': sum(p['p2p_trades'] for p in simulation_data['prosumers']),
            'total_market_trades': sum(p['market_trades'] for p in simulation_data['prosumers'])
        }
    }
    
    summary_path = os.path.join(results_dir, "summary.json")
    with open(summary_path, 'w') as f:
        json.dump(summary_data, f, indent=2)
    print(f"✓ Summary saved to {summary_path}")
    
    # Save prosumer details
    prosumers_path = os.path.join(results_dir, "prosumers.json")
    with open(prosumers_path, 'w') as f:
        json.dump(simulation_data['prosumers'], f, indent=2)
    print(f"✓ Prosumer data saved to {prosumers_path}")
    
    # Save simulation log
    log_path = os.path.join(results_dir, "simulation_log.json")
    with open(log_path, 'w') as f:
        json.dump(simulation_data['simulation_log'], f, indent=2)
    print(f"✓ Simulation log saved to {log_path}")


def generate_plots(simulation_data: dict, results_dir: str = "results"):
    """
    Generate visualization plots
    
    Args:
        simulation_data: Dictionary with all simulation data
        results_dir: Directory to save plots
    """
    plots_dir = os.path.join(results_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    # Extract data
    prosumers = simulation_data['prosumers']
    sim_log = simulation_data['simulation_log']
    
    # 1. Prosumer balance distribution
    plt.figure(figsize=(10, 6))
    balances = [p['balance'] for p in prosumers]
    plt.hist(balances, bins=30, color='skyblue', edgecolor='black')
    plt.xlabel('Balance (€)')
    plt.ylabel('Number of Prosumers')
    plt.title('Prosumer Balance Distribution')
    plt.axvline(np.mean(balances), color='red', linestyle='--', 
                label=f'Mean: €{np.mean(balances):.2f}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "balance_distribution.png"), dpi=300)
    plt.close()
    print(f"✓ Balance distribution plot saved")
    
    # 2. Trading activity over time
    plt.figure(figsize=(12, 6))
    timesteps = [log['timestep'] for log in sim_log]
    p2p_trades = [log['p2p_trades'] for log in sim_log]
    market_trades = [log['market_trades'] for log in sim_log]
    
    plt.plot(timesteps, p2p_trades, label='P2P Trades', marker='o', linewidth=2)
    plt.plot(timesteps, market_trades, label='Local Market Trades', marker='s', linewidth=2)
    plt.xlabel('Time Step (Hour)')
    plt.ylabel('Number of Trades')
    plt.title('Trading Activity Over Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "trading_activity.png"), dpi=300)
    plt.close()
    print(f"✓ Trading activity plot saved")
    
    # 3. Price forecast over time
    plt.figure(figsize=(12, 6))
    prices = [log['price_forecast'] for log in sim_log]
    plt.plot(timesteps, prices, color='green', marker='o', linewidth=2)
    plt.xlabel('Time Step (Hour)')
    plt.ylabel('Price (€/kWh)')
    plt.title('Electricity Price Forecast Over 24 Hours')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "price_forecast.png"), dpi=300)
    plt.close()
    print(f"✓ Price forecast plot saved")
    
    # 4. P2P vs Market trades comparison
    plt.figure(figsize=(10, 6))
    total_p2p = sum(p['p2p_trades'] for p in prosumers)
    total_market = sum(p['market_trades'] for p in prosumers)
    
    labels = ['P2P Trades', 'Local Market Trades']
    values = [total_p2p, total_market]
    colors = ['#4CAF50', '#FF9800']
    
    plt.bar(labels, values, color=colors, edgecolor='black', linewidth=2)
    plt.ylabel('Total Number of Trades')
    plt.title('P2P vs Local Market Trading Volume')
    plt.grid(True, axis='y', alpha=0.3)
    
    for i, v in enumerate(values):
        plt.text(i, v + max(values)*0.02, str(v), ha='center', va='bottom', 
                fontweight='bold', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "p2p_vs_market.png"), dpi=300)
    plt.close()
    print(f"✓ P2P vs Market comparison plot saved")
    
    # 5. Renewable energy usage
    plt.figure(figsize=(10, 6))
    renewable_usage = [p['renewable_usage'] for p in prosumers]
    plt.hist(renewable_usage, bins=30, color='lightgreen', edgecolor='black')
    plt.xlabel('Renewable Energy Usage (kWh)')
    plt.ylabel('Number of Prosumers')
    plt.title('Renewable Energy Self-Consumption Distribution')
    plt.axvline(np.mean(renewable_usage), color='darkgreen', linestyle='--', 
                label=f'Mean: {np.mean(renewable_usage):.2f} kWh')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "renewable_usage.png"), dpi=300)
    plt.close()
    print(f"✓ Renewable usage plot saved")
    
    # 6. Top 10 prosumers by balance
    plt.figure(figsize=(12, 6))
    sorted_prosumers = sorted(prosumers, key=lambda x: x['balance'], reverse=True)[:10]
    prosumer_ids = [f"P{p['id']}" for p in sorted_prosumers]
    prosumer_balances = [p['balance'] for p in sorted_prosumers]
    
    colors_top = ['green' if b > 0 else 'red' for b in prosumer_balances]
    plt.bar(prosumer_ids, prosumer_balances, color=colors_top, edgecolor='black')
    plt.xlabel('Prosumer ID')
    plt.ylabel('Balance (€)')
    plt.title('Top 10 Prosumers by Final Balance')
    plt.xticks(rotation=45)
    plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "top_prosumers.png"), dpi=300)
    plt.close()
    print(f"✓ Top prosumers plot saved")
    
    # 7. Blockchain growth
    plt.figure(figsize=(12, 6))
    blocks = [log['blockchain_blocks'] for log in sim_log]
    plt.plot(timesteps, blocks, color='purple', marker='o', linewidth=2)
    plt.xlabel('Time Step (Hour)')
    plt.ylabel('Number of Blocks')
    plt.title('Blockchain Growth Over Time')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "blockchain_growth.png"), dpi=300)
    plt.close()
    print(f"✓ Blockchain growth plot saved")
    
    print(f"\n✓ All plots saved to {plots_dir}/")
