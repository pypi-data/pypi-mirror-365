from bitcoinlib.wallets import Wallet, WalletError
from testnet.interfaces.logs import Logger
from testnet.interfaces import AddressBalanceInterface
from typing import Optional


class BtcAddressBalance(AddressBalanceInterface):
    @staticmethod
    def get_balance(wallet_name: Optional[str] = None, address: Optional[str] = None) -> float:
        """
        Returns the current balance of a Bitcoin wallet.
        :param wallet_name:
        :param address:
        :return: Returns the current balance in float type
        """

        logger = Logger(log_file="btc-addresses-balance.log").get_logger()
        try:
            wallet = Wallet(wallet_name)
        except WalletError:
            logger.error(f"Error: Unable to find wallet '{wallet_name}'.")
            return 0.0

        try:
            wallet.utxos_update()
            satoshi_balance = wallet.balance()
            balance = satoshi_balance / 100_000_000
            logger.info(f"Balance address: {wallet.get_key().address}: {balance}")
            return balance
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return 0.0
