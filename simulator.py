"""
Main simulator orchestrating the prosumer community energy trading
"""
import random
from typing import List
from prosumer import Prosumer
from trading import P2PTradingMechanism, LocalMarketMechanism, Trade
from blockchain import Blockchain
from regulator import Regulator
from data_generation import generate_pv_generation, generate_consumption, forecast_price
import config
import json


class CommunitySimulator:
    """
    Main simulator for the prosumer community
    """
    
    def __init__(self):
        """Initialize the simulator with all components"""
        self.prosumers = [] # list of prosumers
        self.p2p_mechanism = P2PTradingMechanism()  # initialize P2P trading mechanism which meets offer to demand
        self.local_market = LocalMarketMechanism(
            aggregator_id=-1, # ID of the aggregator which manages the market
            transaction_fee=config.LOCAL_MARKET_FEE # euro/kWh fee charged by aggregator to each trade
        )   # initialize local market mechanism for balancing remaining imbalances
        self.blockchain = Blockchain(
            difficulty=config.DIFFICULTY_TARGET,    # number of leading zeros required in hash
            num_miners=config.NUM_MINERS,   # number of miners in the blockchain network
            block_reward=config.BLOCK_REWARD,  # reward given to miner for mining a block
            max_transactions_per_block=config.MAX_TRANSACTIONS_PER_BLOCK  # max transactions per block
        )   # initialize blockchain for recording trades
        self.regulator = Regulator(objective=config.REGULATOR_OBJECTIVE)    # initialize community regulator with specified objective, it enforces rules and incentivizes desired behavior
        
        self.current_timestep = 0   # current timestep of the simulation
        self.simulation_log = []    # log to store simulation data for analysis
        
    def initialize_prosumers(self):
        """Create prosumers with random characteristics"""
        print(f"Initializing {config.NUM_PROSUMERS} prosumers...")
        
        # for each prosumer, evaluate a random PV capacity between min and max, and a random base consumption between min and max
        for i in range(config.NUM_PROSUMERS):
            pv_capacity = random.uniform(config.MIN_PV_CAPACITY, config.MAX_PV_CAPACITY)
            base_consumption = random.uniform(config.MIN_BASE_CONSUMPTION, 
                                             config.MAX_BASE_CONSUMPTION)
            battery_capacity = random.choices(config.BATTERY_CAPACITY, weights=[0.4, 0.15, 0.25, 0.15, 0.05], k=1)[0]  # choose a random battery capacity from the list with weights
            
            prosumer = Prosumer(i, pv_capacity, base_consumption, battery_capacity)   # initialize prosumer with ID, PV capacity, base consumption, and battery capacity
            self.prosumers.append(prosumer) # add prosumer to the community list
        
        print(f"✓ Created {len(self.prosumers)} prosumers")
    
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
        price_forecast = forecast_price(hour, config.BASE_PRICE)   # get the energy price forecast for the hour

########################

        # Initialize timestep data structure (we'll write once at the end)
        # read existing data or start with empty dict
        try:
            with open("results/timestep_data.json", "r") as f:
                timestep_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            timestep_data = {}

        # initialize timestep data
        timestep_key = f'Timestep_{timestep}'
        timestep_data[timestep_key] = {
            'Price_Forecast_euro/kWh': round(price_forecast, 4),
            'Prosumers': {}
        }
        for p in self.prosumers:
            timestep_data[timestep_key]['Prosumers'][f'Prosumer_{p.id}'] = {
                'PV_Generation_kWh': round(p.pv_generation, 4),
                'Consumption_kWh': round(p.consumption, 4),
                'Balance_euro': round(p.balance, 4),
                'Bonus': round(p.bonus, 4),
                'Penalties': round(p.penalties, 4),                    
                'Imbalances': {},
                'Trader_Status': {},
                'P2P_Trades': [],
                'Market_Trades': [],
                'Regulator': {}
            }   

########################
        if config.VERBOSE:  # verbose output for price and total surplus/deficit
            # count total surplus and deficit in the community (for each prosumer)
            total_surplus = sum(p.imbalance for p in self.prosumers if p.imbalance > 0)
            total_deficit = sum(abs(p.imbalance) for p in self.prosumers if p.imbalance < 0)
            print(f"Price Forecast: euro{price_forecast:.3f}/kWh")
            print(f"Total Surplus: {total_surplus:.2f} kWh | Total Deficit: {total_deficit:.2f} kWh")

