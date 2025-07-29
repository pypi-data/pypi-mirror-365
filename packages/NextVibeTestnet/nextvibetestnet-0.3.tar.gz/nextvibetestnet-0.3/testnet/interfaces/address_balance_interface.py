from abc import ABC, abstractmethod
from typing import Optional


class AddressBalanceInterface(ABC):
    """
    Interface for wallet balance retrieval.

    """
    @staticmethod
    @abstractmethod
    def get_balance(wallet_name: Optional[str] = None, address: Optional[str] = None) -> float:
        """
        Returns the balance of the wallet in selected blockchain.

        :param address:
        :param wallet_name: Name of the wallet.
        :return: Balance of the wallet in selected blockchain"""
        ...
