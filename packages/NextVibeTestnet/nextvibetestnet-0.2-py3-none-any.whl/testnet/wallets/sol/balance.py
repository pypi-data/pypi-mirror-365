from testnet.interfaces.logs import Logger
from testnet.interfaces import AddressBalanceInterface
from typing import Optional
from solana.rpc.api import Client
from solana.publickey import PublicKey


class SolAddressBalance(AddressBalanceInterface):
    @staticmethod
    def get_balance(wallet_name: Optional[str] = None, address: Optional[str] = None) -> float:
        """
        Returns the balance of a Solana wallet.

        :param wallet_name: Name of the Solana wallet.
        :param address: Solana address.
        :return: Returns the current balance in float type.
        """

        logger = Logger("solana-addresses-balance.log").get_logger()
        public_key = PublicKey(address)
        try:
            testnet_client = Client("https://api.devnet.solana.com")
            testnet_balance = testnet_client.get_balance(public_key)
            logger.info(f"Balance address: {address}: {float(testnet_balance.value) / 1_000_000_000}")
            return float(testnet_balance.value) / 1_000_000_000
        except Exception as e:
            logger.error(f"Error: Unable to fetch balance for Solana address '{address}': {str(e)}")
            return 0.0