########################

        # Track imbalances - BEFORE P2P (add to existing timestep_data)
        for p in self.prosumers:
            timestep_data[timestep_key]['Prosumers'][f'Prosumer_{p.id}']['Imbalances'] = {
                'Before_P2P': round(p.imbalance, 4)
            }

        # 3. Prosumers prepare trading offers
        for prosumer in self.prosumers:
            prosumer.prepare_trading_offer(price_forecast, config.LOCAL_MARKET_FEE, config.MAX_TRADE_CAP)  # prosumer prepares their trading offer (buy or sell) based on imbalance and price forecast
        
        buyers_count = sum(1 for p in self.prosumers if p.is_buyer and not p.is_banned) # count active buyers who are not banned
        sellers_count = sum(1 for p in self.prosumers if p.is_seller and not p.is_banned)   # count active sellers who are not banned
        
        if config.VERBOSE:  # verbose output for active buyers and sellers
            print(f"Active Buyers: {buyers_count} | Active Sellers: {sellers_count}")

########################

        # Log active traders data (add to existing timestep_data)
        for p in self.prosumers:
            if (p.is_buyer or p.is_seller) and not p.is_banned:
                timestep_data[timestep_key]['Prosumers'][f'Prosumer_{p.id}']['Trader_Status'] = {
                    'Role': 'Buyer' if p.is_buyer else 'Seller',
                    'Desired_Quantity_kWh': round(p.desired_quantity, 4),
                    'Bid_Price_euro/kWh': round(p.bid_price, 4) if p.is_buyer else None,
                    'Ask_Price_euro/kWh': round(p.ask_price, 4) if p.is_seller else None,
                    'Grid_Buy_Price_euro/kWh': round(price_forecast + (p.desired_quantity * config.LOCAL_MARKET_FEE), 4),
                    'Grid_Sell_Price_euro/kWh': round(price_forecast - (p.desired_quantity * config.LOCAL_MARKET_FEE), 4)
                }
            elif p.is_banned:
                timestep_data[timestep_key]['Prosumers'][f'Prosumer_{p.id}']['Trader_Status'] = {
                    'Role': 'Banned',
                    'Desired_Quantity_kWh': 0,
                    'Bid_Price_euro/kWh': None,
                    'Ask_Price_euro/kWh': None,
                    'Grid_Buy_Price_euro/kWh': None,
                    'Grid_Sell_Price_euro/kWh': None
                }
            else:
                timestep_data[timestep_key]['Prosumers'][f'Prosumer_{p.id}']['Trader_Status'] = {
                    'Role': 'Neutral',
                    'Desired_Quantity_kWh': round(p.desired_quantity, 4),
                    'Bid_Price_euro/kWh': None,
                    'Ask_Price_euro/kWh': None,
                    'Grid_Buy_Price_euro/kWh': None,
                    'Grid_Sell_Price_euro/kWh': None
                }

########################

        # 4. Execute P2P trading
        p2p_trades = self.p2p_mechanism.execute_p2p_trading(self.prosumers, timestep)   # execute P2P trading among prosumers at the current timestep
        
        if config.VERBOSE:  # verbose output for P2P trades
            print(f"\nP2P Trading: {len(p2p_trades)} trades executed")
            if len(p2p_trades) > 0:
                total_p2p_energy = sum(t.quantity for t in p2p_trades)  # total energy traded in P2P
                avg_p2p_price = sum(t.price * t.quantity for t in p2p_trades) / total_p2p_energy if total_p2p_energy > 0 else 0 # average price of P2P trades
                print(f"  Total Energy: {total_p2p_energy:.2f} kWh | Avg Price: euro{avg_p2p_price:.3f}/kWh")

