from testnet.interfaces.logs import Logger
from testnet.interfaces import AddressBalanceInterface
from typing import Optional

from tronpy import Tron


class TrxAddressBalance(AddressBalanceInterface):
    @staticmethod
    def get_balance(wallet_name: Optional[str] = None, address: Optional[str] = None) -> float:
        tron = Tron(network="nile")

        if address:
            try:
                balance = float(tron.get_account(address)["balance"])
                Logger(log_file="trx-addresses-balance.log").get_logger().info(f"Balance: {balance / 10**6} "
                                                                               f"address: {address}")
                return balance / 10**6
            except Exception as e:
                Logger(log_file="trx-addresses-balance.log").get_logger().error(f"Error: {str(e)}")
                return 0.0
