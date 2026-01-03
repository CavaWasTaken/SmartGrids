"""
Blockchain implementation with Proof-of-Work consensus
"""
import hashlib
import json
import time
import random
from typing import List, Dict, Optional


class Block:
    """Represents a single block in the blockchain"""
    
    def __init__(self, index: int, timestamp: float, transactions: List[dict],
                 previous_hash: str, nonce: int = 0):
        self.index = index  # position of the block in the chain
        self.timestamp = timestamp  # time of block creation
        self.transactions = transactions    # list of transactions in the block
        self.previous_hash = previous_hash  # hash of the previous block in the chain
        self.nonce = nonce  # nonce used for Proof-of-Work
        self.hash = self.calculate_hash()   # hash of the current block
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block"""
        block_data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }   # create a structure containing the data to be hashed
        block_string = json.dumps(block_data, sort_keys=True)   # convert the structure to a JSON string, sorting keys for consistency
        return hashlib.sha256(block_string.encode()).hexdigest()    # compute the SHA-256 hash of the JSON string
    
    def to_dict(self) -> dict:
        """Convert block to dictionary"""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }
    
    def __repr__(self):
        return (f"Block(index={self.index}, hash={self.hash[:10]}..., "
                f"transactions={len(self.transactions)}, nonce={self.nonce})")


class Miner:
    """Represents a miner in the blockchain network"""
    
    def __init__(self, miner_id: int):
        self.id = miner_id  # ID of the miner
        self.blocks_mined = 0  # number of blocks mined by this miner
        self.total_reward = 0.0  # total rewards earned by this miner
    
    def mine_block(self, block: Block, difficulty: int) -> Optional[Block]:
        """
        Mine a block using Proof-of-Work
        
        Args:
            block: Block to mine
            difficulty: Number of leading zeros required
        
        Returns:
            Mined block if successful, None otherwise
        """
        target = '0' * difficulty   # create the target string with required leading zeros
        
        # Try to find a valid nonce
        max_attempts = 1000000  # Prevent infinite loops
        for nonce in range(max_attempts):   # iterate max_attempts times to find a valid nonce
            block.nonce = nonce # set the nonce of the block
            block.hash = block.calculate_hash()  # calculate the hash with the current nonce
            
            if block.hash.startswith(target):   # check if the hash meets the difficulty target
                self.blocks_mined += 1  # increment the count of blocks mined by this miner
                return block
        
        return None
    
    def __repr__(self):
        return f"Miner(id={self.id}, blocks_mined={self.blocks_mined})"


class Blockchain:
    """
    Blockchain to record all energy trading transactions
    """
    
    def __init__(self, difficulty: int = 3, num_miners: int = 10, 
                 block_reward: float = 0.1, max_transactions_per_block: int = 50):
        self.chain = [] # list of blocks
        self.pending_transactions = [] # list of pending transactions
        self.difficulty = difficulty    # number of leading zeros required in hash
        self.block_reward = block_reward  # reward given to miner for mining a block
        self.max_transactions_per_block = max_transactions_per_block  # max transactions per block
        
        self.miners = [Miner(i) for i in range(num_miners)]  # list of miners
        
        self._create_genesis_block()    # create the first block in the chain (genesis block)
    
    def _create_genesis_block(self):
        """Create the first block in the chain (genesis block)"""
        genesis_block = Block(0, time.time(), [], "0")  # generate genesis block
        genesis_block.hash = genesis_block.calculate_hash() # calculate its hash
        self.chain.append(genesis_block)    # add genesis block to the chain
    
    def get_latest_block(self) -> Block:
        """Get the most recent block in the chain"""
        return self.chain[-1]   # return the last block in the chain
    
    def add_transaction(self, transaction: dict):
        """
        Add a transaction to pending transactions
        
        Args:
            transaction: Transaction dictionary
        """
        self.pending_transactions.append(transaction)   # add transaction to pending transaction list
    
    def mine_pending_transactions(self) -> Optional[Block]:
        """
        Mine pending transactions into a new block
        
        Returns:
            Newly mined block if successful, None otherwise
        """
        if not self.pending_transactions:   # if no pending transactions
            return None
        
        # Take up to max_transactions_per_block
        transactions_to_mine = self.pending_transactions[:self.max_transactions_per_block]  # extract the maximum number of transactions to include in the new block
        
        # Create new block
        new_block = Block(
            index=len(self.chain),  # index of the new block is the current chain length
            timestamp=time.time(),  # current timestamp for the new block
            transactions=transactions_to_mine,  # set of transactions to include in the new block
            previous_hash=self.get_latest_block().hash  # hash of the previous block in the chain
        )
        
        # Select a random miner to mine (simulating competition)
        selected_miner = random.choice(self.miners)  # randomly select a miner from the list
        
        # Mine the block
        mined_block = selected_miner.mine_block(new_block, self.difficulty)
        
        if mined_block:  # if mining was successful
            # Add block to chain
            self.chain.append(mined_block)  # append the newly mined block to the blockchain
            
            # Remove mined transactions from pending
            self.pending_transactions = self.pending_transactions[self.max_transactions_per_block:]  # remove the mined transactions from the pending list
            
            # Reward the miner
            selected_miner.total_reward += self.block_reward    # add the block reward to the miner's total rewards
            
            return mined_block  # return the newly mined block
        
        return None  # return None if mining failed
    
    def is_chain_valid(self) -> bool:
        """
        Validate the entire blockchain
        
        Returns:
            True if chain is valid, False otherwise
        """
        for i in range(1, len(self.chain)):  # iterate over each block starting from the second block
            current_block = self.chain[i]   # current block in the iteration
            previous_block = self.chain[i - 1]  # previous block in the iteration
            
            # Check hash
            if current_block.hash != current_block.calculate_hash():    # check if the stored hash matches the calculated hash of the current block
                return False
            
            # Check previous hash link
            if current_block.previous_hash != previous_block.hash:  # check if the previous hash link is consistent
                return False
            
            # Check difficulty
            if not current_block.hash.startswith('0' * self.difficulty):  # check if the hash meets the difficulty target
                return False
        
        return True
    
    def get_chain_summary(self) -> dict:
        """Get summary statistics of the blockchain"""
        total_transactions = sum(len(block.transactions) for block in self.chain)
        total_pending = len(self.pending_transactions)
        
        return {
            'total_blocks': len(self.chain),    # total number of blocks in the chain
            'total_transactions': total_transactions,   # total number of transactions in the chain
            'pending_transactions': total_pending, # number of pending transactions
            'is_valid': self.is_chain_valid(),  # validity status of the chain
            'miners': len(self.miners), # number of miners
            'difficulty': self.difficulty   # mining difficulty target
        }   # return summary dictionary of the blockchain
    
    def get_miner_stats(self) -> List[dict]:
        """Get statistics for all miners"""
        return [
            {
                'miner_id': miner.id,   # unique identifier of the miner
                'blocks_mined': miner.blocks_mined,   # number of blocks mined by the miner
                'total_reward': round(miner.total_reward, 2)   # total rewards earned by the miner, rounded to 2 decimals
            }   # dictionary of miner statistics
            for miner in self.miners    # iterate over each miner in the miners list
        ]  # return list of miner statistics
    
    def to_dict(self) -> dict:
        """Convert blockchain to dictionary for export"""
        return {
            'chain': [block.to_dict() for block in self.chain],
            'summary': self.get_chain_summary(),
            'miners': self.get_miner_stats()
        }
    
    def __repr__(self):
        return (f"Blockchain(blocks={len(self.chain)}, "
                f"pending={len(self.pending_transactions)}, "
                f"valid={self.is_chain_valid()})")
