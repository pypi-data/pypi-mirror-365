from typing import Dict, Optional  # Types

from solana.keypair import Keypair

from testnet.interfaces import WalletAddressCreateInterface  # Interface for wallet creation
from testnet.interfaces.logs import Logger  # Import class for logging


class SolWalletAddressCreate(WalletAddressCreateInterface):
    @staticmethod
    def create(user_id: Optional[int] = None) -> Dict[str, str]:
        """
        Creates a new Solana wallet and returns the wallet details.

        Args:
            user_id (int, optional): User associated with the wallet. Defaults to None.

        Returns:
            Dict[str, str]: Wallet details or an error message.
        """
        logger = Logger(log_file="sol-addresses-generator.log").get_logger()

        try:
            # Try to create the wallet
            keypair = Keypair.generate()
            public_key = keypair.public_key
            private_key = keypair.secret_key.hex()
            logger.info(f"Creating wallet with address {public_key} and private key {private_key}")
            return {"address": str(public_key), "private_key": str(private_key)}
        except Exception as e:
            logger.error(f"Error creating Solana wallet: {str(e)}")
            return {"error": str(e)}


