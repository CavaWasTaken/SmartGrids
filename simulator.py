"""
Main simulator orchestrating the prosumer community energy trading
"""
import random
import csv
import os
from typing import List
from prosumer import Prosumer
from trading import P2PTradingMechanism, LocalMarketMechanism, Trade
from blockchain import Blockchain
from regulator import Regulator
from data_generation import generate_pv_generation, generate_consumption, forecast_price
import config
from plot_results import SimulationVisualizer

class CommunitySimulator:
    """
    Main simulator for the prosumer community
    """
    
    def __init__(self):
        """Initialize the simulator with all components"""
        self.prosumers = []
        self.p2p_mechanism = P2PTradingMechanism()
        self.local_market = LocalMarketMechanism(
            aggregator_id=-1,
            transaction_fee=config.LOCAL_MARKET_FEE
        )
        self.blockchain = Blockchain(
            difficulty=config.DIFFICULTY_TARGET,
            num_miners=config.NUM_MINERS,
            block_reward=config.BLOCK_REWARD,
            max_transactions_per_block=config.MAX_TRANSACTIONS_PER_BLOCK
        )
        self.regulator = Regulator(objective=config.REGULATOR_OBJECTIVE)
        
        self.current_timestep = 0
        self.simulation_log = []
        
        # Create results directory
        os.makedirs("results", exist_ok=True)
        
        # Initialize CSV logging
        self._initialize_csv_logs()
        
    def _initialize_csv_logs(self):
        """Initialize CSV files for efficient time-series logging"""
        # Prosumer energy states CSV
        with open("results/prosumer_energy.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestep", "Hour", "Prosumer_ID", "Home_Type_Index", "PV_Generation_kWh", "Consumption_kWh",
                "Battery_Level_kWh", "Battery_Capacity_kWh", "Battery_SOC_%",
                "Battery_Charged_kWh", "Battery_Discharged_kWh",
                "Imbalance_Before_P2P_kWh", "Imbalance_After_P2P_kWh", 
                "Imbalance_After_Market_kWh", "Balance_Euro", "Renewable_Usage_kWh"
            ])
        
        # Prosumer trading CSV
        with open("results/prosumer_trading.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestep", "Hour", "Prosumer_ID", "Home_Type_Index", "Role", "Is_Banned",
                "Desired_Quantity_kWh", "Bid_Price_Euro_kWh", "Ask_Price_Euro_kWh",
                "P2P_Trades_Count", "Market_Trades_Count"
            ])
        
        # All trades CSV
        with open("results/all_trades.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestep", "Hour", "Trade_Type", "Buyer_ID", "Seller_ID",
                "Quantity_kWh", "Price_Euro_kWh"
            ])
        
        # Regulator actions CSV
        with open("results/regulator_actions.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestep", "Hour", "Prosumer_ID", "Bonus_Euro", "Penalties_Euro",
                "Is_Banned", "Ban_Duration", "Ban_Reason"
            ])
        
        # Community summary CSV
        with open("results/community_summary.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestep", "Hour", "Price_Forecast_Euro_kWh",
                "Total_PV_Generation_kWh", "Total_Consumption_kWh",
                "Total_Surplus_kWh", "Total_Deficit_kWh",
                "P2P_Trades_Count", "Market_Trades_Count",
                "Active_Buyers", "Active_Sellers", "Banned_Prosumers"
            ])
    
    def initialize_prosumers(self):
        """Create prosumers with random characteristics"""
        print(f"Initializing {config.NUM_PROSUMERS} prosumers...")
        
        for i in range(config.NUM_PROSUMERS):
            home_index = random.randint(0, len(config.PV_CAPACITY) - 1)
            pv_capacity = config.PV_CAPACITY[home_index]  # PV capacity determined by home type
            base_consumption = config.BASE_CONSUMPTION[home_index]  # Consumption determined by home type
            has_battery = random.random() < config.HAS_BATTERY  # 80% chance of having battery
            # Battery capacity now consistent per home type (not random)
            battery_capacity = config.BATTERY_CAPACITY[home_index] if has_battery else 0.0
            
            prosumer = Prosumer(i, pv_capacity, base_consumption, battery_capacity, home_index)
            self.prosumers.append(prosumer)
        
        print(f"✓ Created {len(self.prosumers)} prosumers")
    
    def _log_timestep_to_csv(self, timestep: int, hour: int, price_forecast: float,
                              p2p_trades: List[Trade], market_trades: List[Trade],
                              imbalances_before_p2p: dict, imbalances_after_p2p: dict,
                              original_desired_quantities: dict):
        """
        Log timestep data to CSV files for efficient storage and analysis
        
        Args:
            timestep: Current timestep
            hour: Hour of day
            price_forecast: Energy price forecast
            p2p_trades: List of P2P trades executed
            market_trades: List of market trades executed
            imbalances_before_p2p: Dict of prosumer imbalances before P2P
            imbalances_after_p2p: Dict of prosumer imbalances after P2P
            original_desired_quantities: Dict of original desired quantities before trading
        """
        # Log prosumer energy states
        with open("results/prosumer_energy.csv", "a", newline="") as f:
            writer = csv.writer(f)
            for p in self.prosumers:
                battery_info = p.get_battery_info()
                writer.writerow([
                    timestep, hour, p.id, p.home_type_index, round(p.pv_generation, 4), round(p.consumption, 4),
                    battery_info['level'], battery_info['capacity'], battery_info['soc'],
                    round(p.battery_charged_kwh, 4), round(p.battery_discharged_kwh, 4),
                    round(imbalances_before_p2p.get(p.id, 0), 4),
                    round(imbalances_after_p2p.get(p.id, 0), 4),
                    round(p.imbalance, 4), round(p.balance, 4), round(p.renewable_usage, 4)
                ])
        
        # Log prosumer trading status
        with open("results/prosumer_trading.csv", "a", newline="") as f:
            writer = csv.writer(f)
            for p in self.prosumers:
                role = "Banned" if p.is_banned else ("Buyer" if p.is_buyer else ("Seller" if p.is_seller else "Neutral"))
                writer.writerow([
                    timestep, hour, p.id, p.home_type_index, role, p.is_banned,
                    round(original_desired_quantities.get(p.id, 0), 4) if not p.is_banned else 0,
                    round(p.bid_price, 4) if p.is_buyer else None,
                    round(p.ask_price, 4) if p.is_seller else None,
                    p.p2p_trades, p.market_trades
                ])
        
        # Log all trades
        with open("results/all_trades.csv", "a", newline="") as f:
            writer = csv.writer(f)
            for trade in p2p_trades + market_trades:
                writer.writerow([
                    timestep, hour, trade.trade_type, trade.buyer_id, trade.seller_id,
                    round(trade.quantity, 4), round(trade.price, 4)])
        
        # Log regulator actions
        with open("results/regulator_actions.csv", "a", newline="") as f:
            writer = csv.writer(f)
            for p in self.prosumers:
                writer.writerow([
                    timestep, hour, p.id, round(p.bonus, 4), round(p.penalties, 4),
                    p.is_banned, p.ban_duration, p.reason_for_ban
                ])
        
        # Log community summary
        with open("results/community_summary.csv", "a", newline="") as f:
            writer = csv.writer(f)
            total_pv = sum(p.pv_generation for p in self.prosumers)
            total_consumption = sum(p.consumption for p in self.prosumers)
            total_surplus = sum(p for p in imbalances_before_p2p.values() if p > 0)
            total_deficit = sum(abs(p) for p in imbalances_before_p2p.values() if p < 0)
            active_buyers = sum(1 for p in self.prosumers if p.is_buyer and not p.is_banned)
            active_sellers = sum(1 for p in self.prosumers if p.is_seller and not p.is_banned)
            banned = sum(1 for p in self.prosumers if p.is_banned)
            
            writer.writerow([
                timestep, hour, round(price_forecast, 4),
                round(total_pv, 4), round(total_consumption, 4),
                round(total_surplus, 4), round(total_deficit, 4),
                len(p2p_trades), len(market_trades),
                active_buyers, active_sellers, banned
            ])
    
    def simulate_timestep(self, timestep: int):
        """
        Simulate one timestep of the community
        
        Args:
            timestep: Current timestep (hour of day)
        """
        hour = timestep % 24    # hour of the day (0-23)
        
        # Verbose output
        if config.VERBOSE:
            print(f"\n{'='*70}")    # splitter line for timestep
            print(f"TIMESTEP {timestep} (Hour {hour}:00)")  # header for current timestep
            print(f"{'='*70}")  # splitter line
        
        # 1. Generate PV and consumption for all prosumers
        for prosumer in self.prosumers:
            pv_gen = generate_pv_generation(hour, prosumer.pv_capacity) # generate PV generation based on hour and prosumer's PV capacity
            consumption = generate_consumption(hour, prosumer.base_consumption) # generate consumption based on hour and prosumer's base consumption
            prosumer.update_energy_state(pv_gen, consumption)   # update prosumer's energy state with generated PV and consumption
        
        # 2. Get price forecast
        price_forecast = forecast_price(hour, config.BASE_PRICE)
        
        # Store imbalances before P2P for logging
        imbalances_before_p2p = {p.id: p.imbalance for p in self.prosumers}
        
        if config.VERBOSE:
            total_surplus = sum(p.imbalance for p in self.prosumers if p.imbalance > 0)
            total_deficit = sum(abs(p.imbalance) for p in self.prosumers if p.imbalance < 0)
            print(f"Price Forecast: €{price_forecast:.3f}/kWh")
            print(f"Total Surplus: {total_surplus:.2f} kWh | Total Deficit: {total_deficit:.2f} kWh")

        # 3. Prosumers prepare trading offers
        for prosumer in self.prosumers:
            prosumer.prepare_trading_offer(price_forecast, config.LOCAL_MARKET_FEE, config.MAX_TRADE_CAP)
        
        # 4. Check the total amount of asked and bid energy - if there is big difference check if some prosumer can help with their battery
        total_asked_energy = sum(p.desired_quantity for p in self.prosumers if p.is_buyer and not p.is_banned)
        total_bid_energy = sum(p.desired_quantity for p in self.prosumers if p.is_seller and not p.is_banned)

        self.p2p_mechanism.balance_trading_offers(self.prosumers, config.IMBALANCE_THRESHOLD, price_forecast, config.LOCAL_MARKET_FEE, config.MAX_TRADE_CAP)

        buyers_count = sum(1 for p in self.prosumers if p.is_buyer and not p.is_banned)
        sellers_count = sum(1 for p in self.prosumers if p.is_seller and not p.is_banned)
        
        if config.VERBOSE:
            print(f"Active Buyers: {buyers_count} | Active Sellers: {sellers_count}")
            print(f"Total Asked Energy: {total_asked_energy:.2f} kWh | Total Bid Energy: {total_bid_energy:.2f} kWh")
        
        # Store original desired quantities before trading (for logging purposes)
        original_desired_quantities = {p.id: p.desired_quantity for p in self.prosumers}

        # 4. Execute P2P trading
        p2p_trades = self.p2p_mechanism.execute_p2p_trading(self.prosumers, timestep)
        
        # Store imbalances after P2P for logging
        imbalances_after_p2p = {p.id: p.imbalance for p in self.prosumers}
        
        if config.VERBOSE:
            print(f"\nP2P Trading: {len(p2p_trades)} trades executed")
            if len(p2p_trades) > 0:
                total_p2p_energy = sum(t.quantity for t in p2p_trades)
                avg_p2p_price = sum(t.price * t.quantity for t in p2p_trades) / total_p2p_energy if total_p2p_energy > 0 else 0
                print(f"  Total Energy: {total_p2p_energy:.2f} kWh | Avg Price: €{avg_p2p_price:.3f}/kWh")
            satisfied_buyers = sum(1 for p in self.prosumers if p.is_buyer and not p.is_banned and p.desired_quantity < 0.01)
            satisfied_sellers = sum(1 for p in self.prosumers if p.is_seller and not p.is_banned and p.desired_quantity < 0.01)
            print(f"Satisfied Buyers after P2P: {satisfied_buyers} | Satisfied Sellers after P2P: {satisfied_sellers}")
            pending_prosumers = [p for p in self.prosumers if (p.is_buyer or p.is_seller) and not p.is_banned and p.desired_quantity > 0]
            if pending_prosumers:
                print(f"Pending Prosumers: {len(pending_prosumers)}")
        
        # Add P2P trades to blockchain
        for trade in p2p_trades:
            self.blockchain.add_transaction(trade.to_dict())
        
        # 5. Execute local market trading for remaining imbalances
        market_trades = self.local_market.execute_local_market(self.prosumers, price_forecast, timestep)
        
        if config.VERBOSE:
            print(f"\nLocal Market Trading: {len(market_trades)} trades executed")
            if len(market_trades) > 0:
                total_market_energy = sum(t.quantity for t in market_trades)
                print(f"  Total Energy: {total_market_energy:.2f} kWh")
            satisfied_buyers = sum(1 for p in self.prosumers if p.is_buyer and not p.is_banned and p.desired_quantity < 0.01)
            satisfied_sellers = sum(1 for p in self.prosumers if p.is_seller and not p.is_banned and p.desired_quantity < 0.01)
            print(f"Satisfied Buyers after Local Market: {satisfied_buyers} | Satisfied Sellers after Local Market: {satisfied_sellers}")
        
        # Add market trades to blockchain
        for trade in market_trades:
            self.blockchain.add_transaction(trade.to_dict())
        
        # 6. Mine blockchain blocks
        if self.blockchain.pending_transactions:
            mined_block = self.blockchain.mine_pending_transactions()
            if mined_block and config.VERBOSE:
                print(f"\n⛏ Block #{mined_block.index} mined with {len(mined_block.transactions)} transactions")
                print(f"  Hash: {mined_block.hash[:20]}... (Nonce: {mined_block.nonce})")

        # 7. Update ban durations (decrement from previous timesteps)
        self.regulator.update_prosumer_bans(self.prosumers)
        
        # 8. Apply incentives and penalties based on behavior
        self.regulator.incentivize_renewable_usage(self.prosumers)
        
        # 9. Enforce rules and apply new bans if needed
        self.regulator.enforce_rules(self.prosumers, timestep)
        
        # 10. Log all data to CSV files
        self._log_timestep_to_csv(timestep, hour, price_forecast, p2p_trades, market_trades,
                                   imbalances_before_p2p, imbalances_after_p2p, original_desired_quantities)
        
        # 11. Reset trading state for next timestep
        for prosumer in self.prosumers:
            prosumer.reset_trading_state()
        
        # Log timestep summary
        self.simulation_log.append({
            'timestep': timestep,
            'hour': hour,
            'p2p_trades': len(p2p_trades),
            'market_trades': len(market_trades),
            'price_forecast': price_forecast,
            'blockchain_blocks': len(self.blockchain.chain)
        })  # log summary data for the current timestep
    
    def run_simulation(self):
        """Run the complete simulation"""
        print("\n" + "="*70)    # splitter line for header
        print("PROSUMER COMMUNITY ENERGY TRADING SIMULATION")
        print("="*70)   # splitter line for details
        print(f"Number of Prosumers: {config.NUM_PROSUMERS}")
        print(f"Objective: {config.REGULATOR_OBJECTIVE}")
        print(f"Time Steps: {config.TIME_STEPS}")
        print(f"Blockchain Difficulty: {config.DIFFICULTY_TARGET} leading zeros")
        print(f"Number of Miners: {config.NUM_MINERS}")
        print("="*70)   # splitter line
        
        # Initialize prosumers
        self.initialize_prosumers()
        
        # Run simulation for each timestep
        for timestep in range(config.TIME_STEPS):
            self.simulate_timestep(timestep)
        
        # Mine any remaining pending transactions (at each timestamp just a block can be mined, but at the end we mine all remaining)
        while self.blockchain.pending_transactions:   # while there are still pending transactions in the blockchain
            mined_block = self.blockchain.mine_pending_transactions()   # attempt to mine a new block with pending transactions
            if mined_block and config.VERBOSE:  # if mining was successful and verbose output is enabled
                print(f"\n⛏ Final block #{mined_block.index} mined")
        
        # Generate final report
        self.generate_final_report()

        # Generate plots
        plot_generator = SimulationVisualizer("results")
        plot_generator.generate_all_plots()
    
    def generate_final_report(self):
        """Generate and display final simulation report"""
        print("\n" + "="*70)
        print("SIMULATION COMPLETE")
        print("="*70)
        
        # Blockchain summary
        print("\n📦 BLOCKCHAIN SUMMARY")
        blockchain_summary = self.blockchain.get_chain_summary()    # get summary statistics of the blockchain
        print(f"Total Blocks: {blockchain_summary['total_blocks']}")
        print(f"Total Transactions: {blockchain_summary['total_transactions']}")
        print(f"Chain Valid: {blockchain_summary['is_valid']}")
        
        # Miner statistics
        print("\n⛏ TOP MINERS")
        miner_stats = self.blockchain.get_miner_stats()    # get statistics of all miners
        top_miners = sorted(miner_stats, key=lambda x: x['blocks_mined'], reverse=True)[:5] # get top 5 miners by blocks mined
        for miner in top_miners:    # iterate over each top miner
            print(f"  Miner {miner['miner_id']}: {miner['blocks_mined']} blocks, "
                  f"euro{miner['total_reward']:.2f} reward")
        
        # Regulator report
        print(self.regulator.get_report(self.prosumers))
        
        # Top and bottom prosumers
        sorted_prosumers = sorted(self.prosumers, key=lambda x: x.balance, reverse=True)    # sort prosumers by their balance in descending order
        
        print("\n💰 TOP 5 PROSUMERS (by balance)")
        for i, p in enumerate(sorted_prosumers[:5]):    # iterate over top 5 prosumers by balance
            print(f"  {i+1}. Prosumer {p.id}: euro{p.balance:.2f} "
                  f"(P2P: {p.p2p_trades}, Market: {p.market_trades}, "
                  f"Renewable: {p.renewable_usage:.1f} kWh)")
        
        print("\n📉 BOTTOM 5 PROSUMERS (by balance)")
        for i, p in enumerate(sorted_prosumers[-5:]):   # iterate over bottom 5 prosumers by balance
            print(f"  {i+1}. Prosumer {p.id}: euro{p.balance:.2f} "
                  f"(P2P: {p.p2p_trades}, Market: {p.market_trades}, "
                  f"Renewable: {p.renewable_usage:.1f} kWh)")
        
        print("\n" + "="*70)