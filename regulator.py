"""
Regulator to enforce community rules and achieve objectives
"""
from typing import List
from prosumer import Prosumer
import config


class Regulator:
    """
    Community regulator that enforces rules and incentivizes desired behavior
    """
    
    def __init__(self, objective: str = "maximize_renewable"):
        """
        Initialize regulator with objective
        
        Args:
            objective: Community objective (maximize_renewable, maximize_profit, maximize_p2p)
        """
        self.objective = objective  # community objective
        self.total_incentives_paid = 0.0    # total incentives given to prosumers
        self.total_penalties_collected = 0.0    # total penalties collected from prosumers
        self.banned_prosumers = []    # list of banned prosumers

    def incentivize_renewable_usage(self, prosumers: List[Prosumer]):
        """
        Reward prosumers for using renewable energy and penalize market usage
        """
        for prosumer in prosumers:  # iterate over each prosumer
            # Skip banned prosumers - they don't receive incentives or penalties
            if prosumer.is_banned:
                continue
            
            # Bonus for renewable self-consumption
            if prosumer.renewable_usage > 0:    # if prosumer has renewable energy usage
                renewable_bonus = prosumer.renewable_usage * config.RENEWABLE_BONUS # calculate bonus based on usage of renewable energy
                prosumer.balance += renewable_bonus # add bonus to prosumer's balance
                prosumer.bonus += renewable_bonus  # track total bonuses received
                self.total_incentives_paid += renewable_bonus   # track total incentives paid
            
            # Penalty for using local market instead of P2P
            if prosumer.market_trades > 0:  # if prosumer has local market trades
                penalty = prosumer.market_quantity * config.PENALTY_FOR_MARKET    # calculate penalty based on last market quantity
                prosumer.balance -= penalty # deduct penalty from prosumer's balance
                prosumer.penalties += penalty   # track total penalties incurred
                self.total_penalties_collected += penalty   # track total penalties collected

    def enforce_rules(self, prosumers: List[Prosumer], timestep: int):
        """
        Enforce community rules and apply punishments
        
        Args:
            prosumers: List of prosumers
            timestep: Current timestep
        """
        for prosumer in prosumers:  # iterate over each prosumer
            # Skip already banned prosumers (ban duration is managed by update_ban_status())
            if prosumer.is_banned:
                continue

            if prosumer.penalties > 2.0 and prosumer.bonus < 2.0:  # if prosumer has high penalties and low bonuses
                # if the prosumer has been recently banned for the same reason, skip re-banning
                recent_bans = [ban for ban in self.banned_prosumers 
                               if ban['prosumer_id'] == prosumer.id and 
                               ban['timestep'] >= timestep - 5 and
                               ban['reason'] == 'excessive_market_usage']
                if recent_bans:
                    continue  # skip re-banning
                
                prosumer.apply_ban(duration=2, reason='excessive_market_usage')  # apply a ban for 2 timesteps
                self.banned_prosumers.append({
                    'prosumer_id': prosumer.id,
                    'timestep': timestep,
                    'reason': 'excessive_market_usage'
                })  # add the prosumer to the banned list
            
            if prosumer.balance < -20.0:  # if prosumer has very negative balance
                # if the prosumer has been recently banned for the same reason, skip re-banning
                recent_bans = [ban for ban in self.banned_prosumers 
                               if ban['prosumer_id'] == prosumer.id and 
                               ban['timestep'] >= timestep - 5 and
                               ban['reason'] == 'negative_balance']
                if recent_bans:
                    continue  # skip re-banning

                prosumer.apply_ban(duration=3, reason='negative_balance')  # apply a ban for 3 timesteps
                self.banned_prosumers.append({
                        'prosumer_id': prosumer.id,
                        'timestep': timestep,
                        'reason': 'negative_balance'
                    })  # add the prosumer to the banned list
    
    def update_prosumer_bans(self, prosumers: List[Prosumer]):
        """
        Update ban status for all prosumers (decrement ban duration)
        Should be called at the start of each timestep
        
        Args:
            prosumers: List of prosumers
        """
        for prosumer in prosumers:
            prosumer.update_ban_status()
    
    def get_community_metrics(self, prosumers: List[Prosumer]) -> dict:
        """
        Calculate community-level metrics based on objective
        
        Args:
            prosumers: List of prosumers
        
        Returns:
            Dictionary of community metrics
        """
        total_renewable = sum(p.renewable_usage for p in prosumers) # total renewable energy usage
        total_p2p_trades = sum(p.p2p_trades for p in prosumers) # total number of P2P trades
        total_market_trades = sum(p.market_trades for p in prosumers) # total number of local market trades
        total_profit = sum(p.balance for p in prosumers) # total profit of the community
        avg_balance = total_profit / len(prosumers) if prosumers else 0 # average balance per prosumer
        
        banned_count = sum(1 for p in prosumers if p.is_banned) # number of banned prosumers
        
        return {
            'total_renewable_usage': round(total_renewable, 2),
            'total_p2p_trades': total_p2p_trades,
            'total_market_trades': total_market_trades,
            'p2p_to_market_ratio': (total_p2p_trades / total_market_trades 
                                    if total_market_trades > 0 else float('inf')),
            'community_profit': round(total_profit, 2),
            'average_prosumer_balance': round(avg_balance, 2),
            'banned_prosumers': banned_count,
            'total_incentives_paid': round(self.total_incentives_paid, 2),
            'total_penalties_collected': round(self.total_penalties_collected, 2),
            'objective': self.objective
        }   # return dictionary of community metrics
    
    def get_report(self, prosumers: List[Prosumer]) -> str:
        """
        Generate a report on regulator activities
        
        Args:
            prosumers: List of prosumers
        
        Returns:
            String report
        """
        metrics = self.get_community_metrics(prosumers) # get community metrics
        
        report = f"\n{'='*60}\n"
        report += f"REGULATOR REPORT - Objective: {self.objective.upper()}\n"
        report += f"{'='*60}\n"
        report += f"Total Renewable Usage: {metrics['total_renewable_usage']} kWh\n"
        report += f"P2P Trades: {metrics['total_p2p_trades']}\n"
        report += f"Local Market Trades: {metrics['total_market_trades']}\n"
        report += f"P2P/Market Ratio: {metrics['p2p_to_market_ratio']:.2f}\n"
        report += f"Community Profit: €{metrics['community_profit']}\n"
        report += f"Average Prosumer Balance: €{metrics['average_prosumer_balance']}\n"
        report += f"Banned Prosumers: {metrics['banned_prosumers']}\n"
        report += f"Total Incentives Paid: €{metrics['total_incentives_paid']}\n"
        report += f"Total Penalties Collected: €{metrics['total_penalties_collected']}\n"
        report += f"{'='*60}\n"
        
        return report
    
    def __repr__(self):
        return f"Regulator(objective={self.objective})"
