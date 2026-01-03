# PROJECT DESCRIPTION

## PROSUMER COMMUNITY

- **~100 prosumers**
- **Energy balance techniques**: 1. Self-balancing, 2. Self-Organized Negotiation, 3. Local Market through load aggregator

**At each timetep:**
- Each prosumer balances its energy by using **self-balancing**, than if it has surplus energy it performs **self-organized trading** by deciding how much energy to trade, at which price and to whom to trade with. On the other hand, if a prosumer has energy deficit and cannot balance the energy imbalance, it needs to go to the **local market** whit which quantity and what price to buy energy.

## REGULATOR

It designs a strategy to reach a community objective (e.g. maximize the entire community profit, maximize the usage of renewable energy, maximize the self-organized trading, creating maximum chaos).  
Moreover, it manages a regulation mechanism (e.g. rewards, penalties, kick them out of the community, trade restrictions) to influence the prosumers' behavior.

## BLOCKCHAIN

Each transaction must be put in the blockchain. The consensus mechanism could be PoW (with 3.0 seconds difficulty target - the hash of the block should begin with 0003) or PoS.
The minimum number of miners could be 10.

## SIMULATION

The simulation must run for at least 24 steps (e.g. 1 step = 1 hour). This will affect the time scale for PV generation, price forecast, etc.