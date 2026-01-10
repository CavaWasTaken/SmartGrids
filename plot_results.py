"""
Visualization module for prosumer community simulation results
Generates comprehensive plots from CSV files
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class SimulationVisualizer:
    """Generate plots from simulation CSV results"""
    
    def __init__(self, results_dir='results'):
        """
        Initialize visualizer
        
        Args:
            results_dir: Directory containing CSV files
        """
        self.results_dir = results_dir
        self.plots_dir = os.path.join(results_dir, 'plots')
        
        # Create plots directory
        os.makedirs(self.plots_dir, exist_ok=True)
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load all CSV files"""
        print("Loading simulation data...")
        self.community_summary = pd.read_csv(
            os.path.join(self.results_dir, 'community_summary.csv'))
        self.prosumer_energy = pd.read_csv(
            os.path.join(self.results_dir, 'prosumer_energy.csv'))
        self.prosumer_trading = pd.read_csv(
            os.path.join(self.results_dir, 'prosumer_trading.csv'))
        self.all_trades = pd.read_csv(
            os.path.join(self.results_dir, 'all_trades.csv'))
        self.regulator_actions = pd.read_csv(
            os.path.join(self.results_dir, 'regulator_actions.csv'))
        
        print(f"Loaded {len(self.community_summary)} timesteps")
        print(f"Loaded {len(self.all_trades)} trades")
        print(f"Loaded data for {self.prosumer_energy['Prosumer_ID'].nunique()} prosumers")
    
    def plot_energy_balance(self):
        """Plot community energy generation and consumption"""
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # Plot 1: Generation vs Consumption
        ax1 = axes[0]
        ax1.plot(self.community_summary['Hour'], 
                self.community_summary['Total_PV_Generation_kWh'],
                label='PV Generation', color='orange', linewidth=2.5, marker='o')
        ax1.plot(self.community_summary['Hour'], 
                self.community_summary['Total_Consumption_kWh'],
                label='Consumption', color='blue', linewidth=2.5, marker='s')
        ax1.fill_between(self.community_summary['Hour'], 
                         self.community_summary['Total_PV_Generation_kWh'],
                         alpha=0.3, color='orange')
        ax1.fill_between(self.community_summary['Hour'], 
                         self.community_summary['Total_Consumption_kWh'],
                         alpha=0.3, color='blue')
        ax1.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Energy (kWh)', fontsize=12, fontweight='bold')
        ax1.set_title('Community Energy Balance Over 24 Hours', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(range(0, 24))
        
        # Plot 2: Surplus vs Deficit
        ax2 = axes[1]
        ax2.bar(self.community_summary['Hour'], 
               self.community_summary['Total_Surplus_kWh'],
               label='Surplus (Sellers)', color='green', alpha=0.7, width=0.8)
        ax2.bar(self.community_summary['Hour'], 
               -self.community_summary['Total_Deficit_kWh'],
               label='Deficit (Buyers)', color='red', alpha=0.7, width=0.8)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax2.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Energy Imbalance (kWh)', fontsize=12, fontweight='bold')
        ax2.set_title('Community Energy Surplus and Deficit', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.set_xticks(range(0, 24))
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, 'energy_balance.png'), dpi=300, bbox_inches='tight')
        print("Generated: energy_balance.png")
        plt.close()
    
    def plot_trading_activity(self):
        """Plot P2P vs market trading activity"""
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # Plot 1: Trade counts
        ax1 = axes[0]
        width = 0.35
        x = np.arange(len(self.community_summary))
        
        bars1 = ax1.bar(x - width/2, self.community_summary['P2P_Trades_Count'],
                       width, label='P2P Trades', color='#2ecc71', alpha=0.8)
        bars2 = ax1.bar(x + width/2, self.community_summary['Market_Trades_Count'],
                       width, label='Market Trades', color='#e74c3c', alpha=0.8)
        
        ax1.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Number of Trades', fontsize=12, fontweight='bold')
        ax1.set_title('P2P vs Local Market Trading Activity', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(self.community_summary['Hour'])
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Plot 2: Active participants
        ax2 = axes[1]
        ax2.plot(self.community_summary['Hour'], 
                self.community_summary['Active_Buyers'],
                label='Active Buyers', color='#3498db', linewidth=2.5, marker='o')
        ax2.plot(self.community_summary['Hour'], 
                self.community_summary['Active_Sellers'],
                label='Active Sellers', color='#f39c12', linewidth=2.5, marker='s')
        ax2.fill_between(self.community_summary['Hour'], 
                         self.community_summary['Active_Buyers'],
                         alpha=0.2, color='#3498db')
        ax2.fill_between(self.community_summary['Hour'], 
                         self.community_summary['Active_Sellers'],
                         alpha=0.2, color='#f39c12')
        ax2.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Number of Prosumers', fontsize=12, fontweight='bold')
        ax2.set_title('Active Market Participants', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(range(0, 24))
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, 'trading_activity.png'), dpi=300, bbox_inches='tight')
        print("Generated: trading_activity.png")
        plt.close()
    
    def plot_price_dynamics(self):
        """Plot price forecasts and trade prices"""
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # Plot 1: Price forecast over time
        ax1 = axes[0]
        ax1.plot(self.community_summary['Hour'], 
                self.community_summary['Price_Forecast_Euro_kWh'],
                color='#9b59b6', linewidth=3, marker='D', markersize=8)
        ax1.fill_between(self.community_summary['Hour'], 
                         self.community_summary['Price_Forecast_Euro_kWh'],
                         alpha=0.3, color='#9b59b6')
        ax1.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Price (€/kWh)', fontsize=12, fontweight='bold')
        ax1.set_title('Electricity Price Forecast', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(range(0, 24))
        
        # Plot 2: P2P vs Local Market trade prices comparison
        ax2 = axes[1]
        p2p_trades = self.all_trades[self.all_trades['Trade_Type'] == 'p2p']
        market_trades = self.all_trades[self.all_trades['Trade_Type'] == 'local_market']
        
        if len(p2p_trades) > 0:
            # Group by hour and calculate statistics
            hourly_p2p_prices = p2p_trades.groupby('Hour')['Price_Euro_kWh'].agg(['mean', 'min', 'max'])
            
            ax2.plot(hourly_p2p_prices.index, hourly_p2p_prices['mean'], 
                    color='#2ecc71', linewidth=2.5, marker='o', markersize=7, label='Avg P2P Price')
            ax2.fill_between(hourly_p2p_prices.index, hourly_p2p_prices['min'], hourly_p2p_prices['max'],
                            alpha=0.2, color='#2ecc71', label='P2P Price Range')
        
        # Show local market buy and sell prices separately
        from config import LOCAL_MARKET_FEE
        grid_prices = self.community_summary['Price_Forecast_Euro_kWh'].values
        hours = self.community_summary['Hour'].values
        
        # Local market buy price (what buyers pay)
        market_buy_price = grid_prices + LOCAL_MARKET_FEE
        ax2.plot(hours, market_buy_price,
                color='#e74c3c', linewidth=2.5, marker='s', markersize=6, 
                label='Local Market (Buy)', linestyle='-', alpha=0.8)
        
        # Local market sell price (what sellers receive)
        market_sell_price = grid_prices - LOCAL_MARKET_FEE
        ax2.plot(hours, market_sell_price,
                color='#e67e22', linewidth=2.5, marker='v', markersize=6,
                label='Local Market (Sell)', linestyle='-', alpha=0.8)
        
        # Grid base price (reference)
        ax2.plot(hours, grid_prices,
                color='#9b59b6', linewidth=2, linestyle='--', alpha=0.7, label='Grid Base Price')
        
        ax2.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Price (€/kWh)', fontsize=12, fontweight='bold')
        ax2.set_title('P2P vs Local Market vs Grid Prices', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10, loc='best')
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(range(0, 24))
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, 'price_dynamics.png'), dpi=300, bbox_inches='tight')
        print("Generated: price_dynamics.png")
        plt.close()
    
    def plot_battery_usage(self):
        """Plot battery charging and discharging patterns"""
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # Aggregate battery data by hour
        battery_data = self.prosumer_energy[self.prosumer_energy['Battery_Capacity_kWh'] > 0]
        hourly_battery = battery_data.groupby('Hour').agg({
            'Battery_Charged_kWh': 'sum',
            'Battery_Discharged_kWh': 'sum',
            'Battery_SOC_%': 'mean'
        }).reset_index()
        
        # Plot 1: Charging and Discharging
        ax1 = axes[0]
        ax1.bar(hourly_battery['Hour'], hourly_battery['Battery_Charged_kWh'],
               label='Charged', color='#2ecc71', alpha=0.7, width=0.8)
        ax1.bar(hourly_battery['Hour'], -hourly_battery['Battery_Discharged_kWh'],
               label='Discharged', color='#e74c3c', alpha=0.7, width=0.8)
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax1.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Energy (kWh)', fontsize=12, fontweight='bold')
        ax1.set_title('Community Battery Charging and Discharging', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.set_xticks(range(0, 24))
        
        # Plot 2: Average State of Charge
        ax2 = axes[1]
        ax2.plot(hourly_battery['Hour'], hourly_battery['Battery_SOC_%'],
                color='#3498db', linewidth=3, marker='o', markersize=8)
        ax2.fill_between(hourly_battery['Hour'], hourly_battery['Battery_SOC_%'],
                         alpha=0.3, color='#3498db')
        ax2.axhline(y=50, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='50% SOC')
        ax2.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Average State of Charge (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Average Battery State of Charge', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(range(0, 24))
        ax2.set_ylim([0, 100])
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, 'battery_usage.png'), dpi=300, bbox_inches='tight')
        print("Generated: battery_usage.png")
        plt.close()
    
    def plot_prosumer_performance(self):
        """Plot prosumer financial performance"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Get final state for each prosumer
        final_state = self.prosumer_energy.groupby('Prosumer_ID').last().reset_index()
        final_trading = self.prosumer_trading.groupby('Prosumer_ID').last().reset_index()
        
        # Merge data
        prosumer_summary = final_state.merge(final_trading, on='Prosumer_ID')
        
        # Sort by balance
        prosumer_summary = prosumer_summary.sort_values('Balance_Euro', ascending=False)
        
        # Plot 1: Top and Bottom 10 prosumers by balance
        ax1 = axes[0, 0]
        top_bottom = pd.concat([prosumer_summary.head(10), prosumer_summary.tail(10)])
        colors = ['green' if x > 0 else 'red' for x in top_bottom['Balance_Euro']]
        ax1.barh(range(len(top_bottom)), top_bottom['Balance_Euro'], color=colors, alpha=0.7)
        ax1.set_yticks(range(len(top_bottom)))
        ax1.set_yticklabels([f"P{int(x)}" for x in top_bottom['Prosumer_ID']], fontsize=8)
        ax1.set_xlabel('Balance (€)', fontsize=11, fontweight='bold')
        ax1.set_title('Top 10 & Bottom 10 Prosumers by Balance', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        ax1.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        
        # Plot 2: Renewable usage distribution
        ax2 = axes[0, 1]
        ax2.hist(prosumer_summary['Renewable_Usage_kWh'], bins=30, color='#2ecc71', alpha=0.7, edgecolor='black')
        ax2.set_xlabel('Renewable Usage (kWh)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Number of Prosumers', fontsize=11, fontweight='bold')
        ax2.set_title('Distribution of Renewable Energy Usage', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.axvline(x=prosumer_summary['Renewable_Usage_kWh'].mean(), 
                   color='red', linestyle='--', linewidth=2, label='Mean')
        ax2.legend()
        
        # Plot 3: P2P vs Market trades scatter
        ax3 = axes[1, 0]
        scatter = ax3.scatter(prosumer_summary['P2P_Trades_Count'], 
                             prosumer_summary['Market_Trades_Count'],
                             c=prosumer_summary['Balance_Euro'], 
                             cmap='RdYlGn', s=100, alpha=0.6, edgecolors='black')
        ax3.set_xlabel('P2P Trades', fontsize=11, fontweight='bold')
        ax3.set_ylabel('Market Trades', fontsize=11, fontweight='bold')
        ax3.set_title('Trading Behavior (color = balance)', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax3, label='Balance (€)')
        
        # Plot 4: Balance vs Renewable Usage
        ax4 = axes[1, 1]
        ax4.scatter(prosumer_summary['Renewable_Usage_kWh'], 
                   prosumer_summary['Balance_Euro'],
                   c='#3498db', s=100, alpha=0.6, edgecolors='black')
        ax4.set_xlabel('Renewable Usage (kWh)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('Balance (€)', fontsize=11, fontweight='bold')
        ax4.set_title('Financial Performance vs Renewable Usage', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        ax4.axhline(y=0, color='red', linestyle='--', linewidth=1)
        
        # Add trend line
        z = np.polyfit(prosumer_summary['Renewable_Usage_kWh'], 
                      prosumer_summary['Balance_Euro'], 1)
        p = np.poly1d(z)
        ax4.plot(prosumer_summary['Renewable_Usage_kWh'], 
                p(prosumer_summary['Renewable_Usage_kWh']), 
                "r--", linewidth=2, alpha=0.8, label='Trend')
        ax4.legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, 'prosumer_performance.png'), dpi=300, bbox_inches='tight')
        print("Generated: prosumer_performance.png")
        plt.close()
    
    def plot_regulator_impact(self):
        """Plot regulator bonuses and penalties"""
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # Aggregate by hour
        hourly_regulator = self.regulator_actions.groupby('Hour').agg({
            'Bonus_Euro': 'sum',
            'Penalties_Euro': 'sum',
            'Is_Banned': 'sum'
        }).reset_index()
        
        # Plot 1: Bonuses and Penalties
        ax1 = axes[0]
        width = 0.35
        x = np.arange(len(hourly_regulator))
        
        ax1.bar(x - width/2, hourly_regulator['Bonus_Euro'],
               width, label='Bonuses', color='#2ecc71', alpha=0.8)
        ax1.bar(x + width/2, hourly_regulator['Penalties_Euro'],
               width, label='Penalties', color='#e74c3c', alpha=0.8)
        
        ax1.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Amount (€)', fontsize=12, fontweight='bold')
        ax1.set_title('Regulator Incentives and Penalties', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(hourly_regulator['Hour'])
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Plot 2: Banned prosumers
        ax2 = axes[1]
        ax2.bar(hourly_regulator['Hour'], hourly_regulator['Is_Banned'],
               color='#e74c3c', alpha=0.7, width=0.8)
        ax2.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Number of Banned Prosumers', fontsize=12, fontweight='bold')
        ax2.set_title('Banned Prosumers Over Time', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.set_xticks(range(0, 24))
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, 'regulator_impact.png'), dpi=300, bbox_inches='tight')
        print("Generated: regulator_impact.png")
        plt.close()
    
    def plot_trade_volume_analysis(self):
        """Plot trade volume and energy flow analysis"""
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # Calculate hourly trade volumes
        hourly_trades = self.all_trades.groupby(['Hour', 'Trade_Type']).agg({
            'Quantity_kWh': 'sum'
        }).reset_index()
        
        # Pivot for easier plotting
        trade_pivot = hourly_trades.pivot(index='Hour', columns='Trade_Type', values='Quantity_kWh').fillna(0)
        
        # Plot 1: Stacked area chart of energy traded
        ax1 = axes[0]
        if 'p2p' in trade_pivot.columns:
            ax1.fill_between(trade_pivot.index, 0, trade_pivot['p2p'],
                           label='P2P Energy', color='#2ecc71', alpha=0.7)
            ax1.fill_between(trade_pivot.index, trade_pivot['p2p'], 
                           trade_pivot['p2p'] + trade_pivot.get('local_market', 0),
                           label='Market Energy', color='#e74c3c', alpha=0.7)
        
        ax1.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Energy Traded (kWh)', fontsize=12, fontweight='bold')
        ax1.set_title('Energy Trading Volume by Type', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(range(0, 24))
        
        # Plot 2: P2P efficiency (P2P / Total)
        ax2 = axes[1]
        total_trades = trade_pivot.sum(axis=1)
        p2p_ratio = (trade_pivot.get('p2p', 0) / total_trades * 100).fillna(0)
        
        ax2.plot(p2p_ratio.index, p2p_ratio, color='#2ecc71', linewidth=3, marker='o', markersize=8)
        ax2.fill_between(p2p_ratio.index, p2p_ratio, alpha=0.3, color='#2ecc71')
        ax2.axhline(y=50, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='50% P2P')
        ax2.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax2.set_ylabel('P2P Share (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Percentage of Energy Traded via P2P', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(range(0, 24))
        ax2.set_ylim([0, 100])
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, 'trade_volume_analysis.png'), dpi=300, bbox_inches='tight')
        print("Generated: trade_volume_analysis.png")
        plt.close()
    
    def plot_home_type_analysis(self):
        """Plot characteristics and behavior analysis by home type"""
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)
        
        # Get final state for each prosumer
        final_state = self.prosumer_energy.groupby('Prosumer_ID').last().reset_index()
        final_trading = self.prosumer_trading.groupby('Prosumer_ID').last().reset_index()
        
        # Merge data - use suffixes to handle duplicate columns
        prosumer_summary = final_state.merge(final_trading, on='Prosumer_ID', suffixes=('', '_trading'))
        
        # Get home type from first timestep
        first_state = self.prosumer_energy.groupby('Prosumer_ID').first().reset_index()
        prosumer_summary = prosumer_summary.merge(first_state[['Prosumer_ID', 'Home_Type_Index']], 
                                                   on='Prosumer_ID', how='left', suffixes=('', '_first'))
        # Use Home_Type_Index_first if the merge created duplicates, otherwise use existing
        if 'Home_Type_Index_first' in prosumer_summary.columns:
            prosumer_summary['Home_Type_Index'] = prosumer_summary['Home_Type_Index_first']
            prosumer_summary.drop(columns=['Home_Type_Index_first'], inplace=True)
        
        # Calculate daily totals per prosumer
        daily_consumption = self.prosumer_energy.groupby('Prosumer_ID')['Consumption_kWh'].sum()
        prosumer_summary['Daily_Consumption_kWh'] = prosumer_summary['Prosumer_ID'].map(daily_consumption)
        
        # Map home type to actual config values
        from config import PV_CAPACITY, BATTERY_CAPACITY
        prosumer_summary['PV_Capacity_kW'] = prosumer_summary['Home_Type_Index'].apply(lambda x: PV_CAPACITY[x])
        
        # Group by home type
        home_type_stats = prosumer_summary.groupby('Home_Type_Index').agg({
            'PV_Capacity_kW': 'mean',
            'Daily_Consumption_kWh': 'mean',
            'Battery_Capacity_kWh': 'mean',
            'Balance_Euro': 'mean',
            'Renewable_Usage_kWh': 'mean',
            'P2P_Trades_Count': 'mean',
            'Market_Trades_Count': 'sum',
            'Prosumer_ID': 'count'
        }).reset_index()
        home_type_stats.rename(columns={'Prosumer_ID': 'Count'}, inplace=True)
        
        # Calculate additional metrics
        home_type_stats['Avg_P2P_Ratio'] = home_type_stats['P2P_Trades_Count'] / (
            home_type_stats['P2P_Trades_Count'] + home_type_stats['Market_Trades_Count'] / home_type_stats['Count']
        )
        
        # Plot 1: Home Type Configurations (PV, Battery, Consumption) - Dual Y-axis
        ax1 = fig.add_subplot(gs[0, :])
        ax1_right = ax1.twinx()
        
        x = home_type_stats['Home_Type_Index']
        width = 0.28
        
        # Left Y-axis: PV and Consumption (smaller values)
        ax1.bar(x - width/2, home_type_stats['PV_Capacity_kW'], width, 
                label='PV Capacity (kW)', color='#f39c12', alpha=0.8)
        ax1.bar(x + width/2, home_type_stats['Daily_Consumption_kWh'], width,
                label='Daily Consumption (kWh/day)', color='#3498db', alpha=0.8)
        
        # Right Y-axis: Battery Capacity (larger values)
        ax1_right.bar(x, home_type_stats['Battery_Capacity_kWh'], width*0.6,
                label='Battery Capacity (kWh)', color='#2ecc71', alpha=0.7, edgecolor='darkgreen', linewidth=1.5)
        
        ax1.set_xlabel('Home Type Index', fontsize=12, fontweight='bold')
        ax1.set_ylabel('PV (kW) / Consumption (kWh/day)', fontsize=11, fontweight='bold', color='black')
        ax1_right.set_ylabel('Battery (kWh)', fontsize=11, fontweight='bold', color='#2ecc71')
        ax1.set_title('Home Type Configurations: PV, Battery & Consumption Capacity', 
                     fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1_right.tick_params(axis='y', labelcolor='#2ecc71')
        
        # Combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax1_right.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=10, loc='upper left', ncol=3)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Plot 2: Battery Distribution by Home Type
        ax2 = fig.add_subplot(gs[1, 0])
        
        # Calculate prosumers with and without batteries per home type
        battery_dist = prosumer_summary.groupby('Home_Type_Index').agg({
            'Battery_Capacity_kWh': lambda x: (x > 0).sum(),  # Count with battery
            'Prosumer_ID': 'count'  # Total count
        }).reset_index()
        battery_dist['Without_Battery'] = battery_dist['Prosumer_ID'] - battery_dist['Battery_Capacity_kWh']
        battery_dist.rename(columns={'Battery_Capacity_kWh': 'With_Battery'}, inplace=True)
        
        x_pos = np.arange(len(battery_dist))
        ax2.bar(x_pos, battery_dist['With_Battery'], 0.6,
                label='With Battery', color='#2ecc71', alpha=0.8, edgecolor='black')
        ax2.bar(x_pos, battery_dist['Without_Battery'], 0.6,
                bottom=battery_dist['With_Battery'],
                label='Without Battery', color='#95a5a6', alpha=0.8, edgecolor='black')
        
        ax2.set_xlabel('Home Type Index', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Number of Prosumers', fontsize=11, fontweight='bold')
        ax2.set_title('Battery Distribution by Home Type', fontsize=12, fontweight='bold')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(battery_dist['Home_Type_Index'])
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.legend(fontsize=9, loc='upper left')
        
        # Plot 3: Average Balance by Home Type
        ax3 = fig.add_subplot(gs[1, 1])
        colors_balance = ['green' if x > 0 else 'red' for x in home_type_stats['Balance_Euro']]
        ax3.barh(home_type_stats['Home_Type_Index'], home_type_stats['Balance_Euro'],
                color=colors_balance, alpha=0.7, edgecolor='black')
        ax3.set_ylabel('Home Type Index', fontsize=11, fontweight='bold')
        ax3.set_xlabel('Average Balance (€)', fontsize=11, fontweight='bold')
        ax3.set_title('Financial Performance by Home Type', fontsize=12, fontweight='bold')
        ax3.axvline(x=0, color='black', linestyle='-', linewidth=1)
        ax3.grid(True, alpha=0.3, axis='x')
        ax3.set_yticks(home_type_stats['Home_Type_Index'])
        
        # Plot 4: Renewable Usage by Home Type
        ax4 = fig.add_subplot(gs[1, 2])
        ax4.bar(home_type_stats['Home_Type_Index'], home_type_stats['Renewable_Usage_kWh'],
                color='#27ae60', alpha=0.7, edgecolor='black')
        ax4.set_xlabel('Home Type Index', fontsize=11, fontweight='bold')
        ax4.set_ylabel('Renewable Usage (kWh)', fontsize=11, fontweight='bold')
        ax4.set_title('Renewable Energy Usage', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        ax4.set_xticks(home_type_stats['Home_Type_Index'])
        
        # Plot 5: Trading Activity by Home Type
        ax5 = fig.add_subplot(gs[2, 0])
        x_pos = np.arange(len(home_type_stats))
        ax5.bar(x_pos - 0.2, home_type_stats['P2P_Trades_Count'], 0.4,
                label='Avg P2P Trades', color='#2ecc71', alpha=0.8)
        ax5.bar(x_pos + 0.2, home_type_stats['Market_Trades_Count'] / home_type_stats['Count'], 0.4,
                label='Avg Market Trades', color='#e74c3c', alpha=0.8)
        ax5.set_xlabel('Home Type Index', fontsize=11, fontweight='bold')
        ax5.set_ylabel('Average Trades per Prosumer', fontsize=11, fontweight='bold')
        ax5.set_title('Trading Activity by Home Type', fontsize=12, fontweight='bold')
        ax5.set_xticks(x_pos)
        ax5.set_xticklabels(home_type_stats['Home_Type_Index'])
        ax5.legend(fontsize=9)
        ax5.grid(True, alpha=0.3, axis='y')

        # Plot 6: P2P Ratio by Home Type
        ax6 = fig.add_subplot(gs[2, 1])
        p2p_ratio_pct = home_type_stats['Avg_P2P_Ratio'] * 100
        ax6.bar(home_type_stats['Home_Type_Index'], p2p_ratio_pct,
                color='#8e44ad', alpha=0.7, edgecolor='black')
        ax6.set_xlabel('Home Type Index', fontsize=11, fontweight='bold')
        ax6.set_ylabel('Average P2P Ratio (%)', fontsize=11, fontweight='bold')
        ax6.set_title('Average P2P Trade Ratio by Home Type', fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='y')
        ax6.set_xticks(home_type_stats['Home_Type_Index'])
        ax6.set_ylim([0, 100])
        ax6.legend(['P2P Ratio (%)'], fontsize=9)
        
        # Plot 7: Scatter - Balance vs Renewable Usage
        ax7 = fig.add_subplot(gs[2, 2])
        scatter = ax7.scatter(home_type_stats['Renewable_Usage_kWh'], 
                             home_type_stats['Balance_Euro'],
                             s=home_type_stats['Count']*20,
                             c=home_type_stats['Home_Type_Index'],
                             cmap='viridis', alpha=0.6, edgecolors='black', linewidth=2)
        
        # Add labels for each home type
        for idx, row in home_type_stats.iterrows():
            ax7.annotate(f"HT{int(row['Home_Type_Index'])}", 
                        (row['Renewable_Usage_kWh'], row['Balance_Euro']),
                        fontsize=9, fontweight='bold', ha='center')
        
        ax7.set_xlabel('Renewable Usage (kWh)', fontsize=11, fontweight='bold')
        ax7.set_ylabel('Average Balance (€)', fontsize=11, fontweight='bold')
        ax7.set_title('Balance vs Renewable Usage\n(size = prosumer count)', 
                     fontsize=12, fontweight='bold')
        ax7.grid(True, alpha=0.3)
        ax7.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
        
        plt.colorbar(scatter, ax=ax7, label='Home Type Index')
        
        plt.savefig(os.path.join(self.plots_dir, 'home_type_analysis.png'), dpi=300, bbox_inches='tight')
        print("Generated: home_type_analysis.png")
        plt.close()
    
    def generate_all_plots(self):
        """Generate all visualization plots"""
        print("\n" + "="*70)
        print("GENERATING VISUALIZATION PLOTS")
        print("="*70 + "\n")
        
        self.plot_energy_balance()
        self.plot_trading_activity()
        self.plot_price_dynamics()
        self.plot_battery_usage()
        self.plot_prosumer_performance()
        self.plot_regulator_impact()
        self.plot_trade_volume_analysis()
        self.plot_home_type_analysis()
        
        print("\n" + "="*70)
        print(f"ALL PLOTS SAVED TO: {self.plots_dir}")
        print("="*70 + "\n")


def main():
    """Main function to generate plots"""
    visualizer = SimulationVisualizer()
    visualizer.generate_all_plots()


if __name__ == "__main__":
    main()
