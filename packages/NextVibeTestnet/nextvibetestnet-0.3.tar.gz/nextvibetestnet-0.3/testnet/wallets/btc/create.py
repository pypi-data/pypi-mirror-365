from typing import Dict, Optional  # Types
from bitcoinlib.wallets import Wallet  # Library for working with Bitcoin blockchain

from testnet.interfaces import WalletAddressCreateInterface  # Interface for wallet creation
from testnet.interfaces.logs import Logger  # Import class for logging


class BtcWalletAddressCreate(WalletAddressCreateInterface):
    @staticmethod
    def create(user_id: Optional[int] = None) -> Dict[str, str]:
        """
        Creates a new Bitcoin wallet and returns the wallet details.
        The wallet details include the wallet object, address, and account ID.
        If an error occurs, logs the error and returns a dictionary with an error message.

        Args:
            user_id (int, optional): User associated with the wallet. Defaults to None.

        Returns:
            Dict[str, str]: Wallet details or an error message.
        """
        logger = Logger(log_file="btc-addresses-generator.log").get_logger()

        try:
            # Try to create the wallet
            wallet = Wallet.create(f"NextVibeWalletBtc{user_id}", network='testnet')
            address = wallet.get_key().address

            logger.info(f"Successfully created BTC wallet for user {user_id} with address {address} wallet name "
                        f"{wallet.name}")

            return {
                "wallet": wallet,
                "address": address,
                "account_id": wallet.wallet_id
            }

        except Exception as e:
            # Log the error and return an error response
            error_message = f"Failed to create BTC wallet for user {user_id}: {str(e)}"
            logger.error(error_message)

            return {"error": error_message}
