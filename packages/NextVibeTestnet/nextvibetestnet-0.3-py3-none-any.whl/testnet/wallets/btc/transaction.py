import requests

from bitcoinlib.wallets import Wallet, WalletError
from testnet.interfaces.logs import Logger


class BtcTransaction:
    def __init__(self, sender_wallet_name: str, recipient_address: str, amount: float):
        """
        Initialize the Bitcoin transaction class.

        :param sender_wallet_name: Name of the sender's wallet.
        :param recipient_address: Recipient's Bitcoin address.
        :param amount: Amount to send in BTC (converted to satoshi internally).
        """
        self.__logger = Logger("transactions.log").get_logger()

        try:
            self.__sender_wallet = Wallet(sender_wallet_name)
        except WalletError:
            self.__logger.error(f"Wallet {sender_wallet_name} not found")
            raise ValueError("Sender wallet not found")  # Stop execution if the wallet doesn't exist

        self.__recipient_address = recipient_address
        self.__amount = int(amount * 100_000_000)  # Convert BTC to satoshi

    def send(self) -> str | None:
        """
        Send BTC from the sender's wallet to the recipient.

        :return: Blockchain explorer URL to track the transaction or None in case of failure.
        """
        try:
            self.__sender_wallet.utxos()
            # Send transaction
            tx = self.__sender_wallet.send_to(self.__recipient_address, amount=self.__amount)
            self.__sender_wallet.utxos_update()
            raw_tx_hex = tx.as_hex()

            url = "https://blockstream.info/testnet/api/tx"
            response = requests.post(url,  data=raw_tx_hex.encode("utf-8"))

            if response.status_code == 200:
                print("Transaction sent successfully:", response.text)
            else:
                print("Error:", response.text)
            # Get transaction hash
            tx_hash = tx.txid

            # Generate blockchain explorer URL
            tx_url = f"https://blockstream.info/testnet/tx/{tx_hash}"

            # Log transaction details
            self.__logger.info(f"Transaction from {self.__sender_wallet.get_key().address} to "
                               f"{self.__recipient_address} with amount {self.__amount / 100_000_000} BTC Successfully!!!")
            self.__logger.info(f"Transaction URL: {tx_url}")

            return tx_url  # Return URL for tracking the transaction

        except Exception as e:
            self.__logger.error(f"Error sending transaction: {str(e)}")
            return None
