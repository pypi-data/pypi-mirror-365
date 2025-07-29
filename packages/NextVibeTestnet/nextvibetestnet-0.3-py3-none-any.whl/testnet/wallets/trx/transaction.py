from tronpy import Tron
from tronpy.keys import PrivateKey


class TrxTransaction:
    def __init__(self, sender_private_key: str, recipient_address: str, amount: float):
        """
        Initialize the Tron transaction class.

        :param sender_private_key: Sender's Tron private key.
        :param recipient_address: Recipient's Tron address.
        :param amount: Amount of Tron to be transferred.
        """
        self._tron = Tron(network="nile")
        self.__sender_private_key = PrivateKey.fromhex(sender_private_key)
        self._recipient_address: str = recipient_address
        self._amount: float = amount

    def send(self):
        txn = (
            self._tron.trx.transfer(self.__sender_private_key.public_key.to_base58check_address(),
                                    self._recipient_address,
                                    int(self._amount * (10**6)))
            .build()
            .sign(self.__sender_private_key)
        )

        txn_hash = txn.broadcast().wait()
        return f"https://nile.tronscan.org/#/transaction/{txn_hash['id']}"

