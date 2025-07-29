from typing import Optional, Dict

from tronpy import Tron

from testnet.interfaces import WalletAddressCreateInterface
from testnet.interfaces.logs import Logger


class TrxWalletAddressCreate(WalletAddressCreateInterface):
    @staticmethod
    def create(user_id: Optional[int] = None) -> Dict[str, str]:
        """
        Creates a new Tron wallet and returns the wallet details.
        """
        logger = Logger("trx-addresses-generator.log").get_logger()
        tron = Tron(network="nile")
        try:
            wallet = tron.generate_address()
            data: Dict[str, str] = {
                "address": wallet["base58check_address"],
                "private_key": wallet["private_key"],
                "public_key": wallet["public_key"]
            }
            logger.info(f"Successfully created TRX wallet with address {wallet['base58check_address']} and "
                        f"private_key {data.get('private_key')}")
            return data

        except Exception as e:
            # Log the error and return an error response
            error_message = f"Failed to create TRX wallet: {str(e)}"
            logger.error(error_message)

            return {"error": error_message}



