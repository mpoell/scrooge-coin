from transaction import Transaction, CoinCreation, Payment
from hashutils import hash_sha256
from base64 import b64encode
from scroogecoin import CoinId


class Blockchain():
    """
    Blockchain is composed by the blockchain itself.
    Represented as an array of blocks, and a series of 
    functions to manage it.
    """

    def __init__(self):
        self.blocks = []

    def add_block(self, block):
        """
        Add a block to the blockchain.
        Return hash of the block.
        """
        if len(self.blocks) > 0:
            block.hash_previous_block = hash_sha256(
                str(self.blocks[-1]).encode('utf-8'))
        else:
            block.hash_previous_block = None
        block.transaction.id = len(self.blocks)

        coin_num = 0
        for coin in block.transaction.created_coins:
            coin.id = CoinId(coin_num, block.transaction.id)
            coin_num += 1

        self.blocks.append(block)
        return block

    def check_blockchain(self):
        """Check the blockchain for inconsistencies."""
        blocks = self.blocks

        # The list must have at least one block (genesis block)
        if len(blocks) == 0:
            return False

        for i in range(len(blocks) - 1, 0, -1):
            if blocks[i].hash_previous_block != hash_sha256(blocks[i - 1]):
                return False

        return True

    def check_coin(self, coin):
        """Check if coin was created, and not yet consumed."""
        creation_id = coin.id.transaction_id

        if coin not in self.blocks[creation_id].transaction.created_coins:
            print('WARNING: Coin creation not found')
            return False

        for i in range(creation_id + 1, len(self.blocks)):
            transaction = self.blocks[i].transaction
            if isinstance(transaction, Payment) and coin in transaction.consumed_coins:
                print('WARNING: Double spend attempt detected')
                return False

        return True

    def check_coins(self, coins):
        """
        Check a group of coins. If check_coin function returns
        false for any of the coins in parameter, returns false,
        otherwise true. 
        """
        for coin in coins:
            if not self.check_coin(coin):
                return False
        return True

    def get_hash_last_block(self):
        """
        Return the hash of the last block of the blockchain.
        If ther are not blocks, return None.
        """
        if len(self.blocks) > 0:
            return hash_sha256(self.blocks[-1])
        else:
            return None

    def __str__(self):
        separator = '-' * 30 + '\n'
        concat = 'Blockchain \n' + separator
        for block in self.blocks:
            concat += str(block) + separator
        return concat


class Block():
    """
    Node of blockchain.
    """

    def __init__(self, transaction, hash_previous_block=None):
        self.transaction = transaction
        self.hash_previous_block = hash_previous_block

    def __str__(self):
        return 'Block: ' + str(self.transaction.id) + \
            '\tHash previous block: ' + str(self.hash_previous_block) + '\n' + \
            str(self.transaction)
