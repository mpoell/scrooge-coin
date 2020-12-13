from ecdsa import SigningKey
from hashutils import hash_sha256, hash_object, encoded_hash_object
from transaction import Payment, CoinCreation
from scroogecoin import ScroogeCoin


class Wallet():
    """ A user of the scroogecoin currency. """

    def __init__(self, signing_key=None):
        if signing_key is None:
            self.signing_key = SigningKey.generate()
        else:
            self.signing_key = signing_key
        self.verifying_key = self.signing_key.get_verifying_key()
        self.id = self.get_wallet_id_from_verifying_key(self.verifying_key)

    def sign(self, message):
        """ Sign a message using the signing key. """
        return self.signing_key.sign(message)

    def verify_signature(self, verifying_key, signature, message):
        """ Verify a signature of a message using the verifying key. """
        return verifying_key.verify(signature, message)

    def get_wallet_id_from_verifying_key(self, verifying_key):
        """ Return the wallet key from the verifying key. """
        return hash_object(verifying_key.to_string())

    def create_payment(self, payments, blockchain, scrooge):
        """
        Transfer coins from this wallet to other(s).
        Params:
        - payments: List of tuples (wallet id, amount)
        - blockchain: The complete blockchain
        - scrooge: An interace to the scrooge functions
        """
        consumed_coins = []
        created_coins = []
        my_coins = self.get_coins(blockchain)

        # TODO: Order coins by their values

        for wallet_id, amount in payments:
            my_coins[:] = [
                coin for coin in my_coins if coin not in consumed_coins
            ]
            for coin in my_coins:
                if coin.value <= amount:
                    consumed_coins.append(coin)
                    consumed_amount = coin.value
                    amount -= coin.value
                else:
                    new_coins = self.divide_coin(coin, amount, scrooge)
                    consumed_idx = self.index_coin_value(new_coins, amount)
                    consumed_coins.append(new_coins[consumed_idx])
                    consumed_amount = amount
                    my_coins.append(new_coins[consumed_idx + 1])
                    amount = 0
            created_coins.append(
                ScroogeCoin(value=consumed_camount, wallet_id=wallet_id)
            )
            if amount == 0:
                break
        return Payment(created_coins, consumed_coins)

    def index_coin_value(self, coins, value):
        """
        Return the index of the first coin with the value
        passed as parameter.
        """
        idx = 0
        while idx < len(coins):
            if coins[idx].value == value:
                return idx
            else:
                idx += 1
        return None

    def divide_coin(self, coin, value, scrooge):
        """
        Divide a coin in two new coins. 
        Params: 
        - value: is the value of one of the new coins a
        - coin: The coin to be consumed and divided. This
                coin cannot be used again.
        """
        if value > coin.value:
            return
        created_coins = []
        created_coins.append(ScroogeCoin(value, self.id))
        created_coins.append(ScroogeCoin(coin.value - value, self.id))
        payment = Payment(created_coins=created_coins, consumed_coins=[coin])
        signature = self.sign(encoded_hash_object(payment))
        new_block = scrooge.process_payment(
            payment, [(self.verifying_key, signature)]
        )
        return new_block.transaction.created_coins

    def get_coins(self, blockchain):
        """
        Get all active coins of the blockchain 
        associated to this wallet.
        """
        coins = []
        for block in blockchain.blocks:
            tx = block.transaction
            for coin in tx.created_coins:
                if coin.wallet_id == self.id:
                    coins.append(coin)
                if isinstance(tx, CoinCreation):
                    continue
                for coin in tx.consumed_coins:
                    if coin.wallet_id == self.id:
                        coins.remove(coin)
        return coins

    def __str__(self):
        """ String representations of the wallet """
        separator = '-' * 30 + '\n'
        concat = 'Wallet\n' + separator + \
            'Id: ' + self.id + '\n' + separator
        return concat