########################

        # log to the prosumer that has traded the trades in the timestep_data
        for trade in p2p_trades:
            buyer_data = timestep_data[timestep_key]['Prosumers'][f'Prosumer_{trade.buyer_id}']
            seller_data = timestep_data[timestep_key]['Prosumers'][f'Prosumer_{trade.seller_id}']
            
            if 'P2P_Trades' not in buyer_data:
                buyer_data['P2P_Trades'] = []
            if 'P2P_Trades' not in seller_data:
                seller_data['P2P_Trades'] = []
            
            buyer_data['P2P_Trades'].append({
                'Role': 'Buyer',
                'Counterparty': trade.seller_id,
                'Quantity_kWh': round(trade.quantity, 4),
                'Price_euro/kWh': round(trade.price, 4)
            })
            seller_data['P2P_Trades'].append({
                'Role': 'Seller',
                'Counterparty': trade.buyer_id,
                'Quantity_kWh': round(trade.quantity, 4),
                'Price_euro/kWh': round(trade.price, 4)
            })

########################

########################

        # log each P2P trade in a json file

        # read existing data or start with empty dict
        try:
            with open("results/trades.json", "r") as f:
                trades_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            trades_data = {}
        
        # initialize timestep data
        timestep_key = f'Timestep_{timestep}'
        trades_data[timestep_key] = []
        for trade in p2p_trades:
            trades_data[timestep_key].append(trade.to_dict())
            
########################

        # track imbalances - AFTER P2P (add to existing timestep_data)
        for p in self.prosumers:
            remaining = p.calculate_remaining_imbalance()
            timestep_data[timestep_key]['Prosumers'][f'Prosumer_{p.id}']['Imbalances']['After_P2P'] = round(remaining, 4)
                
        # Add P2P trades to blockchain
        for trade in p2p_trades:
            self.blockchain.add_transaction(trade.to_dict())    # add each P2P trade as a transaction in the blockchain

        # print the amount of satisfied buyers and sellers after P2P trading
        if config.VERBOSE:
            satisfied_buyers = sum(1 for p in self.prosumers if p.is_buyer and not p.is_banned and p.desired_quantity < 0.01)
            satisfied_sellers = sum(1 for p in self.prosumers if p.is_seller and not p.is_banned and p.desired_quantity < 0.01)
            print(f"\nSatisfied Buyers after P2P: {satisfied_buyers} | Satisfied Sellers after P2P: {satisfied_sellers}")

        # print any pending prosumers that have not traded yet
        if config.VERBOSE:
            pending_prosumers = [p for p in self.prosumers if (p.is_buyer or p.is_seller) and not p.is_banned and p.desired_quantity > 0]
            if pending_prosumers:
                print(f"\nPending Prosumers (not traded yet): {len(pending_prosumers)}")
        
        # 5. Execute local market trading for remaining imbalances
        market_trades = self.local_market.execute_local_market(
            self.prosumers, price_forecast, timestep
        )   # execute local market trading to balance remaining imbalances
        
        if config.VERBOSE:  # verbose output for local market trades
            print(f"\nLocal Market Trading: {len(market_trades)} trades executed")
            if len(market_trades) > 0:  
                total_market_energy = sum(t.quantity for t in market_trades)    # total energy traded in local market
                print(f"  Total Energy: {total_market_energy:.2f} kWh")

########################

        # log to the prosumer that has traded the trades in the timestep_data
        for trade in market_trades:
            if trade.buyer_id == -1:
                seller_data = timestep_data[timestep_key]['Prosumers'][f'Prosumer_{trade.seller_id}']
                if 'Market_Trades' not in seller_data:
                    seller_data['Market_Trades'] = []

                seller_data['Market_Trades'].append({
                    'Role': 'Seller',
                    'Counterparty': 'Aggregator',
                    'Quantity_kWh': round(trade.quantity, 4),
                    'Price_euro/kWh': round(trade.price, 4)
                })                
            elif trade.seller_id == -1:
                buyer_data = timestep_data[timestep_key]['Prosumers'][f'Prosumer_{trade.buyer_id}']
                if 'Market_Trades' not in buyer_data:
                    buyer_data['Market_Trades'] = []

                buyer_data['Market_Trades'].append({
                    'Role': 'Buyer',
                    'Counterparty': 'Aggregator',
                    'Quantity_kWh': round(trade.quantity, 4),
                    'Price_euro/kWh': round(trade.price, 4)
                })

########################

########################

        # log each P2P trade in a json file
        
        # initialize timestep data
        timestep_key = f'Timestep_{timestep}'
        for trade in market_trades:
            trades_data[timestep_key].append(trade.to_dict())
        
        # write everything back
        with open("results/trades.json", "w") as f:
            json.dump(trades_data, f, indent=4)
            
########################

        # track imbalances - AFTER Local Market (add to existing timestep_data)
        for p in self.prosumers:
            remaining = p.calculate_remaining_imbalance()
            timestep_data[timestep_key]['Prosumers'][f'Prosumer_{p.id}']['Imbalances']['After_Local_Market'] = round(remaining, 4)

        # print the amount of satisfied buyers and sellers after local market trading
        if config.VERBOSE:
            satisfied_buyers = sum(1 for p in self.prosumers if p.is_buyer and not p.is_banned and p.desired_quantity < 0.01)
            satisfied_sellers = sum(1 for p in self.prosumers if p.is_seller and not p.is_banned and p.desired_quantity < 0.01)
            print(f"\nSatisfied Buyers after Local Market: {satisfied_buyers} | Satisfied Sellers after Local Market: {satisfied_sellers}")
        
        # Add market trades to blockchain
        for trade in market_trades:
            self.blockchain.add_transaction(trade.to_dict())    # add each local market trade as a transaction in the blockchain
        
        # 6. Mine blockchain blocks
        if self.blockchain.pending_transactions:    # iterate over the pending transactions in the blockchain
            mined_block = self.blockchain.mine_pending_transactions()   # attempt to mine a new block with pending transactions
            if mined_block and config.VERBOSE:  # if mining was successful and verbose output is enabled
                print(f"\n⛏ Block #{mined_block.index} mined with {len(mined_block.transactions)} transactions")
                print(f"  Hash: {mined_block.hash[:20]}... (Nonce: {mined_block.nonce})")

        # 7. Update prosumer ban statuses
        self.regulator.incentivize_renewable_usage(self.prosumers)   # apply incentives or penalties to prosumers based on their behavior
        
        # 9. Apply regulator incentives and enforce rules (which may apply new bans)
        self.regulator.enforce_rules(self.prosumers, timestep)   # enforce regulatory rules on prosumers

########################

        # log regulator actions (add to existing timestep_data)
        for p in self.prosumers:
            timestep_data[timestep_key]['Prosumers'][f'Prosumer_{p.id}']['Regulator']['Applied_Bonus'] = round(p.bonus, 4)
            timestep_data[timestep_key]['Prosumers'][f'Prosumer_{p.id}']['Regulator']['Applied_Penalties'] = round(p.penalties, 4)
            timestep_data[timestep_key]['Prosumers'][f'Prosumer_{p.id}']['Regulator']['Is_Banned'] = p.is_banned
            timestep_data[timestep_key]['Prosumers'][f'Prosumer_{p.id}']['Regulator']['Ban_Duration'] = p.ban_duration
            timestep_data[timestep_key]['Prosumers'][f'Prosumer_{p.id}']['Regulator']['Reason_for_Ban'] = p.reason_for_ban

        # Write all timestep data once at the end (after all data is collected)
        with open("results/timestep_data.json", "w") as f:
            json.dump(timestep_data, f, indent=4)

        
        # 10. Reset trading state for next timestep
        for prosumer in self.prosumers:  # iterate over each prosumer
            prosumer.reset_trading_state()   # reset trading state for the next timestep
        
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
    
    def get_simulation_data(self) -> dict:
        """
        Get all simulation data for export
        
        Returns:
            Dictionary with all simulation data
        """
        return {
            'config': {
                'num_prosumers': config.NUM_PROSUMERS,
                'time_steps': config.TIME_STEPS,
                'objective': config.REGULATOR_OBJECTIVE,
                'difficulty': config.DIFFICULTY_TARGET,
                'num_miners': config.NUM_MINERS
            },  # configuration parameters
            'prosumers': [
                {
                    'id': p.id,
                    'pv_capacity': p.pv_capacity,
                    'base_consumption': p.base_consumption,
                    'balance': round(p.balance, 2),
                    'renewable_usage': round(p.renewable_usage, 2),
                    'p2p_trades': p.p2p_trades,
                    'market_trades': p.market_trades
                }
                for p in self.prosumers
            ],  # list of prosumer data
            'blockchain': self.blockchain.to_dict(),    # blockchain data
            'regulator': self.regulator.get_community_metrics(self.prosumers),  # community metrics
            'simulation_log': self.simulation_log   # log of simulation timesteps
        }